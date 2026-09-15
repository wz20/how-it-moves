"""Expected event != drawn layer != visual judgement. Capture each separately.

DOM visibility and pixel contribution are regression floors, not perceptual scores.
Full occlusion is detected by removing a witness and comparing actual rendered pixels.
"""
from __future__ import annotations
import io,json
from pathlib import Path
from PIL import Image,ImageChops
import topic_model as m

VIEWS=('full','labels-only','mechanism-only')

def probes(scene):
    layers={l['id']:l for l in scene['layers']};result=[]
    for event in scene.get('mechanism_trace',[]):
        fs=sorted({event['start'],max(event['start'],event['contact']-1),event['contact'],event['commit']-1,event['commit'],event['end']-1})
        witnesses=[]
        for w in event['witnesses']:
            layer=layers[w['layer']];state=m.layer_state(layer,event['commit'],scene)
            m.require(layer.get('type','image')=='image' and layer.get('purpose') not in ('decoration','narration','camera'),'E_WITNESS','effect cannot be witnessed solely by a paragraph/decoration')
            m.require(state['opacity']>=.5,'E_WITNESS','effect witness hidden at commit: '+w['layer'])
            witnesses.append(dict(w,asset=state['asset']))
        result.append({'id':event['id'],'frames':fs,'start':event['start'],'end':event['end'], 'commit':event['commit'],
                       'observation':event['observation'],'witnesses':witnesses})
    return result


def pending(scene):
    return {'layers':{'technical':'pending','event':'pending','visual':'pending'},
       'events':[dict(p,verdict='pending',findings={'before_after':'','contact_and_consequence':'','labels_only':'','mechanism_only':''},
                      transition_inspected=False) for p in probes(scene)],
       'limits':['DOM is not perceptual understanding','pixel contribution is not aesthetic quality','no audience study inferred']}


def observe_page(page, scene):
    results=[]
    for event in probes(scene):
        page.evaluate('(f)=>window.renderFrame(f)',event['commit'])
        page.evaluate('window.setReviewView("full")')
        full=page.locator('#stage').screenshot(animations='disabled')
        for w in event['witnesses']:
            actual=page.evaluate('''(id)=>{const g=document.getElementById(id);const b=g.getBoundingClientRect();
              const active=[...g.querySelectorAll('[data-variant]')].filter(n=>Number(n.getAttribute('opacity'))>.5);
              return {opacity:Number(g.getAttribute('opacity')),asset:active.map(n=>n.dataset.variant),box:[b.x,b.y,b.width,b.height]};}''',w['layer'])
            m.require(actual['opacity']>=.5 and w['asset'] in actual['asset'],'E_VISUAL_BINDING',event['id']+': actual SVG state differs from event witness')
            page.evaluate('(id)=>document.getElementById(id).style.opacity="0"',w['layer'])
            removed=page.locator('#stage').screenshot(animations='disabled')
            page.evaluate('(id)=>document.getElementById(id).style.opacity=""',w['layer'])
            a=Image.open(io.BytesIO(full)).convert('RGB');b=Image.open(io.BytesIO(removed)).convert('RGB')
            diff=ImageChops.difference(a,b).convert('L');hist=diff.histogram();changed=sum(hist[1:])
            m.require(changed>=16,'E_VISUAL_OCCLUDED',event['id']+': removing witness '+w['layer']+' changes no meaningful pixels; inspect occlusion')
            results.append({'event':event['id'],'frame':event['commit'],'layer':w['layer'],'actual':actual,'changed_pixels_when_removed':changed})
    return results


def check_records(review,scene,root):
    expected=probes(scene);events=review.get('events')
    m.require(isinstance(events,list) and len(events)==len(expected) and {e.get('id') for e in events}=={e['id'] for e in expected},'E_EVENT_REVIEW','every event needs distinct pre/contact/post and ablation review')
    for ev in events:
        m.require(ev.get('verdict')=='approved' and ev.get('transition_inspected') is True,'E_EVENT_REVIEW','inspect continuous event motion, not screenshots alone: '+str(ev.get('id')))
        for k in ('before_after','contact_and_consequence','labels_only','mechanism_only'):
            m.string(ev.get('findings',{}).get(k),'event-review.'+k,2000)
    evidence=review.get('ablation_evidence',[])
    wanted={(v,f) for e in expected for f in e['frames'] for v in ('labels-only','mechanism-only')}
    quality=review.get('quality_layers',{})
    m.require(isinstance(quality,dict) and set(quality)=={'technical','event','visual'} and all(v=='approved' for v in quality.values()),'E_EVENT_REVIEW','three quality layers need independent review')
    if not expected:return
    m.require(isinstance(evidence,list) and {(x.get('view'),x.get('frame')) for x in evidence}==wanted,'E_EVENT_REVIEW','missing ablation captures')
    for e in evidence:
        m.require(m.sha(m.local(root,e.get('path')))==e.get('sha256'),'E_EVENT_REVIEW','altered ablation image')
    obs=review.get('observed_witnesses',[])
    want={(e['id'],w['layer']) for e in expected for w in e['witnesses']}
    m.require({(x.get('event'),x.get('layer')) for x in obs}==want,'E_EVENT_REVIEW','missing actual DOM/pixel witness observations')
    m.require(all(x.get('changed_pixels_when_removed',0)>=16 for x in obs),'E_EVENT_REVIEW','occluded witnesses')
    for value in review.get('quality_layers',{}).values():
        m.require(value=='approved','E_EVENT_REVIEW','quality layers must be reviewed independently')
