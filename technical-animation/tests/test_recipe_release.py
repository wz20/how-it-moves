"""Release usability regressions. No browser, network, or model API required."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parent
CLI = SKILL / 'scripts/recipe.py'


def run_cli(*args):
    return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                          capture_output=True, text=True)


class RecipeReleaseTests(unittest.TestCase):
    def test_browser_checker_has_portable_help(self):
        path = SKILL / 'tests/check_recipe_browser.py'
        self.assertTrue(path.is_file(), 'README browser checker is missing')
        result = subprocess.run([sys.executable, str(path), '--help'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--out', result.stdout)
        self.assertIn('--browser', result.stdout)

    def test_three_init_outputs_are_valid_without_agent_code(self):
        with tempfile.TemporaryDirectory() as folder:
            for recipe in ('feedback-retry', 'retrieval-evidence', 'cache-aside'):
                path = Path(folder) / (recipe + '.json')
                result = run_cli('init', '--recipe', recipe, '--out', path)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = run_cli('check', path)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_content_changes_do_not_require_scene_edits(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            spec = json.loads((SKILL / 'recipes/cache-aside.json').read_text())
            source = folder / 'config.json'
            source.write_text(json.dumps(spec))
            result = run_cli('build', source, '--out', folder / 'a')
            self.assertEqual(result.returncode, 0, result.stderr)
            spec['content']['key'] = 'order:7'
            spec['content']['value'] = 'PAID'
            source.write_text(json.dumps(spec))
            result = run_cli('build', source, '--out', folder / 'b')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((folder/'a/scene.mjs').read_bytes(), (folder/'b/scene.mjs').read_bytes())
            self.assertNotEqual((folder/'a/project.json').read_bytes(), (folder/'b/project.json').read_bytes())
            self.assertEqual(run_cli('check', folder/'b').returncode, 0)

    def test_malformed_manifest_returns_structured_error(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / 'movie'
            self.assertEqual(run_cli('build', SKILL/'recipes/cache-aside.json', '--out', out).returncode, 0)
            (out/'build-files.json').write_text('[]')
            result = run_cli('check', out)
            self.assertNotEqual(result.returncode, 0)
            errors = json.loads(result.stderr)['errors']
            self.assertTrue(any(e['code'] == 'E_BUILD' for e in errors))

    def test_duplicate_json_key_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/'config.json'
            source.write_text('{"recipe":"cache-aside","recipe":"feedback-retry"}')
            result = run_cli('check', source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('E_DUPLICATE', result.stderr)

    def test_readme_json_examples_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ('README.md', 'README.en.md'):
                blocks = re.findall(r'```json\n(.*?)\n```', (ROOT/name).read_text(), flags=re.S)
                self.assertTrue(blocks, name)
                for i, block in enumerate(blocks):
                    source = Path(folder)/f'{name}-{i}.json'
                    source.write_text(block)
                    result = run_cli('check', source)
                    self.assertEqual(result.returncode, 0, (name, result.stderr))

    def test_script_end_tag_is_escaped_in_standalone_html(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            spec = json.loads((SKILL/'recipes/cache-aside.json').read_text())
            spec['title'] = '</script><p>not code</p>'
            source = folder/'config.json'
            source.write_text(json.dumps(spec))
            result = run_cli('build', source, '--out', folder/'out')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn('</script><p>not code</p>', (folder/'out/preview.html').read_text())

if __name__ == '__main__':
    unittest.main()
