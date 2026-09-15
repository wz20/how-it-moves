"""Compile semantic performances into deterministic tracks for arbitrary registered artwork.

No canned prop names, image generation, external calls or real technical execution.
The same compiler output drives pixels, event inspection, SVG and movie export.
"""
from __future__ import annotations
import copy
import math
from typing import Any
import topic_model as m

ACTIONS = {'store': 2.4, 'retrieve': 2.4, 'transfer': 1.6, 'verify': 2.8, 'replace': 2.4}
DEFAULTS = {'store': 4.0, 'retrieve': 4.0, 'transfer': 3.0, 'verify': 4.0, 'replace': 3.5}


def exact_fields(value: Any, allowed: set[str], name: str) -> None:
    m.require(isinstance(value, dict), 'E_SCHEMA', name+' must be an object')
    m.require(not set(value)-allowed, 'E_FIELD', name+': '+','.join(sorted(set(value)-allowed)))


def point(value: Any, field: str) -> list[float]:
    m.require(isinstance(value, list) and len(value)==2, 'E_PORT', field+' requires normalized [x,y]')
    return [m.number(v,field,0,1) for v in value]


def seconds(value: Any, fps: int, name: str) -> int:
    m.number(value,name,0,180)
    return round(value*fps)  # nearest output frame; documented quantization, <= half frame


def rig_map(scene):
    return {r['id']:r for r in scene.get('compiled_rigs',[])}


def local_anchor(layer, rig, normalized, frame, scene):
    s=m.layer_state(layer,frame,scene)
    w,h=rig['artboard']; fit=min(s['width']/w,s['height']/h)
    x=(normalized[0]-.5)*w*fit; y=(normalized[1]-.5)*h*fit
    pivot=layer.get('pivot',[.5,.5])
    px=(pivot[0]-.5)*w*fit; py=(pivot[1]-.5)*h*fit
    angle=math.radians(s['rotate']); c=math.cos(angle);n=math.sin(angle)
    return ((c*(x-px)-n*(y-py)+px)*s['scale'], (n*(x-px)+c*(y-py)+py)*s['scale'])


def port(scene, rig_id, name, frame):
    rigs=rig_map(scene)
    m.require(rig_id in rigs,'E_RIG','unknown '+str(rig_id))
    r=rigs[rig_id]
    m.require(name in r['anchors'],'E_PORT',rig_id+'.'+name)
    layer=next(l for l in scene['layers'] if l['id']==r['layer'])
    s=m.layer_state(layer,frame,scene);offset=local_anchor(layer,r,r['anchors'][name],frame,scene)
    return [s['x']+offset[0],s['y']+offset[1]]


def key(layer, frame, **changes):
    """One canonical key at each integer frame; conflicts are caught at plan level."""
    found=next((k for k in layer.setdefault('keys',[]) if k['frame']==frame),None)
    if found is None:
        found={'frame':frame};layer['keys'].append(found)
    found.update(changes);layer['keys'].sort(key=lambda k:k['frame'])


def image_state(layer, frame, asset):
    keys=layer.setdefault('asset_keys',[])
    found=next((k for k in keys if k['frame']==frame),None)
    if found is not None:found['asset']=asset
    else:keys.append({'frame':frame,'asset':asset});keys.sort(key=lambda k:k['frame'])


def compile_performance(source: dict) -> dict:
    """Resolve the optional performance contract without altering user inputs."""
    scene=copy.deepcopy(source)
    if 'performance' not in source:return scene
    plan=source['performance']
    exact_fields(plan,{'version','rigs','actions','cues'},'performance')
    m.require(type(plan.get('version')) is int and plan['version']==1,'E_SCHEMA','performance.version must be 1')
    fps=source.get('fps'); m.require(type(fps) is int and fps in (30,60),'E_FPS','30/60fps')
    total=seconds(source.get('duration'),fps,'duration')
    m.require(total>=fps,'E_PACING','timeline too short')
    raw_layers=source.get('layers',[]);raw_assets=source.get('assets',[])
    m.require(isinstance(raw_layers,list) and all(isinstance(l,dict) for l in raw_layers),'E_LAYER','layers required')
    m.require(isinstance(raw_assets,list) and all(isinstance(a,dict) for a in raw_assets),'E_ASSET','assets required')
    for l in raw_layers:m.string(l.get('id'),'layer.id',60)
    for asset in raw_assets:m.string(asset.get('id'),'asset.id',60)
    layers={l.get('id'):l for l in scene['layers']}; assets={a.get('id'):a for a in raw_assets}
    m.require(len(layers)==len(raw_layers) and len(assets)==len(raw_assets),'E_ID','duplicate layer/asset')
    rigs=plan.get('rigs',[])
    m.require(isinstance(rigs,list) and 1<=len(rigs)<=20,'E_RIG','supply 1..20 asset rigs')
    ids=set();owned=set()
    for r in rigs:
        exact_fields(r,{'id','layer','artboard','anchors','gate','front','probe','states','initial_state','initial_contents'},'rig')
        rid=m.string(r.get('id'),'rig.id',60);m.require(rid not in ids,'E_ID','duplicate rig');ids.add(rid)
        m.require(isinstance(r.get('layer'),str) and r.get('layer') in layers,'E_RIG','missing body layer for '+rid)
        l=layers[r['layer']]
        m.require(l.get('type','image')=='image' and isinstance(l.get('asset'),str) and l.get('asset') in assets,'E_RIG','body must use generated image')
        artboard=r.get('artboard')
        m.require(isinstance(artboard,list) and len(artboard)==2 and all(type(v) is int and 256<=v<=8192 for v in artboard),
                  'E_REGISTRATION',rid+' must declare the original registered artboard [width,height]')
        anchors=r.get('anchors',{})
        m.require(isinstance(anchors,dict) and anchors,'E_PORT',rid+' requires ports')
        for n,p in anchors.items():m.string(n,'anchor',40);point(p,rid+'.'+n)
        states=r.get('states',{})
        m.require(isinstance(states,dict),'E_STATE_ART',rid+' states must be an object')
        if states:
            m.require(isinstance(r.get('initial_state'),str) and r.get('initial_state') in states,'E_STATE_ART',rid+' initial_state is missing')
            m.require(all(isinstance(v,str) for v in states.values()),'E_STATE_ART','state assets must be IDs')
            m.require(len(set(states.values()))==len(states),'E_STATE_ART','different states need different registered images: '+rid)
            entity=assets[l['asset']].get('entity',l['asset'])
            for n,aid in states.items():
                m.string(n,'state',40)
                m.require(aid in assets and assets[aid].get('entity',aid)==entity,'E_STATE_ART','state identity mismatch: '+rid+'.'+n)
            l['asset']=states[r['initial_state']]
        part_ids=[r['layer']]
        if r.get('gate'):
            gate=r['gate'];exact_fields(gate,{'layer','pivot','open_degrees','open_offset'},rid+'.gate')
            point(gate.get('pivot',[.5,.5]),rid+'.gate.pivot');angle=m.number(gate.get('open_degrees',0),rid+'.gate.open_degrees',-150,150)
            offset=gate.get('open_offset',[0,0]);m.require(isinstance(offset,list) and len(offset)==2,'E_RIG_PART','open_offset is [dx,dy] in registered image units')
            for v in offset:m.number(v,'gate.open_offset',-.6,.6)
            m.require(abs(angle)>=12 or math.hypot(*offset)>=.04,'E_RIG_PART','gate must visibly articulate');part_ids.append(gate.get('layer'))
        for field in ('front','probe'):
            if field in r:part_ids.append(r[field])
        for pid in part_ids:
            m.require(isinstance(pid,str) and pid in layers and layers[pid].get('type','image')=='image','E_RIG_PART',rid+' missing image part '+str(pid))
            m.require(pid not in owned,'E_RIG_PART','a layer belongs to one rig: '+str(pid));owned.add(pid)
            m.require(not layers[pid].get('keys') and not layers[pid].get('asset_keys'),'E_TRACK_CONFLICT',str(pid)+' has hand-written tracks; performance owns these tracks')
            m.require(layers[pid].get('start',0)==0 and layers[pid].get('end',total)==total,'E_TRACK_CONFLICT','bound layers span the full project: '+str(pid))
        # Gate and front use a shared full registration canvas, including transparent margins.
        for pid in ([r['gate']['layer']] if r.get('gate') else [])+([r['front']] if r.get('front') else []):
            for f in ('slot','box','scale','rotate'):
                if f in l:layers[pid][f]=copy.deepcopy(l[f])
                else:layers[pid].pop(f,None)
        for pid in [r['layer']]+([r['front']] if r.get('front') else [])+([r['gate']['layer']] if r.get('gate') else []):layers[pid]['image_size']=r['artboard']
        if r.get('gate'):layers[r['gate']['layer']]['pivot']=r['gate'].get('pivot',[.5,.5])
    scene.pop('performance')
    scene['compiled_rigs']=copy.deepcopy(rigs)
    scene['compiled_actions']=[]
    R=rig_map(scene);states={r['id']:r.get('initial_state') for r in rigs};contents={r['id']:r['initial_contents'] for r in rigs if 'initial_contents' in r}
    for rid,oid in contents.items():m.require(isinstance(oid,str) and oid in R,'E_CAUSAL_STATE',rid+' initial_contents must reference a real object rig')
    # All state images are already registered, so no runtime dependency or regenerated art.
    for l in scene['layers']:
        if l['id'] in owned:
            s=m.layer_state(l,0,scene)
            key(l,0,**{k:s[k] for k in ('x','y','scale','rotate','opacity')})
    cue_list=plan.get('cues',[]);m.require(isinstance(cue_list,list),'E_CUE','cues must be a list')
    cues={}
    for c in cue_list:
        exact_fields(c,{'id','start','end','text'},'cue');cid=m.string(c.get('id'),'cue.id',60)
        m.require(cid not in cues,'E_CUE','duplicate cue ID')
        a=seconds(c.get('start'),fps,cid+'.start');b=seconds(c.get('end'),fps,cid+'.end')
        m.require(0<=a<b<=total,'E_CUE','cue bounds: '+cid)
        if 'text' in c:m.string(c['text'],'cue.text',400)
        cues[cid]=(a,b)
    actions=plan.get('actions');m.require(isinstance(actions,list) and 1<=len(actions)<=40,'E_OPERATION','supply 1..40 operations')
    completed={};cursor=0;shots=[]
    original_positions={rid:port(scene,rid,'contact',0) for rid in R if 'contact' in R[rid]['anchors']}
    # Named operations have deliberately bounded behavior, not universal arbitrary simulation.
    for action in actions:
        exact_fields(action,{'id','kind','object','target','after','duration','cue','caption','consequence','result','state','derived_from'},'action')
        aid=m.string(action.get('id'),'action.id',60);m.require(aid not in completed,'E_ID','duplicate action ID')
        kind=action.get('kind');m.require(isinstance(kind,str) and kind in ACTIONS,'E_OPERATION','supported: '+', '.join(ACTIONS))
        m.string(action.get('caption'),'caption',42);m.string(action.get('consequence'),'consequence',400)
        oid,tid=action.get('object'),action.get('target')
        m.require(isinstance(oid,str) and isinstance(tid,str) and oid in R and tid in R and oid!=tid,'E_RIG','object and target must be different declared rigs')
        obj,target=R[oid],R[tid];ol=layers[obj['layer']];tl=layers[target['layer']]
        m.require('contact' in obj['anchors'],'E_PORT',oid+'.contact')
        deps=action.get('after',[]);m.require(isinstance(deps,list) and all(isinstance(v,str) and v in completed for v in deps),'E_DEPENDENCY','dependencies must reference earlier actions')
        earliest=max([cursor]+[completed[v]['end'] for v in deps])
        if 'cue' in action:
            m.require(isinstance(action['cue'],str) and action['cue'] in cues,'E_CUE','unknown '+str(action['cue']));a,b=cues[action['cue']]
            m.require(a>=earliest,'E_CUE_CONFLICT',aid+' starts before preceding action finishes; re-time this cue, do not speed up the whole movie')
        else:a=earliest;b=a+seconds(action.get('duration',DEFAULTS[kind]),fps,'action.duration')
        m.require(b-a>=math.ceil(ACTIONS[kind]*fps),'E_PACING',aid+' has insufficient contact/response time')
        m.require(b<=total-round(1.5*fps),'E_PACING',aid+' leaves no final reading hold; increase duration or shorten content')
        def at(u):return a+round((b-a)*u)
        e={'id':aid,'kind':kind,'object':oid,'target':tid,'start':a,'end':b,'contact':at(.32 if kind=='store' else .56 if kind=='retrieve' else .35 if kind=='verify' else .65),
           'commit':at(.68 if kind=='store' else .82 if kind=='retrieve' else .80),'after':deps,'caption':action['caption'],'consequence':action['consequence']}
        e['critical_frames']=sorted({a,at(.15),e['contact']-1,e['contact'],e['commit']-1,e['commit'],b-1})
        required_ports={'store':['entry','inside'],'retrieve':['inside','output'],'verify':['entry'],'replace':['entry'],'transfer':['entry']}[kind]
        for name in required_ports:m.require(name in target['anchors'],'E_PORT',tid+'.'+name)
        if kind in ('store','retrieve'):
            for part in ('gate','front'):m.require(target.get(part),'E_RIG_PART',tid+' needs a generated '+part+' layer; not a CSS replacement')
        if kind=='verify':m.require(target.get('probe'),'E_RIG_PART',tid+' needs a registered moving probe')
        # Freeze previous operation's state across any narration gap.
        for pid in owned:
            l=layers[pid];s=m.layer_state(l,max(0,a-1),scene)
            key(l,a,**{k:s[k] for k in ('x','y','scale','rotate','opacity')})
        def place(frame,xy,opacity=None,scale=None):
            if scale is not None:key(ol,frame,scale=scale)
            offset=local_anchor(ol,obj,obj['anchors']['contact'],frame,scene)
            args={'x':xy[0]-offset[0],'y':xy[1]-offset[1],'ease':'linear'}
            if opacity is not None:args['opacity']=opacity
            key(ol,frame,**args)
        def state_change(frame,name):
            m.require(isinstance(name,str) and name in target.get('states',{}),'E_STATE_ART',tid+' needs state '+name)
            image_state(tl,frame,target['states'][name])
        def gate_animation():
            g=target['gate'];l=layers[g['layer']];st=m.layer_state(l,a,scene);base=st['rotate'];rotation=g.get('open_degrees',0)
            dx,dy=g.get('open_offset',[0,0]);aw,ah=target['artboard'];fit=min(st['width']/aw,st['height']/ah)*st['scale'];angle=math.radians(base)
            ox=math.cos(angle)*dx*aw*fit-math.sin(angle)*dy*ah*fit;oy=math.sin(angle)*dx*aw*fit+math.cos(angle)*dy*ah*fit
            key(l,a,x=st['x'],y=st['y'],rotate=base)
            key(l,at(.15),x=st['x']+ox,y=st['y']+oy,rotate=base+rotation)
            key(l,at(.83),x=st['x']+ox,y=st['y']+oy,rotate=base+rotation)
            key(l,b-1,x=st['x'],y=st['y'],rotate=base)
        before=states.get(tid)
        if kind=='store':
            m.require(tid not in contents and before=='empty','E_CAUSAL_STATE',tid+' is not empty')
            m.require('full' in target.get('states',{}),'E_STATE_ART',tid+' requires full state')
            gate_animation();place(at(.15),port(scene,oid,'contact',a));place(e['contact'],port(scene,tid,'entry',e['contact']))
            place(at(.62),port(scene,tid,'inside',at(.62)));key(ol,e['commit']-1,opacity=1);key(ol,e['commit'],opacity=0)
            state_change(e['commit'],'full');states[tid]='full';contents[tid]=oid;e['new_state']='full';e['stored']=oid
        elif kind=='retrieve':
            original=action.get('derived_from')
            m.require(isinstance(original,str) and original in R and original!=oid and contents.get(tid)==original,'E_CAUSAL_STATE','retrieval needs a stored source and a distinct derived copy')
            m.require(m.layer_state(ol,a,scene)['opacity']==0,'E_CAUSAL_STATE','derived copy must initially be hidden')
            gate_animation();place(a,port(scene,tid,'inside',a),opacity=0)
            place(at(.20),port(scene,tid,'inside',at(.20)),opacity=0);place(at(.22),port(scene,tid,'inside',at(.22)),opacity=1)
            place(e['contact'],port(scene,tid,'output',e['contact']));place(e['commit'],original_positions[oid])
            e['derived_from']=original;e['source_preserved']=True
        else:
            start_xy=port(scene,oid,'contact',a);place(at(.12),start_xy)
            place(e['contact'],port(scene,tid,'entry',e['contact']))
            if kind=='verify':
                result=action.get('result');m.require(result in ('pass','fail'),'E_STATE_CHANGE','verify.result must be pass/fail (simulated, not executed)')
                state_change(e['contact'],'checking');state_change(e['commit'],result);states[tid]=result;e['new_state']=result
                l=layers[target['probe']];st=m.layer_state(l,a,scene)
                key(l,e['contact'],opacity=0);key(l,e['contact']+1,opacity=1)
                key(l,at(.50),x=st['x']-scene['width']*.03,rotate=-12,opacity=1)
                key(l,at(.70),x=st['x']+scene['width']*.03,rotate=12)
                key(l,e['commit'],x=st['x'],rotate=0,opacity=0)
                place(b-1,start_xy)
            elif kind=='replace':
                name=action.get('state');m.require(name!=before,'E_STATE_CHANGE','replacement must change a visible state')
                state_change(e['commit'],name);states[tid]=name;e['new_state']=name
                key(ol,e['commit']-1,opacity=1);key(ol,e['commit'],opacity=0)
            else:
                if 'state' in action:
                    name=action['state'];m.require(name!=before,'E_STATE_CHANGE','receipt state must change')
                    state_change(e['commit'],name);states[tid]=name;e['new_state']=name;e['received']=oid
                # Receiver responds only after delivery. Explicit scale pulse, no autonomous idle loop.
                response_parts=[target['layer']]+([target['front']] if target.get('front') else [])+([target['gate']['layer']] if target.get('gate') else [])
                for pid in response_parts:
                    part=layers[pid];st=m.layer_state(part,a,scene)
                    key(part,e['contact'],scale=st['scale']);key(part,e['commit'],scale=st['scale']*1.045);key(part,b-1,scale=st['scale'])
        # Guarantee a stable endpoint before subsequent actions/cues.
        for pid in owned:
            l=layers[pid];s=m.layer_state(l,b-1,scene);key(l,b-1,**{k:s[k] for k in ('x','y','scale','rotate','opacity')})
        involved=list(dict.fromkeys([assets[layers[R[oid]['layer']]['asset']].get('entity',layers[R[oid]['layer']]['asset']), assets[layers[R[tid]['layer']]['asset']].get('entity',layers[R[tid]['layer']]['asset'])]))
        shot_assets=[asset['id'] for asset in raw_assets if asset.get('entity',asset['id']) in involved]
        if a>cursor:
            shots.append(dict(id=aid+'-cue-wait',start=cursor,end=a,caption=action['caption'],action='resolve',change='Hold the same objects for the supplied narration cue.',asset_ids=shot_assets,critical_frames=[]))
        shots.append(dict(id=aid,start=a,end=b,caption=action['caption'],action={'transfer':'route','replace':'update'}.get(kind,kind),change=action['consequence'],asset_ids=shot_assets,critical_frames=e['critical_frames']))
        scene['compiled_actions'].append(e);completed[aid]=e;cursor=b
    # Foreground masks are physical registered artwork, not rectangle clips. All tokens sit behind them.
    foreground=[r['front'] for r in rigs if r.get('front')];gates=[r['gate']['layer'] for r in rigs if r.get('gate')]
    foreground=list(dict.fromkeys(foreground+gates))
    scene['layers']=[l for l in scene['layers'] if l['id'] not in foreground]+[layers[n] for n in foreground]
    if cursor<total:
        last=shots[-1];shots.append(dict(id='performance-hold',start=cursor,end=total,caption=last['caption'],action='resolve',
                     change='Finished; preserve the final state for reading.',asset_ids=last['asset_ids'],critical_frames=[]))
    scene['shots']=shots
    scene['performance_initial']={'states':{r['id']:r.get('initial_state') for r in rigs},'contents':{r['id']:r['initial_contents'] for r in rigs if 'initial_contents' in r}}
    scene['cue_spans']=cue_list
    return scene


def semantic_state(scene, frame):
    """Derived from compiled events. No simulation history, provider execution or hidden mutable state."""
    initial=scene.get('performance_initial',{});states=dict(initial.get('states',{}));contents=dict(initial.get('contents',{}));copies={};receipts={};active=[]
    for e in scene.get('compiled_actions',[]):
        if e['start']<=frame<e['end']:active.append(e['id'])
        if e['kind']=='verify' and e['contact']<=frame<e['commit']:states[e['target']]='checking'
        if frame>=e['commit']:
            if 'new_state' in e:states[e['target']]=e['new_state']
            if 'received' in e:receipts.setdefault(e['target'],[]).append(e['received'])
            if e['kind']=='store':contents[e['target']]=e['object']
            if e['kind']=='retrieve':copies[e['object']]=e['derived_from']
    events=scene.get('compiled_actions',[])
    return dict(frame=frame,states=states,contents=contents,copies=copies,receipts=receipts,active=active,stopped=bool(events and frame>=events[-1]['end']))


def validate_registration(scene, meta):
    layers={l['id']:l for l in scene['layers']}
    for r in scene.get('compiled_rigs',[]):
        body=layers[r['layer']];ids=[body['asset']]+list(r.get('states',{}).values())
        for name in ([r['front']] if r.get('front') else [])+([r['gate']['layer']] if r.get('gate') else []):ids.append(layers[name]['asset'])
        for aid in ids:
            m.require(meta[aid]['size']==r['artboard'],'E_REGISTRATION',r['id']+'/'+aid+' has mismatched registered dimensions; normalize all related layers together')
