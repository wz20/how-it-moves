"""Topic-first scene contract. No provider API, canned subject catalog or executable JSON."""
from __future__ import annotations
import hashlib, json, math, re, uuid
from pathlib import Path

class Problem(ValueError):
    def __init__(self, code, message): super().__init__(f'{code}: {message}'); self.code=code

def fail(code, message): raise Problem(code, message)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(test, code, message):
    if not test: fail(code, message)
def string(value, field, limit=600):
    require(isinstance(value,str) and value.strip() and len(value)<=limit and not any(ord(c)<32 for c in value),'E_TEXT',field)
    require(not re.search(r'TODO|PLACEHOLDER|ACTUAL_FILE|待填写|待生成',value,re.I),'E_PENDING',field+' is unfinished')
    return value

def number(v, field, lo=-1e6, hi=1e6):
    require(type(v) in (int,float) and math.isfinite(v) and lo<=v<=hi,'E_NUMBER',field)
    return v

def local(root, name):
    require(isinstance(name,str) and name and not Path(name).is_absolute() and ':' not in name,'E_PATH',str(name))
    root=Path(root).resolve(); p=(root/name).resolve()
    require(p.is_relative_to(root),'E_PATH',name+' escapes project')
    require(p.is_file(),'E_PATH','missing '+name)
    return p

def formats(values):
    require(isinstance(values,list) and 1<=len(values)<=3,'E_FORMAT','select html, video and/or svg')
    result=[]
    for v in values:
        v='video' if v=='mp4' else v
        require(v in ('html','video','svg'),'E_FORMAT',str(v))
        require(v not in result,'E_FORMAT','duplicate '+v); result.append(v)
    return result

# Slots are layout anchors, not asset identities. No topic-to-robot/cabinet lookup exists.
SLOTS={'left':(.07,.25,.35,.60),'center':(.325,.25,.35,.60),'right':(.58,.25,.35,.60),
       'hero':(.20,.21,.60,.64),'top-left':(.07,.18,.35,.36),'top-right':(.58,.18,.35,.36),
       'bottom-left':(.07,.52,.35,.36),'bottom-right':(.58,.52,.35,.36),
       'top':(.32,.15,.36,.42),'bottom':(.32,.51,.36,.38),
       'off-left':(-.36,.25,.35,.60),'off-right':(1.01,.25,.35,.60)}
TEXT_SLOTS={'title':(.05,.085),'subtitle':(.05,.15),'caption':(.50,.92)}
ACTIONS={'extract','store','retrieve','inspect','select','assemble','route','split','merge','compare',
         'update','invalidate','evict','verify','repair','dispatch','return','acknowledge','transform','resolve'}


def blank(topic, outputs):
    return {'schema_version':1,'project_id':'project-'+uuid.uuid4().hex[:12], 'topic':topic,
            'formats':formats(outputs),'width':1920,'height':1080,'fps':60,'duration':12,'poster_frame':600,
            'style':'','concept':{'goal':'','candidates':[],'selected':0,'entities':[],'avoid':[]},
            'history':[],'assets':[],'shots':[],'layers':[]}


def concept(data):
    c=data.get('concept',{}); string(data.get('topic'),'topic',140); string(data.get('style'),'style')
    require(isinstance(c,dict),'E_CONCEPT','concept must be an object')
    string(c.get('goal'),'concept.goal',240)
    cand=c.get('candidates',[])
    require(isinstance(cand,list) and len(cand)==3,'E_VARIETY','write three different visual worlds before choosing')
    worlds=[]
    for entry in cand:
        require(isinstance(entry,dict),'E_CONCEPT','candidate object required')
        for k in ('world','reason','risk'): string(entry.get(k),'candidate.'+k,300)
        worlds.append(entry['world'].strip().casefold())
    require(len(set(worlds))==3,'E_VARIETY','three labels for one world are not three concepts')
    selected=c.get('selected'); require(type(selected)==int and 0<=selected<3,'E_CONCEPT','selected index 0..2')
    entities=c.get('entities',[])
    require(isinstance(entities,list) and 1<=len(entities)<=16,'E_CONCEPT','map technical entities to generated subjects')
    ids=[]
    for e in entities:
        require(isinstance(e,dict),'E_CONCEPT','entity object required')
        for k in ('id','meaning','subject','operation','consequence','invariant'): string(e.get(k),'entity.'+k,400)
        require(re.fullmatch(r'[A-Za-z][\w-]{0,47}',e['id'],re.ASCII),'E_ID',e['id']); ids.append(e['id'])
    require(len(set(ids))==len(ids),'E_ID','duplicate entity')
    require(isinstance(c.get('avoid'),list),'E_CONCEPT','avoid must list unsuitable old subjects/visual shortcuts')
    for x in c['avoid']: string(x,'avoid',140)
    hist=data.get('history',[])
    require(isinstance(hist,list),'E_HISTORY','history must be a list')
    consent=data.get('reuse_consent',{})
    require(isinstance(consent,dict),'E_REUSE','reuse_consent object required')
    for h in hist:
        require(isinstance(h,dict) and isinstance(h.get('asset_hashes',[]),list),'E_HISTORY','invalid record')
        if h.get('project_id')!=data['project_id'] and h.get('world','').strip().casefold()==worlds[selected]:
            require(consent.get('world')==cand[selected]['world'] and consent.get('request_reference'),
                    'E_VARIETY','recent visual world repeated; devise a different world or record explicit user consent')
    return c


def prompts(data):
    c=concept(data); world=c['candidates'][c['selected']]
    lines=['# Generation briefs — NOT generated assets',f'Topic: {data["topic"]}',f'Goal: {c["goal"]}',
           f'Chosen world: {world["world"]}',f'Style: {data["style"]}',
           'Generate separate transparent layers, not a collage or a complete text poster.',
           'Use the host image tool. Record its real response; do not invent a provider receipt.']
    for e in c['entities']:
        lines += ['',f'## {e["id"]}',f'Subject: {e["subject"]}. Technical meaning: {e["meaning"]}.',
            f'Operation: {e["operation"]}. Visible consequence: {e["consequence"]}.',
            f'Preserve: {e["invariant"]}.',f'World: {world["world"]}. Shared art direction: {data["style"]}.',
            'Full silhouette; useful independently movable parts and contact surfaces; consistent camera, light and pivot.',
            'Generate only states necessary for this operation. Preserve identity across states in this project.',
            'No embedded paragraphs, title, arrows, dashboard, watermark or full-slide composition.',
            'Avoid: '+', '.join(c['avoid']),f'Metaphor boundary: {world["risk"]}.']
    if data.get('performance'):
        lines += ['','## Animatable asset requirements (not optional decoration)',
            'All state/body/front/gate layers of one rig share a registration canvas, camera, scale and lighting.',
            'Do not independently crop the door/mask. Transparent margins locate the hinge and contact ports.',
            'Generate masks and movable parts as separate images, never bake the whole explainer into one poster.']
        for r in data['performance'].get('rigs',[]):
            lines += ['',f'Rig {r.get("id")}: artboard {r.get("artboard")}; ports {r.get("anchors")}',
                f'State variants: {r.get("states",{})}. Gate: {r.get("gate")}. Foreground mask: {r.get("front")}. Probe: {r.get("probe")}.',
                'These coordinates must be checked against the actual artwork; they are not image-model guarantees.']
    if data.get('mechanism'):
        from action_requirements import brief
        lines.append(brief(data))
    return '\n'.join(lines)+'\n'


def frames(data):
    result={int(data['poster_frame'])}
    for s in data['shots']:
        a,b=s['start'],s['end']; result.update([a,a+(b-a)//4,a+(b-a)//2,a+3*(b-a)//4,b-1]); result.update(s.get('critical_frames',[]))
    return sorted(result)


def layer_state(layer, frame, data):
    """Pure interpolation. Track frame positions and Python/JS share the same smoothstep."""
    typ=layer.get('type','image'); slot=layer.get('slot','center')
    if typ=='text' and slot in TEXT_SLOTS:
        cx,cy=TEXT_SLOTS[slot]; w=h=0
    else:
        x,y,w,h=layer.get('box',SLOTS[slot]); cx=x+w/2; cy=y+h/2
    base={'x':cx*data['width'],'y':cy*data['height'],'scale':layer.get('scale',1),
          'rotate':layer.get('rotate',0),'opacity':layer.get('opacity',1)}
    points=[]; last=dict(base)
    for key in layer.get('keys',[]):
        p=dict(last)
        if 'slot' in key:
            x,y,_,_=SLOTS[key['slot']]; sw,sh=SLOTS[key['slot']][2:]
            p.update(x=(x+sw/2)*data['width'],y=(y+sh/2)*data['height'])
        for k in ('x','y','scale','rotate','opacity'):
            if k in key:p[k]=key[k]
        points.append((key['frame'],p)); last=p
    if points:
        if frame<=points[0][0]:base=points[0][1].copy()
        elif frame>=points[-1][0]:base=points[-1][1].copy()
        else:
            for (a,p),(b,q) in zip(points,points[1:]):
                if a<=frame<=b:
                    t=(frame-a)/(b-a)
                    dest=next(k for k in layer.get('keys',[]) if k['frame']==b)
                    if dest.get('ease','smooth')!='linear':t=t*t*(3-2*t)
                    base={k:p[k]+(q[k]-p[k])*t for k in p}; break
    base['opacity']*=int(layer.get('start',0)<=frame<layer.get('end',round(data['duration']*data['fps'])))
    base['width']=w*data['width']; base['height']=h*data['height']
    base['asset']=layer.get('asset')
    for k in layer.get('asset_keys',[]):
        if frame>=k['frame']:base['asset']=k['asset']
    iw,ih=layer.get('image_size',[base['width'] or 1,base['height'] or 1]);fit=min(base['width']/iw,base['height']/ih)
    px,py=layer.get('pivot',[.5,.5]);base['pivot_x']=(px-.5)*iw*fit;base['pivot_y']=(py-.5)*ih*fit
    return base


def resolved(data):
    if data.get('mechanism'):
        from mechanism_core import resolve
        return resolve(data)
    if 'performance' not in data:return data
    from perform_core import compile_performance
    return compile_performance(data)



def union_area(rects):
    if not rects:return 0
    xs=sorted({v for r in rects for v in (r[0],r[2])}); total=0
    for a,b in zip(xs,xs[1:]):
        intervals=sorted((r[1],r[3]) for r in rects if r[0]<b and r[2]>a)
        end=-math.inf; length=0
        for lo,hi in intervals:
            length+=max(0,hi-max(lo,end)); end=max(end,hi)
        total+=(b-a)*length
    return total


def validate(data, root):
    require(isinstance(data,dict),'E_SCHEMA','expected JSON object')
    allowed={'schema_version','project_id','topic','formats','width','height','fps','duration','poster_frame','style',
             'concept','history','reuse_consent','assets','shots','layers','background','performance','soundtrack','mechanism','presentation','profile','course'}
    require(not set(data)-allowed,'E_FIELD','unknown fields: '+','.join(sorted(set(data)-allowed)))
    require(type(data.get('schema_version'))==int and data['schema_version']==1,'E_SCHEMA','schema_version must be 1')
    string(data.get('project_id'),'project_id',80); fmt=formats(data.get('formats'))
    require(data['formats']==fmt,'E_FORMAT','use video in JSON; mp4 is only a CLI alias')
    for k in ('width','height'):
        require(type(data.get(k))==int and 320<=data[k]<=4096 and data[k]%2==0,'E_SIZE',k+' must be an even integer 320..4096')
    require(data.get('fps') in (30,60) and type(data['fps'])==int,'E_FPS','30/60fps supported')
    number(data.get('duration'),'duration',1,180); total=data['duration']*data['fps']
    require(total==int(total),'E_TIMELINE','fractional frame count'); total=int(total)
    require(type(data.get('poster_frame'))==int and 0<=data['poster_frame']<total,'E_FRAME','invalid poster_frame')
    require(re.fullmatch(r'#[0-9a-fA-F]{6}',data.get('background','#F8F4EA')),'E_COLOR','background')
    if data.get('soundtrack'):
        import soundtrack
        soundtrack.validate(data,root)
    if data.get('profile')=='academic':
        from academic_delivery import validate_course
        validate_course(data)
    performance='performance' in data
    data=resolved(data)
    c=concept(data); entity_ids={e['id'] for e in c['entities']}
    assets=data.get('assets',[])
    require(isinstance(assets,list) and 1<=len(assets)<=40,'ASSET_BLOCKED','generate topic-specific artwork first')
    from PIL import Image, ImageStat
    meta={}; seen=[]; foreign_hashes=set()
    for h in data.get('history',[]):
        if h.get('project_id')!=data['project_id']:foreign_hashes.update(h.get('asset_hashes',[]))
    consent=data.get('reuse_consent',{})
    for asset in assets:
        require(isinstance(asset,dict),'E_ASSET','asset object required')
        aid=asset.get('id'); require(isinstance(aid,str) and re.fullmatch(r'[A-Za-z][\w-]{0,59}',aid,re.ASCII),'E_ID','invalid asset ID')
        require(asset.get('entity',aid) in entity_ids,'E_ASSET','asset must map to a technical entity: '+str(aid))
        require(aid not in seen,'E_ID','duplicate asset '+aid); seen.append(aid)
        require(asset.get('role') in ('subject','prop','background'),'E_ART','invalid role')
        p=local(root,asset.get('path')); require(p.stat().st_size<=30_000_000,'E_ASSET','asset too large')
        require(sha(p)==asset.get('sha256'),'E_HASH',asset['path'])
        gen=asset.get('generation',{})
        for k in ('project_id','tool','model','run_reference','prompt'):string(gen.get(k),'generation.'+k,6000)
        if gen['project_id']!=data['project_id'] or asset['sha256'] in foreign_hashes:
            require(aid in consent.get('asset_ids',[]) and consent.get('request_reference'),'E_REUSE','fresh art required for '+aid)
        try:
            with Image.open(p) as im:
                require(im.format in ('PNG','JPEG','WEBP'),'E_ASSET','PNG/JPEG/WebP required')
                require(min(im.size)>=256 and im.width*im.height<=40_000_000,'E_ASSET','invalid dimensions')
                require(getattr(im,'n_frames',1)==1,'E_ASSET','use separate still states, not animated input')
                rgba=im.convert('RGBA'); box=rgba.getchannel('A').getbbox()
                require(box and (box[2]-box[0])*(box[3]-box[1])/(im.width*im.height)>=.08,'E_ART','empty/sparse image')
                small=rgba.crop(box).convert('RGB').resize((64,64))
                require(max(ImageStat.Stat(small).stddev)>8,'E_ART','flat placeholder image')
                meta[aid]={'size':list(im.size),'alpha_box':list(box),'format':im.format}
        except Problem:raise
        except Exception as exc:fail('E_ASSET',f'{p.name}: {exc}')
    if performance:
        from perform_core import validate_registration
        validate_registration(data,meta)
    shots=data.get('shots',[]); require(isinstance(shots,list) and shots,'E_TIMELINE','shots required')
    end=0; shot_ids=set()
    for shot in shots:
        string(shot.get('id'),'shot.id',60); require(shot['id'] not in shot_ids,'E_ID','duplicate shot');shot_ids.add(shot['id'])
        require(type(shot.get('start'))==int and type(shot.get('end'))==int and shot['start']==end and end<shot['end']<=total,'E_TIMELINE','shots must cover timeline in order without gaps');end=shot['end']
        string(shot.get('caption'),'caption',42); string(shot.get('change'),'change',400)
        require(shot.get('action') in ACTIONS,'E_ACTION','use an operation, not fade/bounce')
        ids=shot.get('asset_ids',[]);require(isinstance(ids,list) and ids and all(x in meta for x in ids),'E_ART','shot missing actual assets')
        require(any(a['id'] in ids and a['role']!='background' for a in assets),'E_ART','background is not subject')
        require(all(type(f)==int and shot['start']<=f<shot['end'] for f in shot.get('critical_frames',[])),'E_FRAME','critical frame outside shot')
    require(end==total,'E_TIMELINE','shots do not cover duration')
    layers=data.get('layers',[]);require(isinstance(layers,list) and 1<=len(layers)<=80,'E_LAYER','1..80 layers required')
    layer_ids={'stage','toggle','seek','clock','_title','_description','_caption'}
    for l in layers:
        string(l.get('id'),'layer.id',60); require(re.fullmatch(r'[A-Za-z][\w-]*',l['id'],re.ASCII) and l['id'] not in layer_ids,'E_ID','duplicate or invalid layer ID'); layer_ids.add(l['id'])
        allowed_layer={'id','type','asset','slot','start','end','keys','scale','rotate','opacity','text','size','color','points','stroke_width','box','pivot','image_size','asset_keys','purpose'}
        require(not set(l)-allowed_layer,'E_FIELD','unknown layer field')
        require(l.get('purpose','subject') in ('subject','mechanism','label','narration','decoration','camera'),'E_PURPOSE','classify layer purpose without hiding the mechanism')
        typ=l.get('type','image');require(typ in ('image','text','path'),'E_LAYER','image/text/path only')
        require(l.get('slot','center') in SLOTS or typ=='text' and l.get('slot') in TEXT_SLOTS,'E_SLOT','invalid slot')
        a,b=l.get('start',0),l.get('end',total);require(type(a)==int and type(b)==int and 0<=a<b<=total,'E_FRAME','layer visibility')
        for k,lo,hi in [('scale',.01,3),('rotate',-180,180),('opacity',0,1)]:
            number(l.get(k,1 if k!='rotate' else 0),k,lo,hi)
        if typ=='image':
            require(l.get('asset') in meta,'E_ART','unknown layer asset')
            if 'image_size' in l:require(l['image_size']==meta[l['asset']]['size'],'E_REGISTRATION','image_size differs from actual asset')
            prev=-1
            for k in l.get('asset_keys',[]):
                require(isinstance(k,dict) and set(k)=={'frame','asset'} and type(k['frame']) is int and prev<k['frame']<total and k['asset'] in meta,'E_STATE_ART','invalid image state key')
                require(meta[k['asset']]['size']==meta[l['asset']]['size'],'E_REGISTRATION','state artboards must match')
                prev=k['frame']
        if 'box' in l:
            require(isinstance(l['box'],list) and len(l['box'])==4,'E_LAYER','box [x,y,w,h]')
            for i,v in enumerate(l['box']):number(v,'box',-.5 if i<2 else .01,1.5)
        if 'pivot' in l:
            require(isinstance(l['pivot'],list) and len(l['pivot'])==2,'E_PORT','pivot [x,y]')
            for v in l['pivot']:number(v,'pivot',0,1)
        if typ=='text':string(l.get('text'),'layer.text',42);number(l.get('size',32),'text.size',18,84)
        if typ=='path':
            pts=l.get('points',[]);require(isinstance(pts,list) and 2<=len(pts)<=24,'E_PATH','2..24 points required')
            for p in pts:
                require(isinstance(p,list) and len(p)==2,'E_PATH','point [x,y]'); [number(x,'point',0,1) for x in p]
            number(l.get('stroke_width',4),'stroke_width',1,12)
        require(re.fullmatch(r'#[0-9a-fA-F]{6}',l.get('color','#263748')),'E_COLOR','layer.color')
        keys=l.get('keys',[]);require(isinstance(keys,list) and len(keys)<=1024,'E_TRACK','invalid keys')
        if typ=='path':
            require(all(not set(k)-{'frame','opacity'} for k in keys),'E_TRACK','paths currently support visibility/opacity only; do not silently discard transforms')
        last=-1
        for key in keys:
            require(isinstance(key,dict) and not set(key)-{'frame','slot','scale','rotate','opacity','x','y','ease'},'E_FIELD','invalid keyframe')
            require(type(key.get('frame'))==int and last<key['frame']<total,'E_TRACK','key frames must increase');last=key['frame']
            if 'ease' in key:require(key['ease'] in ('linear','smooth'),'E_TRACK','unsupported easing')
            for pos in ('x','y'):
                if pos in key:number(key[pos],pos,-8192,8192)
            if 'slot' in key:require(key['slot'] in SLOTS,'E_SLOT','invalid keyframe slot')
            for k,lo,hi in [('scale',.01,3),('rotate',-180,180),('opacity',0,1)]:
                if k in key:number(key[k],k,lo,hi)
    sample_frames=frames(data) if any(x in fmt for x in ('html','video')) else [data['poster_frame']]
    for f in sample_frames: layout(data,meta,f)
    if not performance and any(f in fmt for f in ('html','video')):
        for shot in shots:
            holding = shot == shots[-1] and shot['action']=='resolve' and (shot['end']-shot['start']) <= 2*data['fps']
            require(holding or any(l.get('type','image')=='image' and l.get('asset') in shot['asset_ids'] and
                         operation_track(l, shot, data) for l in layers),
                    'E_MOTION','each animated shot needs a visible operation track, not identical poses or fades')
    return meta


def operation_track(layer,shot,data):
    keys=layer.get('keys',[])
    for a,b in zip(keys,keys[1:]):
        lo=max(a['frame'],shot['start']);hi=min(b['frame'],shot['end']-1)
        if hi<=lo:continue
        p=layer_state(layer,lo,data);q=layer_state(layer,hi,data)
        if layer_state(layer,(lo+hi)//2,data)['opacity']<.5:continue
        if math.hypot(p['x']-q['x'],p['y']-q['y'])>=12 or abs(p['scale']-q['scale'])>=.08 or abs(p['rotate']-q['rotate'])>=8:return True
    return False


def layout(data,meta,frame):
    W,H=data['width'],data['height']; rects=[]; text_area=0; used=set()
    shot=next(s for s in data['shots'] if s['start']<=frame<s['end'])
    assets={a['id']:a for a in data['assets']}
    for l in data['layers']:
        s=layer_state(l,frame,data)
        if s['opacity']<.5:continue
        typ=l.get('type','image')
        if typ=='image' and assets[s['asset']]['role']!='background':
            size=meta[s['asset']]['size']; b=meta[s['asset']]['alpha_box']
            fit=min(s['width']/size[0],s['height']/size[1])*s['scale']
            if data.get('compiled_rigs'):
                # Check actual registered silhouette corners, including articulated pivots.
                angle=math.radians(s['rotate']);co,si=math.cos(angle),math.sin(angle)
                px,py=s['pivot_x']*s['scale'],s['pivot_y']*s['scale'];corners=[]
                for xx,yy in ((b[0],b[1]),(b[2],b[1]),(b[0],b[3]),(b[2],b[3])):
                    lx=(xx-size[0]/2)*fit;ly=(yy-size[1]/2)*fit
                    corners.append((s['x']+px+co*(lx-px)-si*(ly-py),s['y']+py+si*(lx-px)+co*(ly-py)))
                require(all(-2<=x<=W+2 and -2<=y<=H+2 for x,y in corners),'E_STAGE_BOUNDS',f'frame {frame}, layer {l["id"]}: moving artwork is clipped; reposition its rig or revise the verified hinge')
            w,h=(b[2]-b[0])*fit,(b[3]-b[1])*fit
            # Conservative inscribed box for rotated silhouettes, not a claim about pixel-level occlusion.
            factor=1/(abs(math.cos(math.radians(s['rotate'])))+abs(math.sin(math.radians(s['rotate']))))
            w*=factor;h*=factor
            cx=s['x']+((b[0]+b[2])/2-size[0]/2)*fit;cy=s['y']+((b[1]+b[3])/2-size[1]/2)*fit
            r=(max(0,cx-w/2),max(0,cy-h/2),min(W,cx+w/2),min(H,cy+h/2))
            if r[2]>r[0] and r[3]>r[1]:rects.append(r);used.add(s['asset'])
        if typ=='text':
            size=l.get('size',32)*s['scale']; width=sum(1 if ord(c)>255 else .62 for c in l['text'])*size
            text_area+=width*size*1.25
            centered=l.get('slot')!='title' and l.get('slot')!='subtitle'
            x=s['x']-width/2 if centered else s['x']
            require(x>=0 and x+width<=W and size/2<=s['y']<=H-size/2,'E_TEXT_FIT',f'frame {frame}, layer {l["id"]}; shorten text, do not shrink art')
    require(used.intersection(shot['asset_ids']) and union_area(rects)/(W*H)>=.18,'E_ART',f'frame {frame}: visible foreground art too small/unused')
    require(text_area/(W*H)<=.20,'E_ART',f'frame {frame}: text dominates')
    return {'foreground_fraction':union_area(rects)/(W*H),'text_fraction':text_area/(W*H),'used':sorted(used)}
