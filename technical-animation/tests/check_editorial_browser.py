#!/usr/bin/env python3
"""Inspect all frames, causal boundaries, pixel determinism and player controls. Not an audience study."""
import argparse, asyncio, copy, hashlib, json, os, shutil, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from direct import build

async def run(out,browser):
 from playwright.async_api import async_playwright
 sample=json.loads((ROOT/'directing/partition-search.json').read_text())
 maximum=copy.deepcopy(sample)
 maximum['title']='知识怎样经过这个多层搜索过程'*2
 maximum['title']=maximum['title'][:24]
 maximum['query']='查询指定图片内容'
 maximum['takeaway']='先确定范围再并行搜索最后按候选相似度排序返回'
 for i,g in enumerate(maximum['groups']):g['label']='分区分类组'+str(i)
 for i,s in enumerate(maximum['segments']):
  s['label']='检索段'+str(i)
  for j,c in enumerate(s['candidates']):c['id']=f'item{i}{j}xx'
 maximum['selected_group']=maximum['groups'][0]['id']
 small=copy.deepcopy(maximum);small['selected_group']=small['groups'][2]['id'];small['duration']=20;small['fps']=30;small['top_k']=1
 cases=[('default',sample),('max-text-first',maximum),('30fps-last',small)]
 report={'cases':[],'audience_test':False,'weak_model_test':False,'audio_review':False}
 with tempfile.TemporaryDirectory(prefix='how-it-moves-browser-') as td:
  async with async_playwright() as p:
   opts={'headless':True,'executable_path':browser,'args':['--disable-dev-shm-usage']}
   if hasattr(os,'geteuid') and os.geteuid()==0:opts['args'].append('--no-sandbox')
   b=await p.chromium.launch(**opts)
   for name,cfg in cases:
    project=build(cfg,Path(td)/name);page=await b.new_page(viewport={'width':1920,'height':1080});errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    await page.route('http://**/*',lambda route:route.abort());await page.route('https://**/*',lambda route:route.abort())
    await page.set_content((project/'preview.html').read_text(),wait_until='load');await page.wait_for_function('window.ready===true')
    result=await page.evaluate('''()=>{
      const spec=window.videoMeta,n=spec.duration*spec.fps,failures=[];let lastReturned=0;
      for(let f=0;f<n;f++){
       const s=window.renderFrame(f);
       if(s.layoutIssues.length)failures.push({frame:f,issues:s.layoutIssues});
       if(s.returned.length<lastReturned)failures.push({frame:f,issue:'result count went backwards'});
       if(s.ranking && s.returned.length!==3)failures.push({frame:f,issue:'rank before all returns'});
       if(s.stopped && s.packetCount!==0)failures.push({frame:f,issue:'packet after stop'});
       if(s.queryId!=='Q1'||s.focusedIds.length>3)failures.push({frame:f,issue:'identity/focus budget'});
       lastReturned=s.returned.length;
      }
      const frames=[0,Math.floor(n*.3),Math.floor(n*.72),n-1];
      const hashes=frames.map(f=>{window.renderFrame(f);return stage.toDataURL()});
      window.renderFrame(n-1);window.renderFrame(0);
      const deterministic=frames.every((f,i)=>{window.renderFrame(f);return stage.toDataURL()===hashes[i]});
      return {frames_checked:n,failures:failures.slice(0,12),failure_count:failures.length,deterministic};
    }''')
    await page.evaluate('window.renderFrame(0)');await page.click('#toggle');await page.wait_for_timeout(260)
    played=await page.evaluate('window.semanticState.frame>0')
    await page.click('#toggle');paused=await page.evaluate('window.semanticState.frame');await page.wait_for_timeout(160)
    pause_ok=paused==await page.evaluate('window.semanticState.frame')
    seek_ok=await page.evaluate("()=>{seek.value=String(Math.floor(window.videoMeta.fps*window.videoMeta.duration/2));seek.dispatchEvent(new Event('input'));return window.semanticState.frame===Number(seek.value)}")
    result.update(name=name,play=played,pause=pause_ok,seek=seek_ok,console_errors=errors)
    report['cases'].append(result)
    await page.close()
   await b.close()
 report['passed']=all(not c['failure_count'] and c['deterministic'] and c['play'] and c['pause'] and c['seek'] and not c['console_errors'] for c in report['cases'])
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2))
 if not report['passed']:raise SystemExit(1)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--browser',default=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'));a=ap.parse_args()
 if not a.browser:ap.error('Specify an installed browser with --browser')
 asyncio.run(run(a.out,a.browser))
