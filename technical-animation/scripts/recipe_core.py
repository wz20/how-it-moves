"""Strict content-to-events compiler. Standard library only; no execution of model code.
All recipe animations, state checks and captions use this single compiled contract.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import unicodedata
from typing import Any

VERSION = '0.2.0'
RECIPES = {
    'feedback-retry': {'minimum': 10, 'default': 12, 'name': '反馈与重试'},
    'retrieval-evidence': {'minimum': 12, 'default': 12, 'name': '检索与证据汇入'},
    'cache-aside': {'minimum': 12, 'default': 14, 'name': '缓存未命中与命中'},
}
COMMON = {'schema_version','recipe','title','takeaway','duration','fps','style','aspect','audio','content'}
FIELDS = {
 'feedback-retry': {'goal':14,'action':4,'failure':4,'adjustment':4,'success':4,'before':11,'after':11,'decision':10},
 'retrieval-evidence': {'question':16,'answer':24},
 'cache-aside': {'request':8,'key':10,'value':7},
}
SOURCES = {
 'feedback-retry': [{'url':'https://www.anthropic.com/engineering/building-effective-agents','claim':'Tool feedback informs subsequent action; stopping conditions matter.'}],
 'retrieval-evidence': [{'url':'https://arxiv.org/abs/2005.11401','claim':'Retrieval supplies non-parametric evidence to generation. This clip illustrates inference, not training.'}],
 'cache-aside': [{'url':'https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside','claim':'Read cache; on miss read store and populate cache. Hit can avoid another store read.'}],
}

def visual_units(text: str) -> float:
    return sum(1 if unicodedata.east_asian_width(c) in ('W','F') else .6 for c in text)

def validate_spec(spec: Any) -> list[dict[str,str]]:
    errors=[]
    def err(code,field,message,hint):errors.append(dict(code=code,field=field,message=message,hint=hint))
    def keys(obj,allowed,path):
        for k in obj:
            if k not in allowed:err('E_UNKNOWN',f'{path}.{k}', '不支持的字段 / Unknown field', '删除该字段。坐标、时间和动作由配方管理。')
    def text(obj,key,budget,path='content'):
        v=obj.get(key)
        if not isinstance(v,str) or not v.strip() or any(unicodedata.category(c).startswith('C') for c in v) or visual_units(v)>budget:
            err('E_TEXT',f'{path}.{key}',f'需要非空单行文字，视觉宽度不得超过 {budget} 个汉字单位', '缩短文案；不要使用换行、控制字符或把整段口播放进标签。')
    if not isinstance(spec,dict):
        err('E_TYPE','$','输入必须是 JSON object','复制 recipes/ 中的一份完整示例再修改。');return errors
    keys(spec,COMMON,'$')
    if spec.get('schema_version') != 1 or isinstance(spec.get('schema_version'),bool):err('E_VERSION','schema_version','仅支持 schema_version=1','设为整数 1。')
    r=spec.get('recipe')
    if not isinstance(r,str) or r not in RECIPES:
        err('E_RECIPE','recipe','未知机制配方','请选择 feedback-retry / retrieval-evidence / cache-aside；不匹配的主题转高级模式。');return errors
    text(spec,'title',24,'$');text(spec,'takeaway',28,'$')
    duration=spec.get('duration',RECIPES[r]['default']);fps=spec.get('fps',60)
    number=isinstance(duration,(int,float)) and not isinstance(duration,bool) and math.isfinite(duration)
    if not number:err('E_NUMBER','duration','时长必须是有限数字','使用该配方默认时长，不要使用布尔值或 NaN。')
    elif not RECIPES[r]['minimum']<=duration<=40:err('E_DURATION','duration',f'该配方支持 {RECIPES[r]["minimum"]}–40 秒','减少内容或增加时长；不能压缩到无法阅读。')
    if not isinstance(fps,int) or isinstance(fps,bool) or fps not in (30,60):err('E_FPS','fps','仅支持整数 30 或 60','建议使用 60fps。')
    elif number and abs(duration*fps-round(duration*fps))>1e-7:err('E_DURATION','duration','duration × fps 必须是整数帧','使用整数秒或完整帧边界。')
    for key,want,code in [('style','comic-lab','E_STYLE'),('aspect','16:9','E_ASPECT'),('audio','none','E_AUDIO')]:
        if spec.get(key,want)!=want:err(code,key,f'配方模式目前仅支持 {want}','明确切换高级模式；不会偷偷忽略或拉伸这个要求。')
    c=spec.get('content')
    if not isinstance(c,dict):err('E_TYPE','content','content 必须是 object','复制所选配方示例的 content。');return errors
    allowed=set(FIELDS[r])|({'documents','citations'} if r=='retrieval-evidence' else set())
    keys(c,allowed,'content')
    for k,budget in FIELDS[r].items():text(c,k,budget)
    if r=='feedback-retry':
        if isinstance(c.get('before'),str) and c.get('before')==c.get('after'):err('E_NO_CHANGE','content.after','修改前后相同','填写真实的状态变化；不要把无修改画成已修复。')
        if isinstance(c.get('failure'),str) and c.get('failure')==c.get('success'):err('E_AMBIGUOUS','content.success','失败与成功必须可以区分','使用不同的短文字标签。')
    if r=='retrieval-evidence':
        docs=c.get('documents');cites=c.get('citations')
        if not isinstance(docs,list) or not 2<=len(docs)<=3:
            err('E_TYPE','content.documents','需要 2–3 个文档对象','保留两或三个代表性片段；不要塞入完整文档。')
        else:
            ids=[];selected=[]
            for i,d in enumerate(docs):
                path=f'content.documents[{i}]'
                if not isinstance(d,dict):err('E_TYPE',path,'文档必须是 object','使用 id/text/selected 三字段。');continue
                keys(d,{'id','text','selected'},path);text(d,'id',4,path);text(d,'text',17,path)
                did=d.get('id')
                if isinstance(did,str):
                    if did in ids:err('E_DUPLICATE',path+'.id','文档 ID 重复','每个文档使用唯一 ID，如 D1、D2、D3。')
                    ids.append(did)
                if not isinstance(d.get('selected'),bool):err('E_TYPE',path+'.selected','selected 必须是布尔值','使用 true / false，不要写字符串 yes。')
                elif d['selected'] and isinstance(did,str):selected.append(did)
            if not selected or len(selected)==len(docs):err('E_EVIDENCE','content.documents','必须选中至少一份，并保留一份未命中文档','显式展示选择；不要默认所有检索结果都相关。')
            if isinstance(cites,list) and all(isinstance(x,str) for x in cites):
                if not cites or len(set(cites))!=len(cites) or any(x not in selected for x in cites):err('E_CITATION','content.citations','引用必须唯一且属于已检索片段','只引用 selected=true 的文档 ID。')
        if not isinstance(cites,list) or not cites or not all(isinstance(x,str) for x in cites):err('E_TYPE','content.citations','citations 必须是非空 ID 字符串数组','例如 ["D1", "D3"]。')
    return errors

def normalized(spec: dict) -> dict:
    s=copy.deepcopy(spec);r=s['recipe']
    for k,v in {'duration':RECIPES[r]['default'],'fps':60,'style':'comic-lab','aspect':'16:9','audio':'none'}.items():s.setdefault(k,v)
    return s

def digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def _steps(r,c):
    # id, kind, actor, target, packet label, relative duration, arrival effects, caption
    if r=='feedback-retry':
        return [
          ('goal','goal','user','model',c['goal'],.9,{},'目标：'+c['goal']),
          ('test1','call','model','tool',c['action'],.8,{},'模型发出调用，工具接收'),
          ('run1','execute','tool',None,'执行',.65,{'test_runs':1,'tool_result':'fail'},'工具正在执行第一次测试'),
          ('fail','result','tool','model',c['failure'],.9,{'feedback_received':True,'last_feedback':'fail'},'失败结果返回上下文'),
          ('decide1','decision','model',None,'检查反馈',.85,{'decision':'repair'},c['decision']),
          ('patch','call','model','tool',c['adjustment'],.8,{},'根据反馈发出修改指令'),
          ('apply','execute','tool',None,'应用修改',.6,{'code_changed':True,'tool_result':'patched'},'代码发生变化，还需要验证'),
          ('test2','call','model','tool',c['action'],.75,{},'再次调用，验证修改是否有效'),
          ('run2','execute','tool',None,'验证',.6,{'test_runs':2,'tool_result':'pass'},'工具重新执行测试'),
          ('pass','result','tool','model',c['success'],.85,{'last_feedback':'pass'},'成功结果返回后才能决定结束'),
          ('decide2','decision','model',None,'满足目标',.65,{'decision':'stop'},'目标达成，停止重试'),
        ]
    if r=='retrieval-evidence':
        return [
          ('question','goal','user','retriever',c['question'],1.0,{},'问题先变成检索请求'),
          ('query','call','user','retriever','QUERY',1.0,{},'查询进入检索器'),
          ('search','execute','retriever',None,'检索',1.1,{'retrieved':True},'查找相关片段，不是复制整个库'),
          ('select','decision','retriever',None,'选择片段',1.1,{'selected_ids':[d['id'] for d in c['documents'] if d['selected']]},'只选择相关证据'),
          ('evidence','result','retriever','model','EVIDENCE',1.25,{'context_ready':True},'问题与证据一起进入模型上下文'),
          ('generate','execute','model',None,'生成回答',1.25,{'answer_ready':True},'模型依据检索到的上下文生成'),
          ('answer','result','model','user','ANSWER',1.15,{'delivered':True},'回答带引用，方便回查来源'),
        ]
    return [
        ('request1','call','user','cache','GET',.85,{'requests':1},'第一次读取：先查缓存'),
        ('lookup1','execute','cache',None,'查缓存',.75,{'cache_result':'miss'},'检查缓存里是否有这条数据'),
        ('miss','result','cache','user','MISS',.8,{'miss_received':True},'未命中结果返回应用'),
        ('origin','call','user','database','GET',.85,{},'应用回源，读取数据库'),
        ('read','execute','database',None,'读取',.7,{'db_reads':1},'数据库提供原始数据'),
        ('data','result','database','user','DATA',.85,{'has_value':True},'数据返回应用'),
        ('fill','call','user','cache','SET',.85,{'cache_filled':True},'应用把数据写入缓存'),
        ('respond1','execute','user',None,'返回用户',.7,{'responses':1},'本次请求得到结果'),
        ('request2','call','user','cache','GET',.85,{'requests':2},'相同数据，第二次再读取'),
        ('lookup2','execute','cache',None,'查缓存',.65,{'cache_result':'hit'},'检查相同键，准备返回缓存值'),
        ('hit','result','cache','user','HIT',.85,{'responses':2},'直接返回；数据库只读取一次'),
    ]

def compile_recipe(spec: dict) -> dict:
    errors=validate_spec(spec)
    if errors:raise ValueError(json.dumps(errors,ensure_ascii=False))
    s=normalized(spec);r=s['recipe'];fps=s['fps'];n=round(s['duration']*fps);hold=round(2*fps)
    steps=_steps(r,s['content']);total=sum(x[5] for x in steps);events=[];acc=0;start=0;cause=None
    for item in steps:
        eid,kind,actor,target,label,weight,effect,caption=item;acc+=weight
        end=round((n-hold)*acc/total)
        e=dict(id=eid,kind=kind,actor=actor,label=label,start_frame=start,end_frame=end,start=start/fps,end=end/fps,effect=effect,caption=caption)
        if target:e['target']=target
        if cause:e['caused_by']=cause
        events.append(e);start=end;cause=eid
    events.append(dict(id='done',kind='stop',actor='model' if r!='cache-aside' else 'user',label='完成',start_frame=n-hold,end_frame=n,start=(n-hold)/fps,end=n/fps,caused_by=cause,effect={'stopped':True},caption=s['takeaway']))
    return dict(title=s['title'],takeaway=s['takeaway'],width=1920,height=1080,fps=fps,duration=n/fps,entry='index.html',audio='none',requires_feedback=r=='feedback-retry',ready_for_render=True,style=s['style'],recipe=r,compiler_version=VERSION,input_spec=s,spec_sha256=digest(s),content=s['content'],truth='固定机制示意，非实时 Agent / 检索 / 数据库运行；示例内容是虚构教学数据。',events=events,sources=copy.deepcopy(SOURCES[r]),assets=[dict(path='runtime/rigs.mjs',origin='original procedural vector rig',license='MIT',status='approved-for-demo',used=True)])

def state_at_frame(project: dict, frame: int) -> dict:
    n=round(project['fps']*project['duration']);f=max(0,min(n-1,int(frame)))
    state={'frame':f,'stopped':False,'feedback_received':False,'code_changed':False,'test_runs':0,'db_reads':0,'responses':0,'cache_filled':False,'context_ready':False,'selected_ids':[]}
    for e in project['events']:
        if f>=e['end_frame']:state.update(copy.deepcopy(e.get('effect',{})))
        if e['start_frame']<=f<e['end_frame']:
            state.update(active_event=e['id'],active_kind=e['kind'],caption=e['caption'])
            # STOP is an interval, beginning only after the prior decision completed.
            if e['kind']=='stop':state['stopped']=True
    return state

def validate_compiled(project: Any) -> list[dict[str,str]]:
    try:
        expected=compile_recipe(project['input_spec'])
        if project==expected:return []
    except (KeyError,ValueError,TypeError):pass
    return [dict(code='E_CONTRACT',field='project.json',message='生成合同已改变，或不匹配输入配方',hint='只编辑 recipe.json，然后重新 build 到新目录；不要修改事件时间或运行时代码。')]
