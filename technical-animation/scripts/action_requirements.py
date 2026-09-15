"""Derive only required art parts from operations BEFORE image generation."""
from __future__ import annotations
import mechanism_core as mc

# These are supported backend capabilities, not topic-to-object or visual-style presets.
NEEDS={
 'store':{'ports':['entry','inside'],'parts':['body','gate','front'],'states':['empty','full'],'reason':'The object must enter behind the front; occupancy changes only after arrival.'},
 'retrieve':{'ports':['inside','output'],'parts':['body','gate','front'],'states':[],'reason':'A distinct visible copy exits; preserve the original and its identity.'},
 'transfer':{'ports':['entry'],'parts':['body'],'states':[],'reason':'Show contact; use a persistent receipt state when the lesson claims acceptance.'},
 'verify':{'ports':['entry'],'parts':['body','probe'],'states':['checking','pass','fail'],'reason':'The check visibly runs after arrival and produces a supplied teaching outcome.'},
 'replace':{'ports':['entry'],'parts':['body'],'states':[],'reason':'Incoming object arrives before the target changes to a different generated state.'}}

def derive(data):
    plan=mc.plan(data)
    if plan['kind']=='static':return {'status':'planned-not-generated','objects':{},'relations':plan['relations'],'measurement':'No moving parts required merely to export static SVG.'}
    objects={}
    def obj(rid,event,ports,parts,states,reason):
        x=objects.setdefault(rid,{'events':[],'ports':[],'parts':[],'states':[],'reasons':[]})
        for key,values in [('events',[event]),('ports',ports),('parts',parts),('states',states),('reasons',[reason])]:
            for value in values:
                if value not in x[key]:x[key].append(value)
    for a,ev in zip(data['performance']['actions'],plan['events']):
        n=NEEDS[a['kind']]
        obj(a['object'],ev['id'],['contact'],['body'],[], 'Whole silhouette unless a separate part really performs this event.')
        states=list(n['states'])
        if a.get('state'):states.append(a['state'])
        obj(a['target'],ev['id'],n['ports'],n['parts'],states,n['reason'])
    return {'status':'planned-not-generated','objects':objects,
      'measurement':'Measure real anchors and shared registration AFTER inspecting generated images. No default pivots are measured facts.',
      'backend_limit':'gate/front are this 2D adapter\'s supported occlusion strategy, not a requirement that all technical topics be containers.',
      'programmatic':['precise labels','equations and units','paths','state-linked numerical indicators'],
      'keep_whole':'Do not split environment or non-articulated bodies for the sake of a layer-count quota.'}

def brief(data):
    p=derive(data);lines=['\n## Operation-derived art plan — planned, not generated']
    for name,x in p['objects'].items():
        lines.extend([f'### {name}', 'Required by event: '+', '.join(x['events']),
           'Independently needed parts: '+', '.join(x['parts']), 'Contact/entry capabilities: '+', '.join(x['ports']),
           'Generated state variants: '+(', '.join(x['states']) or 'none unless needed by the chosen representation'),
           'Why: '+' '.join(x['reasons'])])
    lines.append(p['measurement']);return '\n'.join(lines)+'\n'
