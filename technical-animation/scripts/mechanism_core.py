"""Typed, bounded teaching-event contract; no eval, model calls or physical simulation.

Planning is asset-free. Resolving binds claimed effects to an independently compiled
performance. Export requires this contract; legacy geometry remains draft-only.
"""
from __future__ import annotations
import copy
import math
import re
import topic_model as m

MILESTONES = {'start', 'contact', 'commit', 'end'}
CHANNELS = {'state', 'contents', 'copy', 'receipts'}
EVENT_FIELDS = {'id', 'action', 'after', 'requires', 'when', 'effects', 'observation'}

def fields(obj, allowed, label):
    m.require(isinstance(obj, dict), 'E_MECHANISM_SCHEMA', label+' must be an object')
    m.require(not set(obj)-set(allowed), 'E_MECHANISM_FIELD', label+': '+','.join(sorted(set(obj)-set(allowed))))

def identifier(value, label):
    m.require(isinstance(value,str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}',value), 'E_EVENT_ID', label)
    return value

def same(a,b):
    # JSON booleans are not numeric values. Sets are represented as sorted unique lists.
    return type(a) is type(b) and a == b

def check_value(spec, value, name):
    kind=spec.get('type')
    if kind=='bool':ok=type(value) is bool
    elif kind=='enum':ok=any(same(value,v) for v in spec.get('values',[]))
    elif kind=='set':
        ok=isinstance(value,list) and all(type(v) is str for v in value) and len(set(value))==len(value)
        ok=ok and all(v in spec.get('values',[]) for v in value)
    elif kind=='number':
        ok=type(value) in (int,float) and math.isfinite(value)
        ok=ok and spec.get('min',-1e12)<=value<=spec.get('max',1e12)
    else:ok=False
    m.require(ok,'E_STATE_TYPE',name+': invalid '+str(kind)+' value '+repr(value))
    return sorted(value) if kind=='set' else value

def predicate(pred, state, specs):
    fields(pred, {'ref','op','value'}, 'predicate')
    ref=pred.get('ref');m.require(isinstance(ref,str) and ref in specs,'E_VARIABLE','predicate: '+str(ref))
    op=pred.get('op');m.require(op in ('eq','ne','contains','empty','gte','lte'),'E_PREDICATE','unsupported predicate '+str(op))
    value=state[ref];want=pred.get('value')
    if op in ('eq','ne'):
        check_value(specs[ref],want,ref);result=same(value,want)
        return result if op=='eq' else not result
    if op in ('contains','empty'):
        m.require(specs[ref]['type']=='set','E_PREDICATE',ref+' is not a set')
        if op=='contains':
            m.require(type(want) is str and want in specs[ref].get('values',[]),'E_STATE_TYPE',ref+' contains invalid member')
            return want in value
        m.require('value' not in pred,'E_PREDICATE','empty takes no value')
        return len(value)==0
    m.require(specs[ref]['type']=='number' and type(want) in (int,float) and math.isfinite(want),'E_PREDICATE',ref+' requires a finite numeric comparator')
    return value>=want if op=='gte' else value<=want

def predicates(items,state,specs,label):
    m.require(isinstance(items,list) and len(items)<=32,'E_PREDICATE',label+' must be a bounded list')
    # Evaluate all items, including false branches, so invalid syntax cannot hide behind short-circuiting.
    return all([predicate(p,state,specs) for p in items])

def plan(data):
    """Validate before any images exist. Events are finite, sequential and declarative."""
    m.require(isinstance(data,dict),'E_MECHANISM_SCHEMA','story must be an object')
    contract=data.get('mechanism')
    m.require(isinstance(contract,dict),'E_MECHANISM_REQUIRED','declare mechanism before artwork; geometry is not a teaching event')
    fields(contract, {'version','kind','variables','events','invariants','relations'}, 'mechanism')
    m.require(type(contract.get('version')) is int and contract['version']==1,'E_MECHANISM_SCHEMA','mechanism.version must be 1')
    if contract.get('kind')=='static':
        entities={e['id'] for e in data.get('concept',{}).get('entities',[])}
        relations=contract.get('relations');m.require(isinstance(relations,list) and 1<=len(relations)<=24,'E_RELATION','static illustration needs explicit relations')
        for r in relations:
            fields(r,{'from','to','relation','observation'},'relation')
            m.require(isinstance(r.get('from'),str) and isinstance(r.get('to'),str) and r.get('from') in entities and r.get('to') in entities and r['from']!=r['to'],'E_RELATION','relations must name distinct real entities')
            m.string(r.get('relation'),'relation',160);m.string(r.get('observation'),'relation.observation',600)
        return {'kind':'static','relations':copy.deepcopy(relations),'events':[],'skipped':[],'final':{}}
    m.require(contract.get('kind')=='discrete','E_MECHANISM_ADAPTER','this release implements discrete events, not general continuous physics')
    specs=contract.get('variables');m.require(isinstance(specs,dict) and 1<=len(specs)<=64,'E_VARIABLE','declare 1..64 typed variables')
    state={}
    for ref,spec in specs.items():
        identifier(ref,'variable ID');fields(spec,{'type','initial','values','unit','min','max','binding'},ref)
        m.require('initial' in spec,'E_VARIABLE',ref+' needs initial state')
        if spec.get('type') in ('enum','set'):
            values=spec.get('values');m.require(isinstance(values,list) and 1<=len(values)<=100,'E_STATE_TYPE',ref+' needs a finite domain')
            if spec.get('type')=='set':m.require(all(type(v) is str for v in values),'E_STATE_TYPE','set domain must contain only string IDs')
            m.require(all(v is None or type(v) in (str,bool,int,float) for v in values),'E_STATE_TYPE','non-scalar enum domain')
            m.require(all(not isinstance(v,float) or math.isfinite(v) for v in values),'E_STATE_TYPE','non-finite domain')
            m.require(len({(type(v).__name__,str(v)) for v in values})==len(values),'E_STATE_TYPE','duplicate domain value')
        if spec.get('type')=='number':
            m.string(spec.get('unit'),'quantity.unit',80)
            for bound in ('min','max'):
                if bound in spec:m.number(spec[bound],ref+'.'+bound,-1e12,1e12)
            m.require(spec.get('min',-1e12)<=spec.get('max',1e12),'E_STATE_TYPE','inverted numeric bounds')
        state[ref]=check_value(spec,spec['initial'],ref)
        if 'binding' in spec:
            b=spec['binding'];fields(b,{'rig','channel'},'binding')
            identifier(b.get('rig'),'binding rig');m.require(isinstance(b.get('channel'),str) and b.get('channel') in CHANNELS,'E_BINDING','unsupported binding channel')
            if b['channel'] in ('contents','receipts'):m.require(spec['type']=='set','E_BINDING','contents/receipts are sets')
            else:m.require(spec['type']=='enum','E_BINDING','state/copy bindings use explicit enum values')
    initial=copy.deepcopy(state)
    invariants=contract.get('invariants',[])
    m.require(predicates(invariants,state,specs,'invariants'),'E_INVARIANT','initial invariant false')
    perf=data.get('performance',{})
    m.require(isinstance(perf,dict),'E_MECHANISM_SCHEMA','performance must be an object')
    actions=perf.get('actions',[]);m.require(isinstance(actions,list) and 1<=len(actions)<=40,'E_EVENT_COVERAGE','declare operations before artwork')
    from perform_core import ACTIONS
    action_ids=[]
    for a in actions:
        m.require(isinstance(a,dict),'E_OPERATION','operation must be an object')
        identifier(a.get('id'),'action ID');m.require(isinstance(a.get('kind'),str) and a.get('kind') in ACTIONS,'E_OPERATION','unsupported operation '+str(a.get('kind')))
        identifier(a.get('object'),'object ID');identifier(a.get('target'),'target ID')
        action_ids.append(a['id'])
    m.require(len(set(action_ids))==len(action_ids),'E_EVENT_ID','duplicate action ID')
    events=contract.get('events');m.require(isinstance(events,list) and len(events)==len(actions),'E_EVENT_COVERAGE','every authored operation needs exactly one event')
    covered=[];seen={};records=[];skipped=[]
    for ev in events:
        fields(ev,EVENT_FIELDS,'event');eid=identifier(ev.get('id'),'event ID')
        m.require(eid not in seen,'E_EVENT_ID','duplicate '+eid)
        aid=ev.get('action');m.require(aid in action_ids and aid not in covered,'E_EVENT_COVERAGE','event action must be real and unique')
        m.require(aid==action_ids[len(covered)],'E_EVENT_COVERAGE','event and operation ordering differ')
        covered.append(aid);m.string(ev.get('observation'),'event.observation',600)
        deps=ev.get('after',[]);m.require(isinstance(deps,list),'E_EVENT_DEPENDENCY','after must be a list')
        enabled=predicates(ev.get('when',[]),state,specs,'when')
        for dep in deps:
            m.require(isinstance(dep,str) and '.' in dep,'E_EVENT_DEPENDENCY','use event.contact/commit/end')
            upstream,mark=dep.rsplit('.',1)
            m.require(upstream in seen and mark in MILESTONES,'E_EVENT_DEPENDENCY','unknown/forward milestone '+dep)
            if enabled:m.require(seen[upstream]['enabled'],'E_EVENT_DEPENDENCY','dependency was skipped: '+dep)
        effects=ev.get('effects');m.require(isinstance(effects,list) and 1<=len(effects)<=32,'E_EFFECT','event needs observable effects')
        before=copy.deepcopy(state);next_state=copy.deepcopy(state);affected=[]
        # Validate every branch's effects. Only enabled branches change state.
        for effect in effects:
            fields(effect,{'ref','op','value'},'effect');ref=effect.get('ref')
            m.require(isinstance(ref,str) and ref in specs,'E_VARIABLE','effect references '+str(ref));m.require(ref not in affected,'E_EFFECT','one effect per variable/event')
            m.require('binding' in specs[ref],'E_BINDING','changed variable needs a visible binding: '+ref)
            op=effect.get('op');value=effect.get('value');old=next_state[ref]
            if op=='set':new=check_value(specs[ref],value,ref)
            elif op in ('add','remove'):
                m.require(specs[ref]['type']=='set' and type(value) is str and value in specs[ref].get('values',[]),'E_STATE_TYPE','set member '+ref)
                if op=='add':new=sorted(set(old)|{value})
                else:
                    if enabled:m.require(value in old,'E_PRECONDITION','cannot remove absent '+value)
                    new=sorted(set(old)-{value})
            else:m.fail('E_EFFECT','supported effects: set/add/remove, not executable expressions')
            if enabled:m.require(not same(old,new),'E_NO_CHANGE',eid+': no observable change to '+ref)
            next_state[ref]=new;affected.append(ref)
        ready=predicates(ev.get('requires',[]),state,specs,'requires')
        if enabled:
            m.require(ready,'E_PRECONDITION',eid+': a required state is false')
            state=next_state
            m.require(predicates(invariants,state,specs,'invariants'),'E_INVARIANT',eid+': invariant false after effects')
        else:skipped.append(eid)
        record={'id':eid,'action':aid,'enabled':enabled,'after':deps,'before':before,'after_state':copy.deepcopy(state),'affected':affected,'observation':ev['observation']}
        seen[eid]=record;records.append(record)
    m.require(any(r['enabled'] for r in records),'E_EVENT_COVERAGE','all events skipped; no mechanism animation to present')
    return {'kind':'discrete','initial':initial,'events':records,'skipped':skipped,'final':copy.deepcopy(state),'variables':copy.deepcopy(specs)}

def production_gate(data):
    mode=data.get('presentation', 'animated' if any(f in data.get('formats',[]) for f in ('html','video')) else 'static')
    m.require(mode in ('animated','static','interactive'),'E_PRESENTATION','unknown presentation')
    m.require(mode!='interactive','E_INTERACTION_ADAPTER','parameter-driven teaching needs a verified domain adapter; playback controls are not teaching interaction')
    p=plan(data)
    if mode=='static':
        m.require(data.get('formats')==['svg'],'E_PRESENTATION','static delivery is SVG; request animated explicitly for video')
        m.require(p['kind']=='static','E_PRESENTATION','static SVG needs structure/relations, not forced motion')
    else:m.require(p['kind']=='discrete' and data.get('performance'),'E_MECHANISM_REQUIRED','animated final requires a typed event contract and executable operations')
    return p

def observed_value(snapshot, binding):
    rid=binding['rig'];channel=binding['channel']
    if channel=='state':return snapshot['states'].get(rid)
    if channel=='contents':return [snapshot['contents'][rid]] if rid in snapshot['contents'] else []
    if channel=='copy':return snapshot['copies'].get(rid)
    return sorted(snapshot.get('receipts',{}).get(rid,[]))

def resolve(data):
    """Link the declarative contract to the actual operation backend; no duplicated animation code."""
    p=plan(data)
    if p['kind']=='static':return copy.deepcopy(data)
    from perform_core import compile_performance,semantic_state
    source=copy.deepcopy(data);by_action={a['id']:a for a in source['performance']['actions']}
    evmap={r['id']:r for r in p['events']};active=[r for r in p['events'] if r['enabled']]
    source['performance']['actions']=[by_action[r['action']] for r in active]
    active_ids={r['action'] for r in active}
    for rec in active:
        a=by_action[rec['action']]
        original=a.get('after',[])
        m.require(isinstance(original,list) and all(type(v) is str for v in original),'E_EVENT_DEPENDENCY','operation after must be a list of action IDs')
        m.require(all(v in active_ids for v in original),'E_EVENT_DEPENDENCY','operation depends on a skipped action')
        a['after']=list(dict.fromkeys(original+[evmap[d.rsplit('.',1)[0]]['action'] for d in rec['after']]))
    scene=compile_performance(source);compiled={e['id']:e for e in scene['compiled_actions']};rigs={r['id']:r for r in scene['compiled_rigs']}
    for ref,spec in p['variables'].items():
        if 'binding' in spec:m.require(spec['binding']['rig'] in rigs,'E_BINDING','unknown bound rig '+spec['binding']['rig'])
    def check_at(expected,frame,label):
        actual=semantic_state(scene,frame)
        for ref,spec in p['variables'].items():
            if 'binding' not in spec:continue
            value=observed_value(actual,spec['binding'])
            m.require(same(value,expected[ref]),'E_MECHANISM_DIVERGENCE',f'{label}: {ref} expected {expected[ref]!r}, operation backend produced {value!r}')
    check_at(p['initial'],0,'initial')
    trace=[]
    for rec in active:
        e=compiled[rec['action']]
        m.require(e['start']<=e['contact']<=e['commit']<e['end'],'E_MILESTONE','outcome precedes contact')
        check_at(rec['before'],e['start'],rec['id']+'.before')
        check_at(rec['after_state'],e['commit'],rec['id']+'.commit')
        check_at(rec['after_state'],e['end']-1,rec['id']+'.after')
        witnesses=[]
        for ref in rec['affected']:
            bind=p['variables'][ref]['binding'];r=rigs[bind['rig']]
            witnesses.append({'ref':ref,'rig':r['id'],'channel':bind['channel'],'layer':r['layer'],'before':rec['before'][ref],'after':rec['after_state'][ref]})
        trace.append({'id':rec['id'],'action':rec['action'],'kind':e['kind'],'start':e['start'],'contact':e['contact'],'commit':e['commit'],'end':e['end'],
                      'before':rec['before'],'after':rec['after_state'],'witnesses':witnesses,'observation':rec['observation']})
    scene['mechanism_trace']=trace;scene['mechanism_skipped']=p['skipped']
    return scene
