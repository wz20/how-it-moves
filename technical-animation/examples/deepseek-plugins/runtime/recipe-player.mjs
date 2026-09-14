/** Recipe renderer: distinct mechanism layouts, controlled original vector assets.
 * No model-written coordinates; all technical state and captions come from compiled events.
 */
import {C,round,line,ellipse,text,label,dots,path,arrowHead,check,cross,burst} from './drawing.mjs';
import {clamp,lerp,smooth,easeOut,easeInOut,backOut,bezier,tangent,pulse,envelope} from './motion.mjs';
import {robot} from './rigs.mjs';
import {stateAtFrame,eventProgress,activeEvent} from './recipe-state.mjs';

const nameMap={'feedback-retry':'01 / FEEDBACK LOOP','retrieval-evidence':'02 / EVIDENCE FLOW','cache-aside':'03 / CACHE ASIDE'};
const colorFor=e=>e.id==='fail'||e.id==='miss'?C.red:e.id==='pass'||e.id==='hit'||e.id==='data'||e.id==='answer'?C.teal:e.id==='evidence'?C.blue:e.id==='patch'||e.id==='fill'?C.yellow:C.orange;

function drawText(ctx,str,x,y,size=36,color=C.ink,options={}){
 text(ctx,str,x,y,size,color,options);
}
function base(ctx,p,state,e){
 ctx.fillStyle=C.paper;ctx.fillRect(0,0,1920,1080);
 dots(ctx,45,116,1840,810,{step:28,r:1,color:C.muted,alpha:.13});
 ellipse(ctx,986,699,841,211,'#E6E8DD');
 line(ctx,[[76,99],[1844,99]],C.ink,2);
 drawText(ctx,'EXPLAIN / MOTION',77,56,24,C.ink,{font:'mono'});
 drawText(ctx,nameMap[p.recipe],1843,56,22,C.muted,{font:'mono',align:'right'});
 drawText(ctx,p.title,78,169,58);
 const u=smooth(clamp(state.frame/(p.fps*.65)));
 line(ctx,[[83,227],[83+620*u,227]],C.orange,9);
 const visible=p.events.filter(ev=>ev.kind!=='goal'&&ev.kind!=='stop');
 const completed=visible.filter(ev=>ev.end_frame<=state.frame).length;
 for(let i=0;i<visible.length;i++)round(ctx,1490+i*(325/visible.length),218,Math.max(6,325/visible.length-7),9,4,i<completed?C.teal:C.line,null);
 round(ctx,77,946,1766,87,21,C.ink,null,0);
 drawText(ctx,state.caption||p.takeaway,960,990,38,e.kind==='stop'?C.yellow:C.cream,{align:'center'});
 drawText(ctx,'机制示意 · 虚构教学数据 · 非实时系统运行',1840,1055,19,C.muted,{align:'right',weight:500});
}
function wrapped(ctx,str,x,y,width,size=28,color=C.ink,maxLines=2,align='center'){
 ctx.save();ctx.font=`800 ${size}px "Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif`;
 const lines=[];let lineText='';for(const char of [...str]){if(ctx.measureText(lineText+char).width>width&&lineText){lines.push(lineText);lineText=char;}else lineText+=char;}if(lineText)lines.push(lineText);ctx.restore();
 if(lines.length>maxLines)throw new Error('E_LAYOUT: text exceeds '+maxLines+' lines: '+str);
 lines.forEach((s,i)=>drawText(ctx,s,x,y+i*(size+8),size,color,{align}));
}
function pill(ctx,str,x,y,fill=C.cream,size=28){label(ctx,str,x,y,{fill,size,height:52,shadow:4});}
function bubble(ctx,str,x,y,fill=C.yellow){
 ctx.save();ctx.translate(x,y);round(ctx,-156,-37,312,75,20,fill,C.ink,4,5);
 drawText(ctx,str,0,0,28,C.ink,{align:'center'});
 ctx.fillStyle=fill;ctx.beginPath();ctx.moveTo(-40,37);ctx.lineTo(-13,59);ctx.lineTo(0,37);ctx.fill();line(ctx,[[-40,37],[-13,59],[0,37]],C.ink,4);ctx.restore();
}
function lane(ctx,points,e,frame,{show=false,caption=null}={}){
 const reached=frame>=e.start_frame;if(!reached&&!show)return;
 const col=colorFor(e);const u=reached?smooth(clamp((frame-e.start_frame)/14)):1;
 path(ctx,points,{color:col,width:5,progress:u,dash:show&&frame<e.start_frame?[7,11]:[]});
 if(u>=.99){const q=bezier(points,1);arrowHead(ctx,q.x,q.y,tangent(points,1),col,13);}
 if(caption){const mid=bezier(points,.53);drawText(ctx,caption,mid.x,mid.y-39,22,C.muted,{align:'center'});}
}
function message(ctx,points,e,frame,str=e.label,{width=144,color=colorFor(e)}={}){
 if(frame<e.start_frame||frame>=e.end_frame)return;
 const u=easeInOut(eventProgress(e,frame));const q=bezier(points,u);
 ctx.save();
 for(let i=5;i>0;i--){let tail=bezier(points,clamp(u-i*.023));ctx.globalAlpha=.16*(1-i/6);ellipse(ctx,tail.x,tail.y,18-i*2,18-i*2,color);}
 ctx.globalAlpha=1;ctx.translate(q.x,q.y);ctx.rotate(tangent(points,u)*.09);
 round(ctx,-width/2,-30,width,60,13,color,C.ink,4,5);drawText(ctx,str,0,1,26,C.ink,{align:'center'});ctx.restore();
}
function paper(ctx,x,y,w,h,title,body,{fill=C.cream,angle=0}={}){
 ctx.save();ctx.translate(x,y);ctx.rotate(angle);round(ctx,-w/2,-h/2,w,h,15,fill,C.ink,4,7);
 round(ctx,-58,-h/2-15,116,28,7,C.yellow,C.ink,3);drawText(ctx,title,0,-h/2+52,25,C.muted,{align:'center'});
 line(ctx,[[-w/2+25,-h/2+84],[w/2-25,-h/2+84]],C.line,2);
 wrapped(ctx,body,0,12,w-42,29,C.ink,2);ctx.restore();
}
function badge(ctx,x,y,value,color){ellipse(ctx,x,y,34,34,color,C.ink,4);if(value)check(ctx,x,y,.68);else cross(ctx,x,y,.8);}
function terminal(ctx,x,y,c,state,e,u,t){
 const working=e.kind==='execute'&&e.actor==='tool';const status=working?'RUNNING':state.tool_result==='fail'?c.failure:state.tool_result==='pass'?c.success:state.code_changed?'PATCHED':'READY';
 const col=status===c.failure?C.red:status===c.success?C.teal:working?C.yellow:C.muted;
 ctx.save();ctx.translate(x,y);ctx.rotate(working?Math.sin(t*32)*.003:0);
 ellipse(ctx,9,234,221,22,'#22252B12');
 ctx.fillStyle='#2B948D';ctx.strokeStyle=C.ink;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(188,-185);ctx.lineTo(218,-155);ctx.lineTo(218,204);ctx.lineTo(188,217);ctx.closePath();ctx.fill();ctx.stroke();
 round(ctx,-197,-194,390,400,33,C.teal,C.ink,6);
 round(ctx,-174,-170,344,246,22,C.ink,C.ink,4);drawText(ctx,'CODE + TEST',-146,-134,24,'#BACEC5',{font:'mono'});
 line(ctx,[[-146,-108],[143,-108]],'#52645F',2);
 drawText(ctx,state.code_changed?c.after:c.before,0,-55,26,state.code_changed?C.teal:C.orange,{align:'center',font:'mono'});
 if(e.id==='apply'){
  const reveal=smooth(clamp((u-.12)/.8));line(ctx,[[-146,0],[-146+292*reveal,0]],C.yellow,7);
  drawText(ctx,'APPLYING PATCH',0,37,25,C.yellow,{align:'center',font:'mono'});
 }else drawText(ctx,status,0,28,34,col,{align:'center',font:'mono'});
 round(ctx,-151,112,206,43,11,C.cream,C.ink,4);
 for(let i=0;i<4;i++)round(ctx,-137+i*47,122,29,21,5,working&&Math.floor(u*12)%4===i?C.yellow:'#C9D9CC',C.ink,2);
 ellipse(ctx,118,134,27,27,C.yellow,C.ink,4);line(ctx,[[118,119],[118,131]],C.ink,4);
 for(const xx of [-134,143]){ctx.save();ctx.translate(xx,193);ctx.rotate(working?t*8:0);ellipse(ctx,0,0,18,18,C.cream,C.ink,3);line(ctx,[[-10,0],[10,0]],C.ink,3);ctx.restore();}
 ctx.restore();
}
function feedback(ctx,p,s,e,f){
 const c=p.content,ev=Object.fromEntries(p.events.map(x=>[x.id,x]));const t=f/p.fps,u=eventProgress(e,f);
 const out=[[879,471],[1050,319],[1230,307],[1390,404]],back=[[1433,770],[1290,882],[1057,884],[820,755]];
 paper(ctx,269,568,295,214,'任务',c.goal,{angle:-.045});
 if(s.stopped)badge(ctx,382,467,true,C.teal);
 lane(ctx,out,ev.test1,f);lane(ctx,back,{...ev.fail,id:f>=ev.pass.start_frame?'pass':'fail'},f);
 let reach=e.kind==='call'&&e.actor==='model'?Math.sin(Math.PI*clamp(u*1.25)):0;
 let think=e.kind==='decision'&&!s.stopped?envelope(u,0,1,.18):0;
 ctx.save();ctx.translate(694,654);robot(ctx,0,0,s.stopped?ev.done.start: t,{reach,think,success:s.stopped?1:0,look:1,recoil:e.id==='decide1'?pulse(u,0,.7):0});ctx.restore();
 terminal(ctx,1510,586,c,s,e,u,t);
 pill(ctx,'模型 / 决策',687,882,C.orange);pill(ctx,'工具 / 执行',1510,878,C.teal);
 // Context is a visible receiving container, not model weights.
 ctx.save();ctx.translate(479,786);ctx.rotate(-.06);
 for(let i=2;i>=0;i--)round(ctx,-86+i*7,-40-i*9,168,82,10,i===0?C.cream:'#DCD5EE',C.ink,3);
 drawText(ctx,'上下文',0,-5,23,C.ink,{align:'center'});if(s.feedback_received)drawText(ctx,s.last_feedback==='pass'?c.failure+' → '+c.success:c.failure+' 已读',0,23,20,s.last_feedback==='pass'?C.teal:C.red,{align:'center'});ctx.restore();
 if(e.kind==='decision'&&e.id!=='decide2')bubble(ctx,c.decision,681,318);
 if(e.id==='decide2')bubble(ctx,'验证通过，可以结束',680,318,C.teal);
 for(const id of ['test1','patch','test2'])message(ctx,out,ev[id],f);
 for(const id of ['fail','pass'])message(ctx,back,ev[id],f);
 if(s.stopped)pill(ctx,'完成 · 停止调用',1100,655,C.teal,32);
}
function doc(ctx,d,x,y,selected,dim=false){
 ctx.save();ctx.globalAlpha=dim?.38:1;round(ctx,x-141,y-46,282,92,13,selected?C.blue:C.cream,C.ink,3,4);
 drawText(ctx,d.id,x-116,y-18,23,C.ink,{font:'mono'});wrapped(ctx,d.text,x-117,y+8,234,22,C.ink,2,'left');
 if(selected)check(ctx,x+111,y-17,.43);ctx.restore();
}
function retrieval(ctx,p,s,e,f){
 const c=p.content,ev=Object.fromEntries(p.events.map(x=>[x.id,x]));const u=eventProgress(e,f),t=f/p.fps;
 const query=[[435,567],[470,466],[491,463],[529,495]],flow=[[800,413],[928,272],[1025,276],[1125,406]],answer=[[1313,568],[1380,475],[1416,475],[1470,535]];
 paper(ctx,270,551,298,238,'用户问题',c.question,{angle:-.035});
 round(ctx,507,319,324,473,22,'#E4DDCD',C.ink,4,7);drawText(ctx,'知识库 / 检索',670,357,27,C.ink,{align:'center'});
 const selected=s.selected_ids||[],inSelect=e.id==='select';
 c.documents.forEach((d,i)=>{
  const onset=clamp(u*1.8-i*.19);const chosen=selected.includes(d.id)||(inSelect&&d.selected&&onset>.35);
  const dy=chosen?-8*backOut(clamp(inSelect?onset:1)):0;
  doc(ctx,d,669,433+i*126+dy,chosen,selected.length>0&&!d.selected);
 });
 if(e.id==='search'){
  const y=393+u*(c.documents.length*126-34);line(ctx,[[523,y],[811,y]],C.orange,5);ellipse(ctx,813,y,8,8,C.orange);
 }
 pill(ctx,s.retrieved?'已找到候选片段':'等待检索',670,850,s.retrieved?C.blue:C.cream,25);
 lane(ctx,query,ev.query,f);lane(ctx,flow,ev.evidence,f);lane(ctx,answer,ev.answer,f);
 message(ctx,query,ev.query,f);
 if(e.id==='evidence'){
  const ds=c.documents.filter(d=>d.selected);ds.forEach((d,i)=>{
   const span=e.end_frame-e.start_frame,delay=Math.round(i*span*.12),end=e.end_frame;
   message(ctx,flow,{...e,start_frame:e.start_frame+delay,end_frame:end},f,d.id,{width:94,color:C.blue});
  });
 }
 ctx.save();ctx.translate(1179,623);ctx.scale(.73,.73);robot(ctx,0,0,s.stopped?ev.done.start:t,{think:e.id==='generate'?envelope(u,0,1,.2):0,reach:e.id==='answer'?Math.sin(Math.PI*u):0,success:s.delivered?1:0});ctx.restore();
 pill(ctx,'LLM / 生成',1176,854,C.orange,27);
 // Question remains visible; the receiving tray appears only after evidence arrival.
 round(ctx,979,750,409,67,14,s.context_ready?'#DCE9F8':C.cream,C.ink,3);
 drawText(ctx,s.context_ready?'问题 + '+s.selected_ids.join(' / '):'等待问题与检索证据',1183,783,26,C.ink,{align:'center'});
 if(e.id==='generate')bubble(ctx,'依据上下文生成',1179,332,C.blue);
 paper(ctx,1652,570,332,324,'带来源的回答','',{angle:.025});
 if(s.delivered){
  // Two lines for a longer answer; this is a recipe-controlled wrap, never squeeze text.
  wrapped(ctx,c.answer,1652,558,288,28,C.ink,3);
  drawText(ctx,c.citations.map(x=>'['+x+']').join(' '),1652,686,25,'#405AB0',{align:'center',font:'mono'});badge(ctx,1752,434,true,C.teal);
 }else {drawText(ctx,e.id==='answer'?'回答传输中':'等待证据与生成',1652,581,26,C.muted,{align:'center'});}
 message(ctx,answer,ev.answer,f);
}
function database(ctx,x,y,state,working,u){
 ctx.save();ctx.translate(x,y);ellipse(ctx,0,198,194,22,'#22252B12');
 for(let i=2;i>=0;i--){
  const yy=i*62;round(ctx,-158,yy-105,316,96,4,C.blue,C.ink,4);
  ellipse(ctx,0,yy-9,158,34,C.blue,C.ink,4);ellipse(ctx,0,yy-105,158,34,'#CBD8FF',C.ink,4);
  ellipse(ctx,116,yy-55,7,7,working&&Math.floor(u*8)%3===i?C.yellow:C.cream,C.ink,2);
 }
 drawText(ctx,'DATABASE',0,-113,27,C.ink,{align:'center',font:'mono'});
 pill(ctx,'回源读取 × '+state.db_reads,0,209,C.cream,25);ctx.restore();
}
function cacheBox(ctx,x,y,c,s,e,u){
 ctx.save();ctx.translate(x,y);ellipse(ctx,0,202,215,19,'#22252B12');
 round(ctx,-189,-163,378,341,25,C.yellow,C.ink,5,8);
 round(ctx,-165,-132,330,54,10,C.cream,C.ink,3);drawText(ctx,'CACHE',0,-105,32,C.ink,{align:'center',font:'mono'});
 round(ctx,-160,-52,320,140,12,C.ink,C.ink,3);drawText(ctx,c.key,0,-19,27,C.yellow,{align:'center',font:'mono'});
 drawText(ctx,s.cache_filled?c.value:'EMPTY',0,37,35,s.cache_filled?C.teal:'#95A292',{align:'center',font:'mono'});
 if(e.id==='lookup1'||e.id==='lookup2'){const xx=lerp(-142,141,u);line(ctx,[[xx,-46],[xx,80]],C.orange,5);}
 drawText(ctx,s.cache_result==='hit'?'HIT ✓':s.cache_result==='miss'?'MISS ×':'等待请求',0,128,29,s.cache_result==='hit'?'#136455':C.ink,{align:'center'});
 ctx.restore();
}
function application(ctx,x,y,c,s,e,u){
 ctx.save();ctx.translate(x,y);ellipse(ctx,0,210,205,21,'#22252B12');
 round(ctx,-172,-150,344,272,24,C.cream,C.ink,5,7);round(ctx,-149,-119,298,208,15,C.ink,C.ink,3);
 drawText(ctx,'APPLICATION',0,-88,23,'#A9BDB6',{align:'center',font:'mono'});drawText(ctx,c.request,0,-34,29,C.cream,{align:'center'});
 drawText(ctx,s.has_value||s.responses>0?c.value:'?',0,27,41,s.has_value?C.teal:C.yellow,{align:'center'});
 line(ctx,[[0,131],[0,163]],C.ink,19);round(ctx,-104,167,208,18,8,C.ink,C.ink,2);
 pill(ctx,'已返回用户 × '+s.responses,0,228,C.cream,25);ctx.restore();
}
function cache(ctx,p,s,e,f){
 const c=p.content,ev=Object.fromEntries(p.events.map(x=>[x.id,x]));const u=eventProgress(e,f);
 const ask=[[513,497],[588,323],[713,318],[811,367]],miss=[[806,548],[694,600],[639,621],[535,617]],origin=[[520,751],[697,806],[1112,803],[1350,737]],data=[[1350,815],[1094,914],[749,917],[503,828]];
 lane(ctx,ask,ev.request1,f);lane(ctx,miss,{...ev.miss,id:f>=ev.hit.start_frame?'hit':'miss'},f);lane(ctx,origin,ev.origin,f);lane(ctx,data,ev.data,f);
 application(ctx,327,633,c,s,e,u);cacheBox(ctx,992,451,c,s,e,u);
 ctx.save();if(s.requests>=2)ctx.globalAlpha=.54;database(ctx,1548,605,s,e.id==='read',u);ctx.restore();
 pill(ctx,'缓存有效期内的相同键',994,745,C.cream,26);
 if(s.requests>=2)drawText(ctx,'第二次不再访问数据库',1545,351,28,'#53665D',{align:'center'});
 for(const id of ['request1','fill','request2'])message(ctx,ask,ev[id],f);
 for(const id of ['miss','hit'])message(ctx,miss,ev[id],f);
 message(ctx,origin,ev.origin,f);message(ctx,data,ev.data,f);
 if(s.stopped)badge(ctx,1180,286,true,C.teal);
}

export function startRecipe(p){
 const canvas=document.getElementById('stage'),ctx=canvas.getContext('2d');canvas.width=p.width;canvas.height=p.height;
 const n=Math.round(p.duration*p.fps);const fn={'feedback-retry':feedback,'retrieval-evidence':retrieval,'cache-aside':cache}[p.recipe];
 if(!fn)throw new Error('Unsupported recipe');
 window.videoMeta=p;
 function draw(frame){
  const f=Math.max(0,Math.min(n-1,Math.trunc(frame)));const s=stateAtFrame(p,f),e=activeEvent(p,f);
  ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;ctx.lineCap='round';ctx.lineJoin='round';
  base(ctx,p,s,e);fn(ctx,p,s,e,f);window.semanticState=s;
  return s;
 }
 window.renderFrame=draw;
 const toggle=document.getElementById('toggle'),seek=document.getElementById('seek'),clock=document.getElementById('clock');
 seek.max=String(n-1);let playing=false,frame=0,anchor=0;
 function update(f){frame=Math.max(0,Math.min(n-1,f));draw(frame);seek.value=String(frame);clock.textContent=(frame/p.fps).toFixed(2)+' / '+p.duration.toFixed(2)+' s';}
 toggle.onclick=()=>{if(!playing&&frame>=n-1)frame=0;playing=!playing;anchor=performance.now()-frame/p.fps*1000;toggle.textContent=playing?'暂停':'播放';};
 seek.addEventListener('input',()=>{playing=false;toggle.textContent='播放';update(Number(seek.value));});
 // Wall clock belongs ONLY to the preview controller, never to frame rendering.
 function tick(now){if(playing){update(Math.floor((now-anchor)/1000*p.fps));if(frame>=n-1){playing=false;toggle.textContent='重播';}}requestAnimationFrame(tick);}
 window.pausePreview=()=>{playing=false;toggle.textContent='播放';};
 awaitFonts().then(()=>{update(0);window.ready=true;requestAnimationFrame(tick);});
}
async function awaitFonts(){if(document.fonts)await document.fonts.ready;}
