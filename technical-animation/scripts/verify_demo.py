#!/usr/bin/env python3
"""Exercise the actual browser scene and offline player's controls."""
from pathlib import Path
import json,os,shutil
from playwright.sync_api import sync_playwright
from bundle import bundle_html
root=Path(__file__).resolve().parents[1];project=root/'examples'/'agent-loop'
html=bundle_html(project,root);evidence=[]
with sync_playwright() as p:
 options={'headless':True}
 executable=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('chromium-browser')
 if executable:options['executable_path']=executable
 if hasattr(os,'geteuid') and os.geteuid()==0:options['args']=['--no-sandbox']
 browser=p.chromium.launch(**options);page=browser.new_page(viewport={'width':1280,'height':800});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html);page.wait_for_function('window.ready===true')
 checks=[(120,{'tool':'idle','feedbackReceived':False}),(123,{'tool':'running'}),(162,{'tool':'fail'}),(209,{'feedbackReceived':False}),(210,{'feedbackReceived':True}),(308,{'patched':False}),(309,{'patched':True}),(404,{'tool':'running'}),(405,{'tool':'pass'}),(446,{'done':False}),(480,{'done':True})]
 for f,wanted in checks:
  observed=page.evaluate('(f)=>{renderFrame(f);return semanticState}',f)
  for k,v in wanted.items():assert observed[k]==v,f'{f}: {k}: {observed[k]} != {v}'
  evidence.append({'frame':f,'expected':wanted,'observed':observed})
 page.locator('#toggle').click();page.wait_for_timeout(450);a=page.evaluate('semanticState.frame');page.wait_for_timeout(450);b=page.evaluate('semanticState.frame');assert b>a,'playback did not advance'
 page.locator('#toggle').click();page.evaluate('let s=document.querySelector("#seek");s.value=480;s.dispatchEvent(new Event("input"))');assert page.evaluate('semanticState.frame')==480
 assert not errors,errors
 browser.close()
report={'causal_boundary_checks':len(checks),'checks':evidence,'playback_advance':[a,b],'scrubber_frame':480,'browser_errors':errors,'status':'pass'}
(project/'player-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('PASS: 11 actual-scene boundary checks, playback advance, pause, and frame scrubber')
