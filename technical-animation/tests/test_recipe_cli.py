import importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path
S=Path(__file__).resolve().parents[1];CLI=S/'scripts/recipe.py'
class CLITests(unittest.TestCase):
 def run_cli(self,*args):
  self.assertTrue(CLI.exists(),'Recipe CLI missing; simple configs cannot yet produce animation')
  return subprocess.run([sys.executable,str(CLI),*map(str,args)],capture_output=True,text=True)
 def test_list(self):
  p=self.run_cli('list');self.assertEqual(p.returncode,0,p.stderr);self.assertIn('cache-aside',p.stdout)
 def test_portable_build(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/'movie';p=self.run_cli('build',S/'recipes/retrieval-evidence.json','--out',out)
   self.assertEqual(p.returncode,0,p.stderr);self.assertTrue((out/'preview.html').is_file())
   html=(out/'preview.html').read_text();self.assertIn('data:text/javascript;base64,',html)
   self.assertNotIn('<script src="https:',html)
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as td:
   p=self.run_cli('build',S/'recipes/cache-aside.json','--out',td)
   self.assertNotEqual(p.returncode,0);self.assertIn('E_EXISTS',p.stderr)
 def test_invalid_writes_nothing(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/'bad.json';src.write_text('{"recipe":"garbage"}');out=Path(td)/'out'
   p=self.run_cli('build',src,'--out',out);self.assertNotEqual(p.returncode,0);self.assertFalse(out.exists())
 def test_init_refuses_existing(self):
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'s.json';f.write_text('keep');p=self.run_cli('init','--recipe','feedback-retry','--out',f)
   self.assertNotEqual(p.returncode,0);self.assertEqual(f.read_text(),'keep')
 def test_tampered_contract_check(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/'movie';self.assertEqual(self.run_cli('build',S/'recipes/cache-aside.json','--out',out).returncode,0)
   f=out/'project.json';j=json.loads(f.read_text());j['events'][0]['end_frame']=9;f.write_text(json.dumps(j))
   p=self.run_cli('check',out);self.assertNotEqual(p.returncode,0);self.assertIn('E_CONTRACT',p.stderr)
if __name__=='__main__':unittest.main()
