"""Regression contract for the content-only editorial director (no network/model)."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/direct.py'

class DirectorTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CLI.is_file(), 'missing content-only directing CLI')
        sys.path.insert(0, str(CLI.parent))
        spec = importlib.util.spec_from_file_location('tested_direct', CLI)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.sample = json.loads((ROOT / 'directing/partition-search.json').read_text())

    def rejected(self, spec, code):
        with self.assertRaises(self.mod.ContractError) as caught:
            self.mod.normalize(spec)
        self.assertEqual(caught.exception.code, code)
        self.assertTrue(caught.exception.field)
        self.assertTrue(caught.exception.hint)

    def test_sample_compiles_to_one_contract(self):
        p = self.mod.compile_project(self.mod.normalize(self.sample))
        self.assertEqual(len(p['direction']['shots']), 6)
        self.assertEqual(p['fps'] * p['duration'], 1440)
        self.assertEqual(p['direction']['query_id'], 'Q1')
        self.assertTrue(p['ready_for_render'])

    def test_unknown_field_is_not_ignored(self):
        self.sample['camera_x'] = 400
        self.rejected(self.sample, 'E_FIELD')

    def test_wrong_pattern_is_not_relabelled(self):
        self.sample['pattern'] = 'TCP'
        self.rejected(self.sample, 'E_PATTERN')

    def test_unknown_selection_rejected(self):
        self.sample['selected_group'] = 'missing'
        self.rejected(self.sample, 'E_REFERENCE')

    def test_duplicate_candidate_identity_rejected(self):
        self.sample['segments'][1]['candidates'][0]['id'] = self.sample['segments'][0]['candidates'][0]['id']
        self.rejected(self.sample, 'E_ID')

    def test_bool_nan_and_out_of_range_scores_rejected(self):
        for bad in (True, float('nan'), 1.5, -0.1, 'high'):
            s = copy.deepcopy(self.sample)
            s['segments'][0]['candidates'][0]['score'] = bad
            self.rejected(s, 'E_SCORE')

    def test_long_text_is_not_squeezed(self):
        self.sample['title'] = '长' * 40
        self.rejected(self.sample, 'E_TEXT')

    def test_wrong_format_is_not_silently_changed(self):
        self.sample['aspect'] = '9:16'
        self.rejected(self.sample, 'E_FORMAT')

    def test_audio_is_not_silently_removed(self):
        self.sample['audio'] = 'voice.mp3'
        self.rejected(self.sample, 'E_FORMAT')

    def test_sort_waits_for_every_return(self):
        p = self.mod.compile_project(self.mod.normalize(self.sample))
        events = {e['id']: e for e in p['events']}
        for dep in events['rank']['after']:
            self.assertGreaterEqual(events['rank']['start'], events[dep]['end'])
        self.assertGreaterEqual(p['duration'] - events['deliver']['end'], 2)
        for e in p['events']:
            self.assertEqual(round(e['start'] * p['fps']), e['start_frame'])
            self.assertEqual(round(e['end'] * p['fps']), e['end_frame'])

    def test_rank_uses_content_scores_and_stable_ties(self):
        p = self.mod.compile_project(self.mod.normalize(self.sample))
        rows = p['direction']['ranked']
        self.assertEqual([r['score'] for r in rows], sorted([r['score'] for r in rows], reverse=True))
        self.assertEqual(rows[0]['id'], 'img24')

    def test_duration_and_fps_are_validated(self):
        for field, value in [('duration', 10), ('fps', 24), ('fps', True)]:
            s = copy.deepcopy(self.sample); s[field] = value
            self.rejected(s, 'E_FORMAT')

    def test_build_is_portable_and_content_does_not_rewrite_scene(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'a', Path(d) / 'b'
            self.mod.build(self.sample, a)
            self.sample['query'] = '查找相似设计稿'
            self.mod.build(self.sample, b)
            self.assertEqual((a / 'scene.mjs').read_bytes(), (b / 'scene.mjs').read_bytes())
            self.assertNotEqual((a / 'project.json').read_bytes(), (b / 'project.json').read_bytes())
            self.assertIn('data:text/javascript;base64,', (a / 'preview.html').read_text())
            self.mod.check_build(a)

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'a'; self.mod.build(self.sample, out)
            old = (out / 'preview.html').read_bytes()
            with self.assertRaises(self.mod.ContractError) as c:
                self.mod.build(self.sample, out)
            self.assertEqual(c.exception.code, 'E_EXISTS')
            self.assertEqual((out / 'preview.html').read_bytes(), old)

    def test_tampering_contract_or_runtime_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'a'; self.mod.build(self.sample, out)
            p = json.loads((out / 'project.json').read_text()); p['events'][0]['end'] = 100
            (out / 'project.json').write_text(json.dumps(p))
            with self.assertRaises(self.mod.ContractError) as c:
                self.mod.check_build(out)
            self.assertEqual(c.exception.code, 'E_INTEGRITY')

    def test_display_ids_and_query_respect_pixel_budget(self):
        self.sample['segments'][0]['candidates'][0]['id'] = 'abcdefghijkl'
        self.rejected(self.sample, 'E_ID')
        self.sample = json.loads((ROOT / 'directing/partition-search.json').read_text())
        self.sample['query'] = '长' * 16
        self.rejected(self.sample, 'E_TEXT')

    def test_incomplete_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'a'; self.mod.build(self.sample, out)
            m = json.loads((out / 'build-files.json').read_text())
            del m['runtime/partition-search.mjs']
            (out / 'build-files.json').write_text(json.dumps(m))
            with self.assertRaises(self.mod.ContractError) as c:
                self.mod.check_build(out)
            self.assertEqual(c.exception.code, 'E_INTEGRITY')

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.json'; p.write_text('{"title":"a","title":"b"}')
            r = subprocess.run([sys.executable, str(CLI), 'check', str(p)], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(json.loads(r.stdout)['errors'][0]['code'], 'E_DUPLICATE')

    def test_nested_script_end_tag_remains_text(self):
        with tempfile.TemporaryDirectory() as d:
            self.sample['title'] = '</script><p>hi</p>'
            self.mod.build(self.sample, Path(d) / 'out')
            self.assertNotIn('</script><p>hi</p>', (Path(d) / 'out/preview.html').read_text())

    def test_cli_machine_readable_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.json'; p.write_text('{')
            r = subprocess.run([sys.executable, str(CLI), 'check', str(p)], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            error = json.loads(r.stdout)['errors'][0]
            self.assertEqual(error['code'], 'E_INPUT')
            self.assertTrue(error['hint'])

if __name__ == '__main__':
    unittest.main()
