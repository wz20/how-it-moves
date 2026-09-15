"""One topic scene -> self-contained HTML, layered static SVG, or silent MP4.
Final export is blocked until artwork, provenance and per-shot review are present.
"""
from __future__ import annotations
import base64, hashlib, html as html_lib, json, os, shutil, subprocess, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
import topic_model as m

RUNTIME=Path(__file__).resolve().parents[1]/'runtime/topic-player.js'
SVG='http://www.w3.org/2000/svg'
ET.register_namespace('',SVG)

def tag(name):return '{'+SVG+'}'+name

def svg(data,root,frame):
    meta=m.validate(data,root)
    m.require(type(frame)==int and 0<=frame<round(data['duration']*data['fps']),'E_FRAME','SVG frame outside timeline')
    m.layout(data,meta,frame)
    W,H=data['width'],data['height']
    node=ET.Element(tag('svg'),{'id':'stage','width':str(W),'height':str(H),'viewBox':f'0 0 {W} {H}',
        'role':'img','aria-labelledby':'_title _description'})
    ET.SubElement(node,tag('title'),{'id':'_title'}).text=data['topic']
    ET.SubElement(node,tag('desc'),{'id':'_description'}).text='Hybrid SVG: editable text/paths/groups and embedded-raster illustration layers. Not a pure-vector conversion.'
    ET.SubElement(node,tag('metadata')).text=json.dumps({'project_id':data['project_id'],'frame':frame,
        'format_kind':'hybrid-svg','artwork':'embedded-raster','font_files_embedded':False},ensure_ascii=False)
    ET.SubElement(node,tag('rect'),{'width':str(W),'height':str(H),'fill':data.get('background','#F8F4EA')})
    assets={a['id']:a for a in data['assets']}
    for l in data['layers']:
        s=m.layer_state(l,frame,data);typ=l.get('type','image')
        attrs={'id':l['id'],'opacity':str(s['opacity']),'data-layer-type':typ}
        if typ!='path':attrs['transform']=f'translate({s["x"]} {s["y"]}) rotate({s["rotate"]}) scale({s["scale"]})'
        g=ET.SubElement(node,tag('g'),attrs)
        if typ=='image':
            a=assets[l['asset']]; p=m.local(root,a['path']);fmt=meta[a['id']]['format'];mime={'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp'}[fmt]
            uri='data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
            ET.SubElement(g,tag('image'),{'data-asset-id':a['id'],'href':uri,'x':str(-s['width']/2),'y':str(-s['height']/2),
                'width':str(s['width']),'height':str(s['height']),'preserveAspectRatio':'xMidYMid meet'})
        elif typ=='text':
            anchor='start' if l.get('slot') in ('title','subtitle') else 'middle'
            ET.SubElement(g,tag('text'),{'x':'0','y':'0','font-size':str(l.get('size',32)),'font-family':'sans-serif',
                'font-weight':'600','text-anchor':anchor,'dominant-baseline':'middle','fill':l.get('color','#263748')}).text=l['text']
        else:
            d='M '+' L '.join(f'{p[0]*W} {p[1]*H}' for p in l['points'])
            ET.SubElement(g,tag('path'),{'d':d,'fill':'none','stroke':l.get('color','#263748'),'stroke-width':str(l.get('stroke_width',4)),
                'stroke-linecap':'round','stroke-linejoin':'round'})
    shot=next(s for s in data['shots'] if s['start']<=frame<s['end'])
    ET.SubElement(node,tag('text'),{'id':'_caption','x':str(W/2),'y':str(H*.95),'text-anchor':'middle','font-family':'sans-serif',
        'font-size':str(round(W/60)),'font-weight':'600','fill':'#263748'}).text=shot['caption']
    return ET.tostring(node,encoding='unicode')


def html(data,root,draft=False):
    public={k:data[k] for k in ('topic','width','height','duration','fps','layers','shots')}
    source=json.dumps(public,ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    css='''body{margin:0;background:#171e27;color:#eee;font-family:sans-serif}main{max-width:1280px;margin:auto}#stage{display:block;width:100%;height:auto}nav{display:flex;gap:16px;align-items:center;padding:16px}input{flex:1}button{font:inherit;padding:8px 20px}aside{padding:12px;background:#853b20}button:focus-visible,input:focus-visible{outline:3px solid #68d5c8}'''
    banner='<aside>内部审片草稿 · 未批准，不得作为成品交付 / REVIEW DRAFT</aside>' if draft else ''
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+\
        '<title>'+html_lib.escape(data['topic'])+'</title><style>'+css+'</style><main>'+banner+svg(data,root,0 if any(x in data['formats'] for x in ('html','video')) else data['poster_frame'])+\
        '<nav aria-label="动画控制"><button id="toggle">播放</button><input id="seek" aria-label="动画时间轴" type="range" min="0" value="0"><span id="clock"></span></nav></main>'+\
        '<script>'+RUNTIME.read_text(encoding='utf-8')+'\nmountTopicPlayer('+source+','+json.dumps(m.SLOTS)+','+json.dumps(m.TEXT_SLOTS)+');</script></html>'


def fingerprint(data,root):
    m.validate(data,root)
    h=hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True,allow_nan=False).encode())
    for p in (Path(m.__file__),Path(__file__),RUNTIME):h.update(p.read_bytes())
    for a in data['assets']:h.update(m.local(root,a['path']).read_bytes())
    return h.hexdigest()


def required_frames(data):
    return m.frames(data) if any(x in data['formats'] for x in ('html','video')) else [data['poster_frame']]


def browser():
    try:from playwright.sync_api import sync_playwright
    except ImportError:m.fail('E_BROWSER','Review capture/video needs Playwright and Chromium; SVG/HTML final serialization does not.')
    pw=sync_playwright().start()
    try:
        options={'headless':True,'args':['--disable-dev-shm-usage']}
        path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
        if path:options['executable_path']=path
        if hasattr(os,'geteuid') and os.geteuid()==0:options['args'].append('--no-sandbox')
        b=pw.chromium.launch(**options)
        return pw,b
    except Exception:pw.stop();raise


def capture(data,root,indices,destination):
    pw,b=browser(); images=[]; errors=[]
    try:
        page=b.new_page(viewport={'width':data['width'],'height':data['height']+100},device_scale_factor=1)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('http://**/*',lambda r:r.abort());page.route('https://**/*',lambda r:r.abort())
        page.set_content(html(data,root),wait_until='load')
        page.add_style_tag(content=f'main{{max-width:none}}#stage{{width:{data["width"]}px;height:{data["height"]}px}}')
        page.wait_for_function('window.ready===true',timeout=30000)
        for f in indices:
            page.evaluate('(f)=>window.renderFrame(f)',f)
            target=destination/f'{f:06d}.png';page.locator('#stage').screenshot(path=str(target),animations='disabled')
            images.append({'frame':f,'path':str(target.relative_to(root)) if target.is_relative_to(root) else str(target),'sha256':m.sha(target)})
        m.require(not errors,'E_BROWSER','; '.join(errors))
        return images
    finally:b.close();pw.stop()


def prepare_review(data,root,directory):
    m.validate(data,root);root=Path(root).resolve();directory=Path(directory).resolve()
    m.require(directory.is_relative_to(root),'E_PATH','review evidence must be within project')
    m.require(not directory.exists(),'E_EXISTS','use a new review directory')
    directory.mkdir(parents=True)
    (directory/'draft.html').write_text(html(data,root,True),encoding='utf-8')
    evidence=capture(data,root,required_frames(data),directory)
    views=['asset_quality','not_slides','readability','mechanism']
    if any(x in data['formats'] for x in ('html','video')):views+=['causal_motion']
    report={'schema_version':1,'fingerprint':fingerprint(data,root),'verdict':'pending','reviewer':'','method':'',
        'reviewed_formats':data['formats'],'evidence':evidence,'shots':[
            {'id':s['id'],'verdict':'pending','findings':{k:'' for k in views}} for s in data['shots']]}
    (directory/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return directory/'review.json'


def check_review(data,root,review_file,selected):
    m.require(review_file is not None,'E_REVIEW','capture and inspect artwork/shot transitions before final export')
    root=Path(root).resolve();rp=Path(review_file).resolve()
    m.require(rp.is_relative_to(root) and rp.is_file(),'E_REVIEW','review file must exist within project')
    review=json.loads(rp.read_text(encoding='utf-8'))
    m.require(review.get('verdict')=='approved','E_REVIEW','review is not approved')
    m.require(review.get('fingerprint')==fingerprint(data,root),'E_REVIEW_STALE','source, assets or exporter changed; recapture and re-review')
    m.string(review.get('reviewer'),'reviewer',160)
    m.require(review.get('method') in ('human','vision-agent'),'E_REVIEW','visual review by a human or vision-capable agent is required')
    m.require(set(selected)<=set(review.get('reviewed_formats',[])),'E_REVIEW','output format not reviewed')
    evidence=review.get('evidence',[])
    m.require({e.get('frame') for e in evidence}==set(required_frames(data)),'E_REVIEW','missing required frames')
    for e in evidence:m.require(m.sha(m.local(root,e.get('path')))==e.get('sha256'),'E_REVIEW','evidence hash mismatch')
    shots=review.get('shots',[])
    m.require(len(shots)==len(data['shots']) and {s.get('id') for s in shots}=={s['id'] for s in data['shots']},'E_REVIEW','every shot must be inspected')
    checks=['asset_quality','not_slides','readability','mechanism']
    if any(x in selected for x in ('html','video')):checks+=['causal_motion']
    for shot in shots:
        m.require(shot.get('verdict')=='approved','E_REVIEW','unapproved shot')
        for k in checks:
            finding=shot.get('findings',{}).get(k)
            m.string(finding,'review.'+k,800);m.require(len(finding.strip())>=12,'E_REVIEW','record a specific finding, not just pass')
    return review


def render_video(data,root,target,review):
    ffmpeg=shutil.which('ffmpeg');probe=shutil.which('ffprobe')
    m.require(ffmpeg and probe,'E_VIDEO_DEP','MP4 needs ffmpeg and ffprobe; other formats do not')
    count=round(data['duration']*data['fps'])
    with tempfile.TemporaryDirectory(prefix='topic-frames-') as temp:
        temp=Path(temp);capture(data,root,range(count),temp)
        for e in review['evidence']:
            m.require(m.sha(temp/f'{e["frame"]:06d}.png')==e['sha256'],'E_REVIEW_PIXELS','export differs from reviewed pixels; re-review in this environment')
        cmd=[ffmpeg,'-v','error','-y','-framerate',str(data['fps']),'-i',str(temp/'%06d.png'),'-frames:v',str(count),'-an',
             '-c:v','libx264','-threads','2','-preset','medium','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
        subprocess.run(cmd,check=True,timeout=900)
    metadata=json.loads(subprocess.check_output([probe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)],text=True))
    streams=metadata['streams'];v=[s for s in streams if s['codec_type']=='video']
    m.require(len(streams)==1 and len(v)==1 and int(v[0]['nb_read_frames'])==count,'E_VIDEO','wrong streams/frame count')
    m.require(v[0]['width']==data['width'] and v[0]['height']==data['height'],'E_VIDEO','wrong size')
    m.require(abs(float(metadata['format']['duration'])-data['duration'])<=1/data['fps'],'E_VIDEO','wrong duration')
    subprocess.run([ffmpeg,'-v','error','-xerror','-i',str(target),'-f','null','-'],check=True,timeout=900)
    return metadata


def export(data,root,destination,selected=None,review_file=None,svg_frame=None):
    selected=m.formats(data['formats'] if selected is None else selected);m.validate(data,root)
    m.require(set(selected)<=set(data['formats']),'E_FORMAT','set formats in source before review')
    review=check_review(data,root,review_file,selected)
    frame=data['poster_frame'] if svg_frame is None else svg_frame
    m.require(frame in {e['frame'] for e in review['evidence']},'E_REVIEW','SVG frame must have reviewed evidence')
    dest=Path(destination).resolve();m.require(not dest.exists(),'E_EXISTS','refuse overwrite; use a new destination')
    dest.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.topic-delivery-',dir=dest.parent))
    try:
        report={'project_id':data['project_id'],'formats':selected,'source_fingerprint':fingerprint(data,root),
                'svg_kind':'hybrid: editable vectors plus embedded generated raster layers','audio':'none','files':{},'reviewer':review['reviewer']}
        if 'html' in selected:(stage/'animation.html').write_text(html(data,root),encoding='utf-8')
        if 'svg' in selected:(stage/'illustration.svg').write_text(svg(data,root,frame),encoding='utf-8')
        if 'video' in selected:report['video']=render_video(data,root,stage/'video.mp4',review)
        for p in stage.iterdir():report['files'][p.name]={'bytes':p.stat().st_size,'sha256':m.sha(p)}
        (stage/'delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        c=data['concept'];history={'project_id':data['project_id'],'topic':data['topic'],
            'world':c['candidates'][c['selected']]['world'],'asset_hashes':[a['sha256'] for a in data['assets']]}
        (stage/'asset-history-entry.json').write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        # mkdir is the last race-safe reservation; don't merge output with an existing folder.
        dest.mkdir()
        for p in stage.iterdir():p.rename(dest/p.name)
        return report
    finally:shutil.rmtree(stage,ignore_errors=True)
