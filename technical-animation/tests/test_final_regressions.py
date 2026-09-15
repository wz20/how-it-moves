"""Mutation/regression boundaries; approval data below is explicitly test-only."""
import copy, hashlib, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import topic_model as m, topic_output as out, mechanism_core as mc, academic_delivery as ad
from test_mechanism import mechanism_fixture
from test_release_gates import course_fixture

class FinalRegressions(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.d=mechanism_fixture(self.root)
 def tearDown(self):self.tmp.cleanup()
 def test_bad_json_shapes_have_structured_errors(self):
  mutations=[
   lambda d:d['mechanism']['variables']['stored']['binding'].update(channel=[]),
   lambda d:d['mechanism']['events'][0]['effects'][0].update(ref=[]),
   lambda d:d['performance']['actions'][0].update(kind=[]),
   lambda d:d.update(performance=[]),
   lambda d:d['performance']['actions'][0].update(after='save'),
   lambda d:d['mechanism']['variables']['stored'].update(values=['token',1]),
  ]
  for change in mutations:
   with self.subTest(change=change):
    d=copy.deepcopy(self.d);change(d)
    with self.assertRaises(m.Problem):mc.resolve(d)
 def transfer(self,state=True):
  d=copy.deepcopy(self.d)
  a=dict(id='deliver',kind='transfer',object='token',target='vessel',duration=3,caption='Receive',consequence='Record token after contact')
  if state:a['state']='full'
  d['performance']['actions']=[a]
  d['mechanism']['variables']={
   'status':dict(type='enum',values=['empty','full'],initial='empty',binding=dict(rig='vessel',channel='state')),
   'received':dict(type='set',values=['token'],initial=[],binding=dict(rig='vessel',channel='receipts'))}
  d['mechanism']['events']=[dict(id='receive',action='deliver',effects=[dict(ref='status',op='set',value='full'),dict(ref='received',op='add',value='token')],observation='The receiver switches state after contact and keeps receipt.')]
  return d
 def test_transfer_receipt_is_persistent_not_pulse(self):
  from perform_core import semantic_state
  d=self.transfer();sc=mc.resolve(d);ev=sc['mechanism_trace'][0]
  self.assertEqual(semantic_state(sc,ev['commit']-1)['receipts'],{})
  self.assertEqual(semantic_state(sc,359)['receipts'],{'vessel':['token']})
  self.assertEqual(semantic_state(sc,359)['states']['vessel'],'full')
 def test_pulse_cannot_claim_receipt(self):
  with self.assertRaisesRegex(m.Problem,'E_MECHANISM_DIVERGENCE'):mc.resolve(self.transfer(False))
 def test_source_predicate_unknown_in_false_branch_still_fails(self):
  d=self.d;d['mechanism']['variables']['choose']={'type':'bool','initial':False}
  d['mechanism']['events'][1]['when']=[dict(ref='choose',op='eq',value=True)]
  d['mechanism']['events'][1]['requires']=[dict(ref='unknown',op='eq',value=3)]
  with self.assertRaisesRegex(m.Problem,'E_VARIABLE'):mc.plan(d)
 def test_equation_object_shape_is_checked(self):
  d=copy.deepcopy(self.d);d['profile']='academic';d['course']=course_fixture();d['course']['equations']=['formula']
  with self.assertRaises(m.Problem):ad.validate_course(d)
 def test_equation_domain_and_units_cannot_be_empty(self):
  d=copy.deepcopy(self.d);d['profile']='academic';d['course']=course_fixture();d['course']['equations']=[dict(expression='x=y',domain='',unit_check='',symbols={'x':'m','y':'m'},source_ids=['S1'])]
  with self.assertRaises(m.Problem):ad.validate_course(d,final=True)
 def test_pending_claim_cannot_export_academic(self):
  d=copy.deepcopy(self.d);d['profile']='academic';d['course']=course_fixture();d['course']['claims'][0]['status']='pending'
  with self.assertRaisesRegex(m.Problem,'E_CLAIM_REVIEW'):ad.validate_course(d,final=True)
 def test_pending_teacher_is_not_visual_approval(self):
  d=copy.deepcopy(self.d);d['profile']='academic';d['course']=course_fixture()
  p=self.root/'teacher.json';p.write_text(json.dumps(ad.teacher_template('f','h')))
  with self.assertRaisesRegex(m.Problem,'E_TEACHER_REVIEW'):ad.check_teacher(d,'f',p,'h')
 def test_export_bytes_must_match_delivery(self):
  folder=self.root/'export';folder.mkdir();(folder/'animation.html').write_text('test placeholder')
  (folder/'delivery.json').write_text(json.dumps({'files':{'animation.html':{'sha256':'changed','bytes':16}}}))
  with self.assertRaisesRegex(m.Problem,'E_HANDOFF'):ad.verified_delivery(folder)
 def test_teacher_signoff_binds_specific_delivery(self):
  d=copy.deepcopy(self.d);d['profile']='academic';d['course']=course_fixture()
  r=ad.teacher_template('f','old');r.update(verdict='approved',reviewer='Test reviewer',role='instructor',request_reference='Synthetic unit test; not actual approval')
  r['findings']={k:'Synthetic test observation' for k in r['findings']}
  p=self.root/'teacher.json';p.write_text(json.dumps(r))
  with self.assertRaisesRegex(m.Problem,'E_TEACHER_REVIEW'):ad.check_teacher(d,'f',p,'new')
 def test_handoff_packages_only_media_and_notes_after_separate_approval(self):
  from unittest.mock import patch
  d=copy.deepcopy(self.d);d['profile']='academic';d['course']=course_fixture()
  delivery=self.root/'delivery';delivery.mkdir();media=delivery/'animation.html';media.write_text('<html>UNIT TEST PLACEHOLDER ONLY</html>')
  (delivery/'private-client-notes.txt').write_text('Never include this file')
  manifest={'source_fingerprint':out.fingerprint(d,self.root),'files':{'animation.html':{'sha256':m.sha(media),'bytes':media.stat().st_size}}}
  (delivery/'delivery.json').write_text(json.dumps(manifest))
  teacher=ad.prepare_handoff(d,self.root,delivery,self.root/'teacher.json')
  r=json.loads(teacher.read_text());self.assertEqual(r['verdict'],'pending')
  r.update(verdict='approved',reviewer='TEST HARNESS',role='instructor',request_reference='Unit-test record, NOT an actual instructor sign-off')
  r['findings']={k:'Synthetic packaging test, not subject validation' for k in r['findings']};teacher.write_text(json.dumps(r))
  # Isolate packaging from provenance: the real synthetic-asset rejection is tested separately.
  with patch.object(ad,'assert_publishable_assets'):
   result=ad.handoff(d,self.root,delivery,teacher,self.root/'handoff')
  self.assertFalse((self.root/'handoff/private-client-notes.txt').exists())
  self.assertEqual(set(p.name for p in (self.root/'handoff').iterdir()),{'animation.html','教学说明.md','handoff.json'})
  self.assertEqual(result['status'],'subject-reviewed-handoff');self.assertFalse(result['public_publish'])
 def test_modified_media_invalidates_subject_handoff(self):
  delivery=self.root/'delivery';delivery.mkdir();media=delivery/'video.mp4';media.write_bytes(b'not-a-video-test-only')
  (delivery/'delivery.json').write_text(json.dumps({'files':{'video.mp4':{'sha256':m.sha(media),'bytes':media.stat().st_size}}}))
  media.write_bytes(b'changed')
  with self.assertRaisesRegex(m.Problem,'E_HANDOFF'):ad.verified_delivery(delivery)
 def test_raster_options_are_shared_by_capture_and_export(self):
  # The browser integration exercises fractional-position geometry in sparse and dense captures.
  # This pins the CPU/full-raster defaults after a Chromium tile-cache regression was reproduced.
  import inspect
  code=inspect.getsource(out.browser)
  self.assertIn('--disable-gpu',code);self.assertIn('--disable-partial-raster',code)

if __name__=='__main__':unittest.main()
