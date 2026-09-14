#!/usr/bin/env python3
"""Frame-exact, silent Canvas video renderer. No API keys or realtime screen recording."""
from __future__ import annotations
import argparse, asyncio, base64, hashlib, json, os, shutil, subprocess, tempfile, time
from pathlib import Path
from validate import validate_project
from bundle import bundle_html

async def render(args, data, project, root):
    try: from playwright.async_api import async_playwright
    except ImportError: raise RuntimeError('Install: python -m pip install -r requirements.txt; python -m playwright install chromium')
    errors=validate_project(data)
    if errors:raise RuntimeError('\n'.join(errors))
    count=round(data['fps']*data['duration']); selected=[int(i) for i in args.frames.split(',')] if args.frames else list(range(count))
    if any(f<0 or f>=count for f in selected): raise RuntimeError(f'Frame outside [0, {count-1}]')
    out=args.out.resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    width,height=data['width'],data['height']
    # snapshot paths are retained; full frame sequence uses an isolated temp dir
    framesdir=out if args.frames else Path(tempfile.mkdtemp(prefix='explain-frames-'))
    framesdir.mkdir(parents=True,exist_ok=True)
    html=bundle_html(project,root)
    browser_path=args.browser or os.environ.get('CHROMIUM_PATH')
    if not browser_path:
        browser_path=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
    js_errors=[]; hashes={}; states={}; start=time.monotonic()
    try:
      async with async_playwright() as p:
        options={'headless':True,'args':['--disable-dev-shm-usage']}
        if browser_path:options['executable_path']=browser_path
        # Chromium sandbox cannot run as root; do not disable it for normal users.
        if hasattr(os,'geteuid') and os.geteuid()==0:options['args'].append('--no-sandbox')
        browser=await p.chromium.launch(**options)
        async def worker(items):
            page=await browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            page.on('pageerror',lambda e:js_errors.append(str(e)))
            await page.set_content(html,wait_until='load');await page.wait_for_function('window.ready === true');await page.evaluate('document.body.classList.add("capture")')
            # Prevent hidden external dependencies in the example during capture.
            for f in items:
                result=await page.evaluate('''(f) => {window.renderFrame(f);const c=document.getElementById('stage');return {image:c.toDataURL('image/png').split(',')[1],state:window.semanticState||null}}''',f)
                raw=base64.b64decode(result['image']); (framesdir/f'{f:06d}.png').write_bytes(raw)
                if f in (0,count//2,count-1) or args.frames:
                    hashes[str(f)]=hashlib.sha256(raw).hexdigest();states[str(f)]=result['state']
                if not args.frames and f%100==0:print(f'frame {f:03d}/{count}  elapsed {time.monotonic()-start:.1f}s',flush=True)
            # Random-access determinism: the same frame must be bit-identical after seeking.
            if items:
                f=items[len(items)//2]
                await page.evaluate('(f)=>window.renderFrame(f)',0)
                raw2=base64.b64decode(await page.evaluate('(f)=>{window.renderFrame(f);return document.getElementById("stage").toDataURL("image/png").split(",")[1]}',f))
                if raw2!=(framesdir/f'{f:06d}.png').read_bytes():raise RuntimeError(f'Non-deterministic frame {f}')
            await page.close()
        jobs=min(args.jobs,len(selected));await asyncio.gather(*(worker(selected[j::jobs]) for j in range(jobs)))
        await browser.close()
      if js_errors:raise RuntimeError('Browser errors:\n'+'\n'.join(js_errors))
      report={'title':data['title'],'browser':browser_path or 'Playwright managed Chromium','width':width,'height':height,'fps':data['fps'],'frames_requested':len(selected),'duration':data['duration'],'audio':'none','random_access_deterministic':True,'console_errors':js_errors,'selected_hashes':hashes,'semantic_samples':states,'elapsed_seconds':round(time.monotonic()-start,2)}
      if not args.frames:
        ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe')
        if not ffmpeg or not ffprobe:raise RuntimeError('ffmpeg and ffprobe are required on PATH')
        cmd=[ffmpeg,'-y','-hide_banner','-loglevel','error','-framerate',str(data['fps']),'-i',str(framesdir/'%06d.png'),'-frames:v',str(count),'-an','-c:v','libx264','-preset','slow','-crf',str(args.crf),'-pix_fmt','yuv420p','-movflags','+faststart','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(out)]
        subprocess.run(cmd,check=True)
        meta=json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)],text=True))
        videos=[s for s in meta['streams'] if s['codec_type']=='video']; audios=[s for s in meta['streams'] if s['codec_type']=='audio']
        assert len(videos)==1 and not audios,'Unexpected stream layout'
        v=videos[0];assert int(v['nb_read_frames'])==count,'Frame count mismatch'
        assert v['width']==width and v['height']==height,'Output size mismatch'
        assert abs(float(meta['format']['duration'])-data['duration'])<=1/data['fps'],'Duration mismatch'
        subprocess.run([ffmpeg,'-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
        report.update({'video_decode':'pass','video_frame_count':int(v['nb_read_frames']),'output_bytes':out.stat().st_size,'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'ffprobe':meta})
        reportpath=out.with_suffix('.qa.json')
      else:reportpath=out/'snapshots.qa.json'
      reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
      print(f'OK: {out}\nQA: {reportpath}',flush=True)
    finally:
      if not args.frames and not args.keep_frames:shutil.rmtree(framesdir,ignore_errors=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--frames',help='Comma separated snapshot frame indices; --out becomes a directory')
    parser.add_argument('--jobs',type=int,default=2);parser.add_argument('--browser',help='Chromium executable path')
    parser.add_argument('--crf',type=int,default=16);parser.add_argument('--keep-frames',action='store_true')
    args=parser.parse_args()
    if not 1<=args.jobs<=8:parser.error('--jobs must be 1..8')
    if not 0<=args.crf<=30:parser.error('--crf must be 0..30')
    project=args.project.resolve();root=Path(__file__).resolve().parents[1]
    if not project.is_relative_to(root):root=project
    if not (project/'project.json').exists():raise SystemExit(f'Missing {project}/project.json')
    data=json.loads((project/'project.json').read_text(encoding='utf-8'))
    if data.get('audio','none')!='none':raise SystemExit('This renderer supports silent exports only. Use a configured audio-capable adapter for narration/music.')
    try:asyncio.run(render(args,data,project,root))
    except Exception as exc:raise SystemExit(f'RENDER FAILED: {exc}')
if __name__=='__main__':main()
