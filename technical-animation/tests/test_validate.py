"""Semantic contract regressions. Run without API access."""
import copy, importlib.util, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validate',ROOT/'scripts'/'validate.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
BASE={
 'title':'Agent loop','width':1920,'height':1080,'fps':60,'duration':10,'audio':'none',
 'takeaway':'Tool feedback changes the next decision.', 'entry':'index.html',
 'events':[
 {'id':'call','kind':'call','start':1.,'end':2.,'actor':'model','target':'tool','label':'RUN'},
 {'id':'result','kind':'result','start':2.2,'end':3.,'actor':'tool','target':'model','label':'FAIL','caused_by':'call'},
 {'id':'decision','kind':'decision','start':3.2,'end':4.,'actor':'model','label':'PATCH','caused_by':'result'},
 {'id':'stop','kind':'stop','start':8.,'end':10.,'actor':'model','label':'DONE','caused_by':'decision'}],
 'assets':[], 'sources':[{'url':'https://www.anthropic.com/engineering/building-effective-agents','claim':'feedback loop'}]
}
class Tests(unittest.TestCase):
 def test_draft_blocked(self):
  d=copy.deepcopy(BASE);d['ready_for_render']=False
  self.assertTrue(any('draft' in s for s in m.validate_project(d)))
 def test_good(self): self.assertEqual(m.validate_project(BASE),[])
 def test_early_result(self):
  d=copy.deepcopy(BASE);d['events'][1]['start']=1.3
  self.assertTrue(any('causality' in s for s in m.validate_project(d)))
 def test_unknown_cause(self):
  d=copy.deepcopy(BASE);d['events'][2]['caused_by']='missing'
  self.assertTrue(any('unknown' in s for s in m.validate_project(d)))
 def test_overrun(self):
  d=copy.deepcopy(BASE);d['events'][-1]['end']=11
  self.assertTrue(any('outside' in s for s in m.validate_project(d)))
 def test_missing_feedback(self):
  d=copy.deepcopy(BASE);d['events'][1]['kind']='decorative'
  self.assertTrue(any('feedback' in s for s in m.validate_project(d)))
 def test_fractional_frames(self):
  d=copy.deepcopy(BASE);d['duration']=10.001
  self.assertTrue(any('integer' in s for s in m.validate_project(d)))
 def test_rejected_asset(self):
  d=copy.deepcopy(BASE);d['assets']=[{'path':'bad.png','status':'rejected','used':True,'origin':'image-generation'}]
  self.assertTrue(any('rejected' in s for s in m.validate_project(d)))
 def test_no_path_traversal(self):
  d=copy.deepcopy(BASE);d['entry']='../../secret.html'
  self.assertTrue(any('entry' in s for s in m.validate_project(d)))
if __name__=='__main__':unittest.main()
