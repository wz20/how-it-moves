/** Content-driven illustrated scenes; time is a pure function of the compiled event contract. */
import {clamp,lerp,smooth,inv} from './motion.mjs';
import {path,packet,arrowHead} from './drawing.mjs';
import {robot} from './rigs.mjs';
import {stateAtFrame,activeEvent,eventProgress} from './recipe-state.mjs';
import {C,round,line,ellipse,dots,check,cross,label,ink,wrap,at,shadow,gear,sheet,clipboard,notebook,terminal,archive,binder,press,kiosk,cacheDrawer,vault} from './studio-art.mjs';
export function visualState(spec,frame){
 const s=stateAtFrame(spec,frame),e=activeEvent(spec,s.frame);
 return {...s,presentation:'illustrated-studio',artAssets:spec.art.assets,active:e.id,progress:eventProgress(e,s.frame),packetCount:['call','result','goal'].includes(e.kind)?1:0};
}
function windowed(f,a,b,r){return smooth(inv(f,a,a+r))*(1-smooth(inv(f,b-r,b)))}
export function drawFrame(ctx,spec,frame){
 const s=visualState(spec,frame),f=s.frame,t=f/spec.fps,c=spec.input_spec.content;
 const E=Object.fromEntries(spec.events.map(e=>[e.id,e]));const e=E[s.active],u=s.progress;
 const active=(id)=>s.active===id,done=(id)=>f>=E[id].end_frame;
 ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;ctx.artIssues=[];
 const theme=spec.recipe==='feedback-retry'?C.orange:spec.recipe==='retrieval-evidence'?C.purple:C.teal;
 ctx.fillStyle=C.paper;ctx.fillRect(0,0,1920,1080);
 dots(ctx,12,12,1900,1050,{step:30,r:.65,alpha:.12});
 ellipse(ctx,990,668,837,254,'#D3DFC225');
 ink(ctx,'HOW IT MOVES',72,57,25,C.ink,{mono:true});
 const number={'feedback-retry':'01  /  AGENT','retrieval-evidence':'02  /  RAG','cache-aside':'03  /  CACHE'}[spec.recipe];
 ink(ctx,number,1848,57,24,C.muted,{mono:true,align:'right'});line(ctx,[[72,101],[1848,101]],C.ink,2);
 ink(ctx,spec.title,78,170,61,C.ink,{width:1760});line(ctx,[[81,226],[970,226]],theme,8);
 ctx.save();ctx.beginPath();ctx.rect(55,257,1810,675);ctx.clip();
 if(spec.recipe==='feedback-retry')agent();else if(spec.recipe==='retrieval-evidence')rag();else cache();
 ctx.restore();
 round(ctx,78,934,1764,85,20,C.ink,null);
 ink(ctx,s.stopped?spec.input_spec.takeaway:e.caption,960,976,38,s.stopped?C.yellow:C.cream,{align:'center',width:1690});
 line(ctx,[[82,1032],[82+1753*(f/(spec.duration*spec.fps-1)),1032]],theme,3);
 const truth=spec.recipe==='cache-aside'?'同一键 · 未过期/未失效 · 非性能测试':spec.recipe==='retrieval-evidence'?'虚构教学资料 · 非训练 · 引用仍需核验':'机制示意 · 非真实 Agent 录屏';
 ink(ctx,truth,1838,1053,21,C.muted,{align:'right',weight:500});
 s.layoutIssues=ctx.artIssues;return s;
 function flow(points,eventId,color,caption='',size=1){
  const ev=E[eventId];if(f<ev.start_frame)return;
  path(ctx,points,{color,width:5,progress:smooth(inv(f,ev.start_frame,ev.start_frame+spec.fps*.3))});
  arrowHead(ctx,points[3][0],points[3][1],Math.atan2(points[3][1]-points[2][1],points[3][0]-points[2][0]),color,12);
  packet(ctx,points,t,ev.start,ev.end,{str:caption||ev.label,color,size});
 }
 function agent(){
  // Original full-size rig and extruded machine remain the same objects in every shot.
  const focus1=windowed(f,E.run1.start_frame,E.fail.start_frame+spec.fps*.15,spec.fps*.45);
  const focus2=windowed(f,E.apply.start_frame,E.test2.end_frame,spec.fps*.45);
  const z=Math.max(focus1,focus2);ctx.save();ctx.translate(960,640);ctx.scale(1+.06*z,1+.06*z);ctx.translate(-960,-640);
  const reach=active('test1')||active('patch')||active('test2')?Math.sin(u*Math.PI):0;
  const thought=active('decide1')?Math.sin(u*Math.PI):0;
  at(ctx,590,655,1.1,()=>robot(ctx,0,0,s.stopped?spec.duration-2:t,{reach,think:thought,look:active('fail')?-1:1,recoil:active('fail')?Math.sin(u*Math.PI)*.7:0,success:s.last_feedback==='pass'?1:0}));
  clipboard(ctx,216,482,{goal:c.goal,done:s.stopped});
  notebook(ctx,364,790,{feedback:s.last_feedback==='pass'?c.success:s.feedback_received?c.failure:'',state:s.last_feedback==='pass'?'pass':s.feedback_received?'fail':'idle'});
  const toolState=active('apply')?'patching':s.tool_result==='patched'?'patch':s.tool_result==='pass'?'pass':s.tool_result==='fail'&&!active('run2')?'fail':'idle';
  at(ctx,1470,647,1.04,()=>terminal(ctx,0,0,t,c,{working:active('run1')||active('run2'),patched:s.code_changed,state:toolState,progress:u}));
  const out=[[838,491],[958,309],[1260,296],[1386,441]];
  const back=[[1346,846],[1240,920],[880,881],[756,759]];
  const callId=f<E.patch.start_frame?'test1':f<E.test2.start_frame?'patch':'test2';
  if(f>=E.test1.start_frame){flow(out,callId,C.orange);ink(ctx,'调用',1093,307,26,C.muted,{align:'center'})}
  if(f>=E.fail.start_frame){flow(back,f<E.pass.start_frame?'fail':'pass',s.last_feedback==='pass'||f>=E.pass.start_frame?C.teal:C.red);ink(ctx,'工具反馈',1060,886,25,C.muted,{align:'center'})}
  if(active('decide1'))label(ctx,c.decision,929,559,{fill:C.yellow,size:27,angle:-.05});
  if(active('apply'))label(ctx,c.adjustment,1248,417,{fill:C.yellow,size:30,angle:-.07});
  if(s.stopped)label(ctx,'完成 ✓',1066,618,{fill:C.teal,size:42,height:70,angle:-.04});
  label(ctx,'LLM · 决定下一步',590,881,{fill:C.orange,size:28,height:50});
  label(ctx,'工具 · 执行与验证',1470,881,{fill:C.teal,size:28,height:48});
  ctx.restore();
 }
 function rag(){
  const docs=c.documents,sel=docs.filter(d=>d.selected);
  const focus=windowed(f,E.search.start_frame,E.evidence.start_frame,spec.fps*.45);
  ctx.save();ctx.translate(960,625);ctx.scale(1+.035*focus,1+.035*focus);ctx.translate(-960,-625);
  const arc=[[410,334],[231,328],[179,358],[225,419]];
  if(active('query'))flow(arc,'query',C.orange,'QUERY',.72);
  round(ctx,116,275,588,67,15,C.cream,C.ink,4,5);ink(ctx,'Q',144,310,32,C.orange,{mono:true});ink(ctx,c.question,195,310,30,C.ink,{width:478});
  const scan=active('search')?Math.max(.001,u):0;
  at(ctx,354,635,.93,()=>archive(ctx,0,0,t,docs,{scan,selected:done('select')}));
  // Evidence is copied out; the original binders never disappear from the archive.
  const acquired=done('evidence')?sel:active('evidence')?sel.slice(0,Math.floor(u*sel.length)):[];
  at(ctx,984,643,.95,()=>binder(ctx,0,0,{question:c.question,docs:acquired}));
  at(ctx,1585,616,1.0,()=>press(ctx,0,0,t,{working:active('generate'),ready:s.answer_ready,progress:u,answer:c.answer,citations:c.citations}));
  if(active('select')){
   docs.forEach((d,i)=>{if(d.selected)label(ctx,d.id+' ✓',226+i*126,402,{fill:C.yellow,size:26,height:45,angle:(i-1)*.025})});
  }
  if(f>=E.evidence.start_frame){
   const p=[[537,461],[635,338],[781,370],[915,494]];
   path(ctx,p,{color:C.orange,width:5,progress:smooth(inv(f,E.evidence.start_frame,E.evidence.start_frame+spec.fps*.3))});
   ink(ctx,'只复制相关片段',738,359,27,C.muted,{align:'center'});
   if(active('evidence'))sel.forEach((d,i)=>{
    const a=i/sel.length,b=(i+1)/sel.length,pu=inv(u,a,b);
    if(u>=a&&u<b){const x=lerp(492,1099,smooth(pu)),y=lerp(488,562,smooth(pu))-Math.sin(pu*Math.PI)*134;
     sheet(ctx,x,y,191,187,{id:d.id,lines:[d.text],accent:i?C.orange:C.teal,angle:Math.sin(pu*Math.PI)*-.13});}
   });
  }
  if(s.context_ready){
   const p=[[1207,568],[1270,532],[1310,532],[1421,558]];path(ctx,p,{color:C.purple,width:5});
   if(active('generate'))packet(ctx,p,t,E.generate.start,E.generate.start+(E.generate.end-E.generate.start)*.35,{str:'CONTEXT',color:C.purple,size:.78});
  }
  if(active('answer')||s.delivered){
   label(ctx,'有出处的回答',1580,355,{fill:C.teal,size:32,height:55,angle:-.035});
   
  }
  label(ctx,'检索 · 不是全库搬运',353,897,{fill:C.teal,size:27,height:44});
  label(ctx,'上下文 · 不是训练',986,867,{fill:C.yellow,size:27,height:44});
  label(ctx,'LLM · 依据证据生成',1585,887,{fill:C.purple,size:26,height:44});
  ctx.restore();
 }
 function cache(){
  const q=E.lookup1,fill=E.fill,second=E.lookup2;
  let opening=0;
  if(f>=q.start_frame&&f<E.origin.end_frame)opening=windowed(f,q.start_frame,E.origin.end_frame,spec.fps*.45);
  if(f>=fill.start_frame&&f<E.request2.start_frame)opening=windowed(f,fill.start_frame,E.request2.start_frame,spec.fps*.45);
  if(f>=second.start_frame)opening=smooth(inv(f,second.start_frame,second.start_frame+spec.fps*.5));
  const zoom=windowed(f,fill.start_frame,E.request2.start_frame,spec.fps*.5);
  ctx.save();ctx.translate(960,620);ctx.scale(1+.04*zoom,1+.04*zoom);ctx.translate(-960,-620);
  at(ctx,296,610,1.0,()=>kiosk(ctx,0,0,{request:c.request,responses:s.responses}));
  at(ctx,939,615,1.0,()=>cacheDrawer(ctx,0,0,{open:opening,filled:s.cache_filled,key:c.key,value:c.value,status:s.cache_result==='hit'?'HIT ✓':s.cache_result==='miss'&&!s.cache_filled?'MISS':''}));
  ctx.save();if(s.cache_filled)ctx.globalAlpha=.5;
  at(ctx,1588,614,1,()=>vault(ctx,0,0,t,{reads:s.db_reads,working:active('read'),value:c.value}));ctx.restore();
  round(ctx,102,275,520,65,13,C.cream,C.ink,3,5);ink(ctx,'同一个键',128,307,27,C.muted);ink(ctx,c.key,402,307,29,C.ink,{align:'center',mono:true,width:222});
  const short=[[439,520],[550,406],[683,405],[774,473]];
  if(f>=E.request1.start_frame){flow(short,f<E.request2.start_frame?'request1':'request2',C.orange,'GET',.84)}
  const origin=[[382,430],[625,267],[1340,277],[1474,415]];
  if(f>=E.origin.start_frame&&f<E.request2.start_frame){flow(origin,'origin',C.orange,'GET',.85);ink(ctx,'未命中 → 应用回源',1045,323,29,C.muted,{align:'center'})}
  const ret=[[1447,798],[1209,900],[688,900],[419,754]];
  if(f>=E.data.start_frame&&f<E.request2.start_frame)flow(ret,'data',C.teal,c.value,.88);
  const miss=[[741,663],[658,758],[530,758],[438,664]];
  if(active('miss'))flow(miss,'miss',C.red,'MISS',.85);
  if(active('fill'))flow(short,'fill',C.yellow,'SET',.85);
  if(f>=E.hit.start_frame)flow(miss,'hit',C.teal,'HIT',.85);
  if(s.has_value&&!s.cache_filled)label(ctx,c.value,515,826,{fill:C.yellow,size:27,angle:-.045});
  if(f>=E.request2.start_frame){label(ctx,'第 2 次 · 同一个键',632,377,{fill:C.yellow,size:29,height:53,angle:-.035});label(ctx,'这次不回源',1590,352,{fill:C.cream,size:30,height:54,angle:.03});}
  label(ctx,'应用 · 管理读取',296,891,{fill:C.orange,size:27,height:45});
  label(ctx,'缓存 · 保存副本',939,903,{fill:C.teal,size:27,height:44});
  label(ctx,'数据源 · 原件',1588,891,{fill:C.purple,size:27,height:45});
  ctx.restore();
 }
}
export function start(spec){
 const canvas=document.getElementById('stage'),ctx=canvas.getContext('2d'),seek=document.getElementById('seek'),toggle=document.getElementById('toggle'),clock=document.getElementById('clock');
 const count=Math.round(spec.duration*spec.fps);let frame=0,playing=false,origin=0;
 canvas.width=spec.width;canvas.height=spec.height;seek.max=count-1;
 const draw=f=>{frame=clamp(Math.round(f),0,count-1);window.semanticState=drawFrame(ctx,spec,frame);window.layoutIssues=window.semanticState.layoutIssues;seek.value=frame;clock.textContent=`${(frame/spec.fps).toFixed(2)} / ${spec.duration.toFixed(2)} s`;return window.semanticState};
 window.renderFrame=draw;window.videoMeta=spec;
 const stop=()=>{playing=false;toggle.textContent='播放'};
 const tick=now=>{if(!playing)return;draw(Math.floor((now-origin)*spec.fps/1000));if(frame>=count-1)stop();else requestAnimationFrame(tick)};
 toggle.onclick=()=>{if(playing)stop();else{if(frame>=count-1)frame=0;origin=performance.now()-frame/spec.fps*1000;playing=true;toggle.textContent='暂停';requestAnimationFrame(tick)}};
 seek.oninput=()=>{stop();draw(Number(seek.value))};
 document.fonts.ready.then(()=>{draw(0);window.ready=true});
}
