"""Public export/academic handoff gates; never auto-approve real client work."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import topic_model as m, topic_output as out
import visual_evidence as ve
import academic_delivery as ad
from test_mechanism import mechanism_fixture
from test_topic_outputs import fixture

def course_fixture():
 c=ad.blank_course();c.update(audience='Synthetic test audience',objectives=['Track source and copy'],scope='single-slot teaching example',
 assumptions=['No real database is executed'],assessment=['Which object remains?'],sources=[dict(id='S1',title='Test reference',reference='fixture-only',kind='user-material')],
 claims=[dict(id='C1',statement='The fixture preserves the original',locator='Fixture line 1',source_ids=['S1'],status='verified',checked_by='synthetic test')])
 return c

class Gates(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name);self.d=mechanism_fixture(self.root)
 def tearDown(self):self.t.cleanup()
 def test_integrated_typed_scene_validate(self):m.validate(self.d,self.root)
 def test_uncertified_old_scene_cannot_render_final(self):
  d=fixture(self.root)
  with self.assertRaisesRegex(m.Problem,'E_MECHANISM_REQUIRED'):out.export(d,self.root,self.root/'out',['html'],self.root/'pretend-review.json')
 def test_probe_frames_capture_effect_boundary(self):
  sc=m.resolved(self.d);p=ve.probes(sc)
  self.assertEqual(len(p),2)
  self.assertIn(sc['compiled_actions'][0]['commit']-1,p[0]['frames'])
  self.assertIn(sc['compiled_actions'][0]['commit'],p[0]['frames'])
 def test_witnesses_come_from_actual_layer_properties(self):
  sc=m.resolved(self.d);p=ve.probes(sc)
  w=p[0]['witnesses'][0];self.assertEqual(w['asset'],'full');self.assertEqual(w['layer'],'vessel-body')
 def test_hiding_explanations_not_hiding_labels(self):
  self.d['layers'].append(dict(id='title',type='text',slot='title',text='Explanation',purpose='narration'))
  self.d['layers'].append(dict(id='tag',type='text',slot='top',text='M1',purpose='label'))
  h=out.html(self.d,self.root,True);self.assertIn('setReviewView',h);self.assertIn('data-purpose="label"',h)
 def test_missing_event_review_not_approved_by_paragraphs(self):
  sc=m.resolved(self.d)
  with self.assertRaisesRegex(m.Problem,'E_EVENT_REVIEW'):ve.check_records({'events':[]},sc,self.root)
 def test_quality_has_three_separate_results(self):
  r=ve.pending(m.resolved(self.d));self.assertEqual(r['layers'],{'technical':'pending','event':'pending','visual':'pending'})
 def test_synthetic_receipt_blocks_customer_handoff(self):
  with self.assertRaisesRegex(m.Problem,'E_TEST_ASSET'):ad.assert_publishable_assets(self.d)
 def test_course_brief_needed_for_academic(self):
  self.d['profile']='academic'
  with self.assertRaisesRegex(m.Problem,'E_COURSE'):ad.validate_course(self.d)
 def test_course_not_required_for_internal_general(self):ad.validate_course(self.d)
 def test_instructor_approval_is_not_filled_by_init(self):
  c=ad.blank_course();self.assertEqual(c['teacher_review']['verdict'],'pending')
 def test_source_claim_without_locator_fails(self):
  self.d['profile']='academic';self.d['course']=course_fixture()
  self.d['course']['claims'][0]['locator']=''
  with self.assertRaises(m.Problem):ad.validate_course(self.d)
 def test_source_reference_exists(self):
  self.d['profile']='academic';self.d['course']=course_fixture()
  self.d['course']['claims'][0]['source_ids']=['missing']
  with self.assertRaisesRegex(m.Problem,'E_CLAIM_SOURCE'):ad.validate_course(self.d)
 def test_teacher_record_tied_to_fingerprint(self):
  self.d['profile']='academic';self.d['course']=course_fixture()
  with self.assertRaisesRegex(m.Problem,'E_TEACHER_REVIEW'):ad.check_teacher(self.d,'fingerprint','abc')
 def test_permission_to_upload_customer_materials_not_assumed(self):
  c=ad.blank_course();self.assertFalse(c['privacy']['public_publish']);self.assertFalse(c['privacy']['third_party_upload'])
if __name__=='__main__':unittest.main()
