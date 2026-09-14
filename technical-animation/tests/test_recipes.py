"""Recipe-mode tests. Content fixtures predate the implementation."""
import copy, importlib.util, json, sys, unittest
from pathlib import Path
S=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(S/'scripts'))
try:
 import recipe_core as core
except ModuleNotFoundError:
 core=None

class RecipeTests(unittest.TestCase):
 def setUp(self):
  self.assertIsNotNone(core,'Recipe compiler is missing: users still have to write scene code')
 def spec(self,name='feedback-retry'):
  return json.loads((S/'recipes'/f'{name}.json').read_text())
 def codes(self,s):return {e['code'] for e in core.validate_spec(s)}
 def test_all_three_compile(self):
  for r in ('feedback-retry','retrieval-evidence','cache-aside'):
   with self.subTest(recipe=r):
    s=self.spec(r);self.assertEqual(core.validate_spec(s),[])
    p=core.compile_recipe(s);self.assertTrue(p['ready_for_render']);self.assertEqual(p['recipe'],r)
 def test_unknown_recipe(self):
  s=self.spec();s['recipe']='TCP';self.assertIn('E_RECIPE',self.codes(s))
 def test_unknown_key(self):
  s=self.spec();s['x']=34;self.assertIn('E_UNKNOWN',self.codes(s))
 def test_no_freeform_timing(self):
  s=self.spec();s['content']['start']=0;self.assertIn('E_UNKNOWN',self.codes(s))
 def test_bool_is_not_duration(self):
  s=self.spec();s['duration']=True;self.assertIn('E_NUMBER',self.codes(s))
 def test_nan_is_not_duration(self):
  s=self.spec();s['duration']=float('nan');self.assertIn('E_NUMBER',self.codes(s))
 def test_minimum_duration(self):
  s=self.spec();s['duration']=3;self.assertIn('E_DURATION',self.codes(s))
 def test_long_duration_rejected(self):
  s=self.spec();s['duration']=180;self.assertIn('E_DURATION',self.codes(s))
 def test_only_supported_aspect(self):
  s=self.spec();s['aspect']='9:16';self.assertIn('E_ASPECT',self.codes(s))
 def test_audio_not_silently_dropped(self):
  s=self.spec();s['audio']='voice';self.assertIn('E_AUDIO',self.codes(s))
 def test_unknown_style_rejected(self):
  s=self.spec();s['style']='photo';self.assertIn('E_STYLE',self.codes(s))
 def test_overlong_title(self):
  s=self.spec();s['title']='字'*70;self.assertIn('E_TEXT',self.codes(s))
 def test_same_code_not_a_patch(self):
  s=self.spec();s['content']['after']=s['content']['before'];self.assertIn('E_NO_CHANGE',self.codes(s))
 def test_failure_success_distinct(self):
  s=self.spec();s['content']['success']=s['content']['failure'];self.assertIn('E_AMBIGUOUS',self.codes(s))
 def test_duplicate_evidence_id(self):
  s=self.spec('retrieval-evidence');s['content']['documents'][1]['id']='D1';self.assertIn('E_DUPLICATE',self.codes(s))
 def test_missing_selected_evidence(self):
  s=self.spec('retrieval-evidence')
  for d in s['content']['documents']:d['selected']=False
  self.assertIn('E_EVIDENCE',self.codes(s))
 def test_citation_must_have_been_retrieved(self):
  s=self.spec('retrieval-evidence');s['content']['citations']=['D2'];self.assertIn('E_CITATION',self.codes(s))
 def test_selected_must_be_boolean(self):
  s=self.spec('retrieval-evidence');s['content']['documents'][0]['selected']='yes';self.assertIn('E_TYPE',self.codes(s))
 def test_bad_nested_type(self):
  s=self.spec('retrieval-evidence');s['content']['documents']=None;self.assertIn('E_TYPE',self.codes(s))
 def test_no_control_characters(self):
  s=self.spec();s['title']='first\nsecond';self.assertIn('E_TEXT',self.codes(s))
 def test_contract_roundtrip_deterministic(self):
  s=self.spec();self.assertEqual(core.compile_recipe(s),core.compile_recipe(copy.deepcopy(s)))
 def test_no_side_effect_before_arrival(self):
  p=core.compile_recipe(self.spec());e=next(e for e in p['events'] if e['id']=='fail')
  self.assertFalse(core.state_at_frame(p,e['end_frame']-1).get('feedback_received',False))
  self.assertTrue(core.state_at_frame(p,e['end_frame']).get('feedback_received'))
 def test_retry_and_stop(self):
  p=core.compile_recipe(self.spec());st=core.state_at_frame(p,p['fps']*p['duration']-1)
  self.assertTrue(st['stopped']);self.assertEqual(st['test_runs'],2);self.assertTrue(st['code_changed'])
 def test_cache_only_one_database_read(self):
  p=core.compile_recipe(self.spec('cache-aside'));st=core.state_at_frame(p,p['fps']*p['duration']-1)
  self.assertEqual(st['db_reads'],1);self.assertTrue(st['cache_filled']);self.assertEqual(st['responses'],2)
 def test_rag_evidence_before_generation(self):
  p=core.compile_recipe(self.spec('retrieval-evidence'));events={e['id']:e for e in p['events']}
  self.assertGreaterEqual(events['generate']['start_frame'],events['evidence']['end_frame'])
  self.assertFalse(core.state_at_frame(p,events['evidence']['end_frame']-1).get('context_ready',False))
 def test_bounds_and_holds(self):
  for r in ('feedback-retry','retrieval-evidence','cache-aside'):
   for fps in (30,60):
    s=self.spec(r);s['fps']=fps;p=core.compile_recipe(s);n=int(p['duration']*fps)
    self.assertEqual(p['events'][-1]['end_frame'],n)
    self.assertGreaterEqual(p['events'][-1]['end_frame']-p['events'][-1]['start_frame'],1.5*fps)
    for e in p['events']:
     self.assertLess(e['start_frame'],e['end_frame']);self.assertLessEqual(e['end_frame'],n)
    self.assertEqual(core.validate_compiled(p),[])
 def test_contract_tampering_rejected(self):
  p=core.compile_recipe(self.spec());p['events'][1]['start_frame']=0
  self.assertIn('E_CONTRACT',{e['code'] for e in core.validate_compiled(p)})
 def test_errors_have_field_and_hint(self):
  s=self.spec();s['content']['before']=None
  for e in core.validate_spec(s):
   self.assertTrue(e['field']);self.assertTrue(e['hint']);self.assertTrue(e['message'])

if __name__=='__main__':unittest.main()
