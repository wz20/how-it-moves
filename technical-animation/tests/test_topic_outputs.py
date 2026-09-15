"""Synthetic fixture tests: these images are not AI-generated showcase material."""
import copy, importlib.util, json, sys, tempfile, unittest
from pathlib import Path
from PIL import Image, ImageDraw
SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import topic_model as m
import topic_output as out


def fixture(root):
    data = m.blank('topic-test', ['html', 'video', 'svg'])
    data['duration'] = 2
    data['fps'] = 30
    data['poster_frame'] = 45
    data['style'] = 'Original tactile editorial illustration; warm light, sculpted silhouettes.'
    data['concept'] = {
        'goal': 'Explain why feedback changes the next operation.',
        'candidates': [
            {'world': 'ceramic workshop', 'reason': 'A test changes the clay shape.', 'risk': 'Not physical model training.'},
            {'world': 'sailboat navigation', 'reason': 'A sounding changes the next heading.', 'risk': 'Not guaranteed convergence.'},
            {'world': 'theatre rehearsal', 'reason': 'A review changes the next take.', 'risk': 'Not learning model weights.'}],
        'selected': 0,
        'entities': [
            {'id': 'source', 'meaning': 'input', 'subject': 'split ceramic vessel', 'operation': 'inspect', 'consequence': 'defect becomes visible', 'invariant': 'the vessel remains the same'},
            {'id': 'tool', 'meaning': 'test', 'subject': 'glazed inspection lens', 'operation': 'verify', 'consequence': 'surface defect found', 'invariant': 'test is not the repair'}],
        'avoid': ['robot', 'file cabinet', 'text cards']}
    data['assets'] = []
    for i, name in enumerate(['source', 'tool']):
        p = root / (name + '.png')
        im = Image.new('RGBA', (320, 320), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse((10, 10, 310, 310), fill=(40+i*90, 90, 130, 255))
        d.polygon([(55, 230), (150, 40), (265, 230)], fill=(240, 210, 95, 255))
        d.text((100, 150), 'TEST ONLY', fill='black')
        im.save(p)
        data['assets'].append({'id':name, 'path':p.name, 'sha256':m.sha(p), 'role':'subject',
            'generation':{'project_id':data['project_id'], 'tool':'synthetic-unit-test', 'model':'NOT A MODEL',
            'run_reference':'test-fixture-only', 'prompt':'Synthetic image for the '+name+' fixture; not a production receipt.'}})
    data['shots'] = [{'id':'one', 'start':0, 'end':60, 'caption':'Inspect, then act.',
        'action':'inspect', 'change':'the test identifies a defect', 'asset_ids':['source','tool'], 'critical_frames':[20,40]}]
    data['layers'] = [
        {'id':'source-art', 'asset':'source', 'slot':'left', 'start':0,'end':60,
         'keys':[{'frame':0,'slot':'left'}, {'frame':40,'slot':'center'}]},
        {'id':'tool-art', 'asset':'tool', 'slot':'right','start':0,'end':60},
        {'id':'label','type':'text','text':'<& " Editable','slot':'title','size':38,'start':0,'end':60}]
    return data


class TopicTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.d = fixture(self.root)
    def tearDown(self): self.tmp.cleanup()
    def valid(self, d=None): return m.validate(d or self.d, self.root)
    def test_valid(self): self.valid()
    def test_three_explicit_outputs(self): self.assertEqual(m.formats(['html','mp4','svg']), ['html','video','svg'])
    def test_unknown_output_rejected(self):
        with self.assertRaises(m.Problem): m.formats(['pdf'])
    def test_empty_output_rejected(self):
        with self.assertRaises(m.Problem): m.formats([])
    def test_init_has_no_canned_art(self):
        p = m.blank('Redis', ['svg']); self.assertEqual(p['assets'], []); self.assertEqual(p['layers'], [])
    def test_same_world_three_times_rejected(self):
        self.d['concept']['candidates'] *= 0
        self.d['concept']['candidates'] = [{'world':'robot','reason':'x','risk':'x'}] * 3
        with self.assertRaisesRegex(m.Problem, 'E_VARIETY'): self.valid()
    def test_foreign_project_art_rejected_by_default(self):
        self.d['assets'][0]['generation']['project_id']='other-project'
        with self.assertRaisesRegex(m.Problem, 'E_REUSE'): self.valid()
    def test_explicit_reuse_needs_specific_consent(self):
        self.d['assets'][0]['generation']['project_id']='other-project'
        self.d['reuse_consent']={'asset_ids':['source'], 'request_reference':'user explicitly requests original mascot'}
        self.valid()
    def test_another_project_same_bytes_history_rejected(self):
        self.d['history']=[{'project_id':'previous','world':'other','asset_hashes':[self.d['assets'][0]['sha256']]}]
        with self.assertRaisesRegex(m.Problem,'E_REUSE'): self.valid()
    def test_empty_assets_blocks(self):
        self.d['assets']=[]
        with self.assertRaisesRegex(m.Problem,'ASSET_BLOCKED'): self.valid()
    def test_missing_asset_blocks(self):
        self.d['assets'][0]['path']='absent.png'
        with self.assertRaises(m.Problem): self.valid()
    def test_path_escape_blocks(self):
        self.d['assets'][0]['path']='../outside.png'
        with self.assertRaisesRegex(m.Problem,'E_PATH'): self.valid()
    def test_asset_hash_mismatch(self):
        self.d['assets'][0]['sha256']='0'*64
        with self.assertRaisesRegex(m.Problem,'E_HASH'): self.valid()
    def test_background_does_not_satisfy_subject(self):
        for a in self.d['assets']: a['role']='background'
        with self.assertRaisesRegex(m.Problem,'E_ART'): self.valid()
    def test_asset_not_used_rejected(self):
        self.d['layers']=[self.d['layers'][-1]]
        with self.assertRaisesRegex(m.Problem,'E_ART'): self.valid()
    def test_tiny_art_rejected(self):
        for l in self.d['layers'][:2]: l['scale']=.1; l['keys']=[]
        with self.assertRaisesRegex(m.Problem,'E_ART'): self.valid()
    def test_timeline_gap(self):
        self.d['shots'][0]['end']=59
        with self.assertRaisesRegex(m.Problem,'E_TIMELINE'): self.valid()
    def test_caption_only_animation_rejected(self):
        self.d['shots'][0]['action']='fade'
        with self.assertRaisesRegex(m.Problem,'E_ACTION'): self.valid()
    def test_state_is_seekable(self):
        l=self.d['layers'][0]
        a=m.layer_state(l,20,self.d); m.layer_state(l,50,self.d)
        self.assertEqual(a,m.layer_state(l,20,self.d))
    def test_svg_contains_separate_editable_layers(self):
        s=out.svg(self.d,self.root,45)
        self.assertIn('<text',s); self.assertEqual(s.count('<image '),2)
        self.assertIn('embedded-raster',s); self.assertIn('data:image/png;base64',s)
        self.assertIn('&lt;&amp;',s); self.assertNotIn('<foreignObject',s)
    def test_svg_no_player_or_external_fonts(self):
        s=out.svg(self.d,self.root,45)
        self.assertNotIn('<script',s); self.assertNotIn('@font-face',s)
    def test_html_self_contained(self):
        h=out.html(self.d,self.root)
        self.assertIn('renderFrame',h); self.assertIn('data:image/png;base64',h)
        self.assertNotIn('https://',h)
    def test_history_same_world_requires_new_design(self):
        self.d['history']=[{'project_id':'prior','world':'ceramic workshop','asset_hashes':[]}]
        with self.assertRaisesRegex(m.Problem,'E_VARIETY'): self.valid()
    def test_svg_only_no_motion_requirement(self):
        self.d['formats']=['svg']; self.d['layers'][0]['keys']=[]; self.valid()
    def test_reading_hold_static_animation_rejected(self):
        self.d['layers'][0]['keys']=[]
        with self.assertRaisesRegex(m.Problem,'E_MOTION'): self.valid()
    def test_unknown_scene_field(self):
        self.d['run_javascript']='alert(1)'
        with self.assertRaisesRegex(m.Problem,'E_FIELD'): self.valid()
    def test_nonfinite_track_rejected(self):
        self.d['layers'][0]['keys'][0]['scale']=float('nan')
        with self.assertRaises(m.Problem): self.valid()
    def test_no_outputs_without_review(self):
        with self.assertRaisesRegex(m.Problem,'E_REVIEW'): out.export(self.d,self.root,self.root/'out',['svg'])
        self.assertFalse((self.root/'out').exists())
    def test_prompt_brief_is_topic_specific(self):
        p=m.prompts(self.d)
        self.assertIn('split ceramic vessel',p); self.assertIn('defect becomes visible',p)
        self.assertIn('topic-test',p); self.assertNotIn('generated successfully',p)
    def test_duplicate_layers(self):
        self.d['layers'].append(copy.deepcopy(self.d['layers'][0]))
        with self.assertRaisesRegex(m.Problem,'E_ID'): self.valid()

    def test_reserved_dom_id_rejected(self):
        self.d['layers'][0]['id']='stage'
        with self.assertRaisesRegex(m.Problem,'E_ID'): self.valid()
    def test_repeated_identical_pose_not_motion(self):
        self.d['layers'][0]['keys']=[{'frame':0,'slot':'left'},{'frame':40,'slot':'left'}]
        with self.assertRaisesRegex(m.Problem,'E_MOTION'): self.valid()
    def test_final_html_omits_private_receipts(self):
        self.d['assets'][0]['generation']['run_reference']='PRIVATE_RECEIPT_REFERENCE'
        h=out.html(self.d,self.root)
        self.assertNotIn('PRIVATE_RECEIPT_REFERENCE',h)
    def test_path_transform_not_silently_ignored(self):
        self.d['layers'].append({'id':'line','type':'path','points':[[.2,.3],[.8,.3]],
            'keys':[{'frame':0,'slot':'left'},{'frame':50,'slot':'right'}]})
        with self.assertRaisesRegex(m.Problem,'E_TRACK'): self.valid()
    def test_image_bytes_renamed_still_match_history(self):
        a=self.d['assets'][0]
        (self.root/'renamed.png').write_bytes((self.root/a['path']).read_bytes());a['path']='renamed.png'
        self.d['history']=[{'project_id':'other','world':'different','asset_hashes':[a['sha256']]}]
        with self.assertRaisesRegex(m.Problem,'E_REUSE'): self.valid()
    def test_duration_requires_exact_frames(self):
        self.d['duration']=2.001
        with self.assertRaisesRegex(m.Problem,'E_TIMELINE'): self.valid()
    def test_no_script_markup_in_svg(self):
        self.d['layers'][-1]['text']='<script>alert(1)</script>'
        svg=out.svg(self.d,self.root,45)
        self.assertNotIn('<script>',svg);self.assertIn('&lt;script&gt;',svg)
    def test_empty_transparent_image_blocks(self):
        a=self.d['assets'][0];p=self.root/a['path'];Image.new('RGBA',(320,320),(0,0,0,0)).save(p);a['sha256']=m.sha(p)
        with self.assertRaisesRegex(m.Problem,'E_ART'): self.valid()
    def test_solid_image_blocks(self):
        a=self.d['assets'][0];p=self.root/a['path'];Image.new('RGB',(320,320),'white').save(p);a['sha256']=m.sha(p)
        with self.assertRaisesRegex(m.Problem,'E_ART'): self.valid()
    def test_small_resolution_blocks(self):
        a=self.d['assets'][0];p=self.root/a['path'];Image.new('RGB',(40,40),'white').save(p);a['sha256']=m.sha(p)
        with self.assertRaisesRegex(m.Problem,'E_ASSET'): self.valid()

    def test_mp4_alias_must_be_canonicalized_in_json(self):
        self.d['formats']=['mp4']
        with self.assertRaisesRegex(m.Problem,'E_FORMAT'): self.valid()
    def test_explicit_empty_export_selection_rejected(self):
        with self.assertRaisesRegex(m.Problem,'E_FORMAT'): out.export(self.d,self.root,self.root/'empty',[])

if __name__=='__main__': unittest.main()
