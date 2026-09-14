"""Art-preserving presentation tests. No model/API needed."""
import copy, importlib.util, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import illustrate
from recipe_core import compile_recipe, validate_spec
class IllustratedTests(unittest.TestCase):
 def source(self,r='feedback-retry'): return illustrate.example(r)
 def test_three_mechanisms(self):
  for r in illustrate.DURATIONS:
   s=self.source(r);self.assertEqual(validate_spec(s),[])
   p=illustrate.compile_illustrated(s)
   self.assertEqual(p['events'],compile_recipe(s)['events'])
   self.assertEqual(p['presentation'],'illustrated-studio')
 def test_events_are_input_driven(self):
  s=self.source('cache-aside');s['content']['key']='item:7';s['content']['value']='Book'
  p=illustrate.compile_illustrated(s)
  self.assertEqual(p['input_spec']['content']['value'],'Book')
 def test_hero_assets_locked(self):
  for r in illustrate.DURATIONS:
   p=illustrate.compile_illustrated(self.source(r))
   self.assertGreaterEqual(len(p['art']['assets']),3)
   self.assertEqual(p['art']['fallback'],'fail-not-diagram')
 def test_terminal_hold(self):
  for r in illustrate.DURATIONS:
   p=illustrate.compile_illustrated(self.source(r));e=p['events'][-1]
   self.assertEqual(e['kind'],'stop');self.assertEqual(e['end_frame']-e['start_frame'],2*p['fps'])
 def test_audio_rejected(self):
  s=self.source();s['audio']='music'
  with self.assertRaises(ValueError):illustrate.compile_illustrated(s)
 def test_unknown_coordinates_rejected(self):
  s=self.source();s['camera']={'x':2}
  with self.assertRaises(ValueError):illustrate.compile_illustrated(s)
 def test_no_change_rejected(self):
  s=self.source();s['content']['after']=s['content']['before']
  with self.assertRaises(ValueError):illustrate.compile_illustrated(s)
 def test_invalid_citation_rejected(self):
  s=self.source('retrieval-evidence');s['content']['citations']=['D2']
  with self.assertRaises(ValueError):illustrate.compile_illustrated(s)
 def test_build_and_immutable_review(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'v1';illustrate.build(self.source(),out)
   self.assertTrue((out/'preview.html').exists());self.assertEqual(illustrate.check(out),[])
   with self.assertRaises(FileExistsError):illustrate.build(self.source(),out)
   (out/'runtime/illustrated-player.mjs').write_text('changed')
   self.assertTrue(illustrate.check(out))
 def test_offline_no_fetch(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'v1';illustrate.build(self.source('retrieval-evidence'),out)
   html=(out/'preview.html').read_text();self.assertIn('data:text/javascript;base64,',html)
   self.assertNotIn('src="https://',html)
 def test_renderer_accepts_illustrated_contract(self):
  from validate import validate_project
  self.assertEqual(validate_project(illustrate.compile_illustrated(self.source())),[])
 def test_renderer_rejects_modified_art_contract(self):
  from validate import validate_project
  p=illustrate.compile_illustrated(self.source());p["art"]["assets"]=["generic-card"]
  self.assertTrue(validate_project(p))
 def test_renderer_rejects_modified_event(self):
  from validate import validate_project
  p=illustrate.compile_illustrated(self.source());p["events"][1]["end_frame"]+=1
  self.assertTrue(validate_project(p))
 def test_art_text_budget_rejected_before_render(self):
  s=self.source('retrieval-evidence');s['content']['answer']='一二三四五六七八九十一二三四五六'
  with self.assertRaises(ValueError):illustrate.compile_illustrated(s)
 def test_20_second_readability_floor(self):
  s=self.source();s['duration']=10
  with self.assertRaises(ValueError):illustrate.compile_illustrated(s)
if __name__=='__main__':unittest.main()
