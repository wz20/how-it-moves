#!/usr/bin/env python3
"""Render every frame, reject invalid geometry/text overflow, test state and controls."""
import argparse, base64, hashlib, json, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import illustrate
from recipe_core import state_at_frame
from playwright.sync_api import sync_playwright

def check_all(out,browser=None):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);results=[]
 with tempfile.TemporaryDirectory() as td, sync_playwright() as p:
  opts={'headless':True,'args':['--disable-dev-shm-usage']}
  import os,shutil
  if hasattr(os,'geteuid') and os.geteuid()==0:opts['args'].append('--no-sandbox')
  browser=browser or os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
  if browser:opts['executable_path']=browser
  b=p.chromium.launch(**opts)
  for r in illustrate.DURATIONS:
   build=Path(td)/r;spec=illustrate.build(illustrate.example(r),build)
   page=b.new_page(viewport={'width':1920,'height':1080});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
   page.set_content((build/'preview.html').read_text(),wait_until='load');page.wait_for_function('window.ready===true')
   # Invalid bezier/path coordinates can otherwise silently disappear on Canvas.
   page.evaluate('''()=>{for(const n of ['moveTo','lineTo','translate','scale','arc','ellipse','bezierCurveTo','quadraticCurveTo']){const p=CanvasRenderingContext2D.prototype,old=p[n];p[n]=function(...a){for(const x of a)if(typeof x==='number'&&!Number.isFinite(x))throw new Error('nonfinite '+n);return old.apply(this,a)}}}''')
   n=round(spec['duration']*spec['fps'])
   for start in range(0,n,120):
    report=page.evaluate('''([a,b])=>{for(let f=a;f<b;f++){const s=window.renderFrame(f);if(s.layoutIssues.length)return {f,issues:s.layoutIssues};if(s.stopped&&s.packetCount)throw new Error('packets after stop')}return null}''',[start,min(n,start+120)])
    if report:raise AssertionError((r,report))
   for ev in spec['events']:
    for f in [ev['start_frame'],min(n-1,ev['end_frame'])]:
     actual=page.evaluate('(f)=>window.renderFrame(f)',f);expected=state_at_frame(spec,f)
     for k,v in expected.items():assert actual[k]==v,(r,f,k,actual.get(k),v)
   final=page.evaluate('(f)=>window.renderFrame(f)',n-1)
   if r=='cache-aside':assert final['db_reads']==1 and final['responses']==2
   if r=='feedback-retry':assert final['test_runs']==2 and final['code_changed']
   if r=='retrieval-evidence':assert final['delivered'] and final['context_ready']
   def png(f):return base64.b64decode(page.evaluate('(f)=>{window.renderFrame(f);return document.getElementById("stage").toDataURL().split(",")[1]}',f))
   images={}
   for f in [n//4,n//2,n-1]:
    v=png(f);png(0);assert v==png(f),(r,'seek nondeterminism');images[str(f)]=hashlib.sha256(v).hexdigest();(out/f'{r}-{f}.png').write_bytes(v)
   page.evaluate('()=>window.renderFrame(0)');page.click('#toggle');page.wait_for_timeout(230)
   assert page.evaluate('Number(document.getElementById("seek").value)')>0
   page.click('#toggle');x=page.evaluate('Number(document.getElementById("seek").value)');page.wait_for_timeout(90)
   assert page.evaluate('Number(document.getElementById("seek").value)')==x
   page.locator('#seek').evaluate('(e)=>{e.value=300;e.dispatchEvent(new Event("input"))}')
   assert page.evaluate('window.semanticState.frame')==300
   assert not errs,errs
   results.append({'recipe':r,'frames_checked':n,'finite_geometry':True,'text_width':True,'semantic_boundaries':True,'seek_deterministic':True,'controls':True,'images':images})
   print('PASS',r,n,flush=True);page.close()
  b.close()
 result={'results':results,'limits':'Does not establish aesthetic superiority, weak-model success rate or audience comprehension.'}
 (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--browser');o=a.parse_args();check_all(o.out,o.browser)
