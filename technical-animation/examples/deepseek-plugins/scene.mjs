import {C,round,line,ellipse,text,check,arrowHead} from './runtime/drawing.mjs';
import {clamp,inv,easeOut,easeInOut,lerp} from './runtime/motion.mjs';
const spec=window.__PROJECT__ ?? await(await fetch('./project.json')).json();
const canvas=document.getElementById('stage'); canvas.width=spec.width;canvas.height=spec.height;
const g=canvas.getContext('2d');window.videoMeta=spec;
const events=Object.fromEntries(spec.events.map(e=>[e.id,e]));
const progress=(id,t)=>inv(t,events[id].start,events[id].end);
const finished=(id,t)=>t>=events[id].end;
const active=(id,t)=>t>=events[id].start&&t<events[id].end;
const modules=[{id:'model',x:480,name:'模型插件',key:'ctx.llm',color:C.blue,icon:'model'},
 {id:'tools',x:960,name:'工具插件',key:'ctx.tools',color:C.teal,icon:'tools'},
 {id:'loop',x:1440,name:'循环插件',key:'ctx.agentLoop',color:C.yellow,icon:'loop'}];
function txt(s,x,y,size=36,color=C.ink,weight=800,align='center'){text(g,s,x,y,size,color,{weight,align});}
function drawIcon(kind,x,y,color){
 g.save();g.translate(x,y);
 if(kind==='model'){
   round(g,-60,-41,120,78,20,C.cream,C.ink,5);ellipse(g,-22,-5,8,10,C.ink);ellipse(g,22,-5,8,10,C.ink);
   line(g,[[-15,18],[0,23],[15,18]],C.ink,4);line(g,[[0,-41],[0,-55]],C.ink,4);ellipse(g,0,-61,8,8,color,C.ink,4);
 }else if(kind==='tools'){
   round(g,-60,-38,120,82,10,C.ink,C.ink,4);
   line(g,[[-35,-10],[-21,2],[-35,14]],C.teal,6);line(g,[[-6,19],[24,19]],C.cream,5);
   ellipse(g,44,-24,4,4,C.teal);
 }else{
   g.strokeStyle=C.ink;g.lineWidth=8;g.lineCap='round';
   for(let k=0;k<2;k++){let a=k*Math.PI;g.beginPath();g.arc(0,0,42,a+.25,a+2.65);g.stroke();let end=a+2.65;arrowHead(g,42*Math.cos(end),42*Math.sin(end),end+Math.PI/2,C.ink,14);}
   ellipse(g,0,0,9,9,C.ink);
 }
 g.restore();
}
function cartridge(m,t){
 const dock=easeOut(progress('mount-'+m.id,t));
 const removed=m.id==='tools'&&t>=events.unload.start;
 const lift=removed?easeInOut(progress('unload',t))*98:0;
 const y=lerp(278,350,dock)-lift;
 const muted=removed&&finished('unload',t);
 g.save();g.translate(m.x,y);
 for(let i=-1;i<=1;i++) round(g,i*48-12,211,24,32,3,muted?'#D7D3CB':C.yellow,C.ink,4);
 round(g,-164,0,328,215,24,muted?'#E6E2D8':C.cream,C.ink,5,8);
 round(g,-147,16,294,15,5,muted?'#BCB8AF':m.color,null,0);
 drawIcon(m.icon,0,95,m.color);
 txt(m.name,0,173,40,muted?C.muted:C.ink);
 const mounted=finished('mount-'+m.id,t)&&!muted;
 ellipse(g,137,44,7,7,mounted?m.color:'#C9C5BD',C.ink,2);
 if(removed){round(g,-90,-32,180,48,12,C.cream,C.ink,3);txt(muted?'已卸载':'卸载中',0,-8,28,C.muted);}
 if(m.id==='tools'&&active('execute',t)){
   round(g,-100,75,200,49,10,C.teal,C.ink,3);txt('执行',0,100,30);
 }
 if(m.id==='loop'&&t>=events.decision.start){
   round(g,-106,76,212,46,10,C.teal,C.ink,3);check(g,-67,100,.55);txt('已收到',23,99,28);
 }
 g.restore();
}
function trace(points,color,width=6,p=1){
 const lengths=points.slice(1).map((v,i)=>Math.hypot(v[0]-points[i][0],v[1]-points[i][1]));
 let remaining=lengths.reduce((a,b)=>a+b,0)*clamp(p);const visible=[points[0]];
 for(let i=0;i<lengths.length;i++){
   const u=Math.min(1,remaining/lengths[i]);visible.push([lerp(points[i][0],points[i+1][0],u),lerp(points[i][1],points[i+1][1],u)]);
   remaining-=lengths[i];if(remaining<=0)break;
 }
 line(g,visible,color,width);
 return visible.at(-1);
}
function transfer(id,t,points,color,label){
 if(!active(id,t))return;
 trace(points,color,8,.99);
 const pos=trace(points,color,8,easeInOut(progress(id,t)));
 const prev=points.at(-2),end=points.at(-1);arrowHead(g,...end,Math.atan2(end[1]-prev[1],end[0]-prev[0]),color,15);
 round(g,pos[0]-67,pos[1]-25,134,50,13,color,C.ink,4,4);txt(label,pos[0],pos[1],28);
}
function header(t){
 const step=t<2?0:t<5?1:t<8?2:3;
 txt('DEEPSEEK HARNESS',100,83,26,C.muted,700,'left');
 txt('插件如何协作',100,164,68,C.ink,900,'left');
 const names=['装入插件','注册能力','调用与回传','卸载与清理'];
 round(g,1420,77,400,82,20,C.ink,null,0);
 txt(String(step+1).padStart(2,'0'),1466,118,32,C.yellow,800,'left');txt(names[step],1638,118,33,C.cream);
 const labels=['装入','注册','协作','卸载'];
 for(let i=0;i<4;i++){
   let x=1270+i*148;line(g,[[x,204],[x+112,204]],i<=step?C.ink:'#D6D1C7',5);txt(labels[i],x+56,236,25,i===step?C.ink:C.muted,700);
 }
}
function caption(t){
 const step=t<2?0:t<5?1:t<8?2:3;
 const headlines=['连 Agent 循环也是插件','插件通过 ctx 提供能力','各插件协作完成任务','卸载时，撤销对应注册'];
 const details=['模型 · 工具 · 循环，可按配置组合','ctx 是有作用域的能力入口','一次工具调用：发出 → 执行 → 返回','这里只展示工具插件的注册被撤销'];
 round(g,246,864,1428,122,22,C.cream,C.ink,4,6);
 round(g,265,882,12,87,5,[C.yellow,C.blue,C.teal,C.yellow][step],null,0);
 txt(headlines[step],960,907,48);txt(details[step],960,957,28,C.muted,600);
 txt('原理示意 · 非真实运行记录',100,1032,22,C.muted,500,'left');
 txt('EXPLAIN MOTION  /  10s',1820,1032,22,C.muted,600,'right');
}
window.renderFrame=(frame)=>{
 const f=Math.max(0,Math.min(599,Math.round(frame))),t=f/spec.fps;
 g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,1920,1080);g.fillStyle=C.paper;g.fillRect(0,0,1920,1080);
 g.fillStyle='#E4DFD4';for(let x=100;x<1850;x+=48)for(let y=278;y<840;y+=48){g.beginPath();g.arc(x,y,1.3,0,Math.PI*2);g.fill();}
 header(t);
 round(g,260,574,1400,233,28,'#E8E3D8',C.ink,5,9);
 txt('Cordis',315,766,37,C.ink,800,'left');txt('插件框架',472,766,26,C.muted,600,'left');
 if(t>=2){
   const a=easeOut(inv(t,2,2.25));g.save();g.globalAlpha=a;
   round(g,701,737,678,54,15,C.ink,null,0);txt('ctx  ·  有作用域的能力入口',1040,764,29,C.cream);
   g.restore();
 }
 for(const m of modules){
   const cleaned=m.id==='tools'&&finished('cleanup',t);
   const reg=finished('register-'+m.id,t)&&!cleaned;
   round(g,m.x-80,578,160,17,7,C.ink,null,0);
   if(t>=events['register-'+m.id].start&&!cleaned){
     trace([[m.x,594],[m.x,643]],m.color,10,progress('register-'+m.id,t));
   }
   if(reg){
     round(g,m.x-169,648,338,61,15,m.color,C.ink,4);txt(m.key,m.x,679,31);
   }else if(cleaned){
     round(g,m.x-169,648,338,61,15,null,C.muted,3);line(g,[[m.x,600],[m.x,639]],C.muted,3,[7,8]);txt('注册已撤销',m.x,679,31,C.muted);
   }else{
     round(g,m.x-169,648,338,61,15,'#DED9CF',null,0);txt('待注册',m.x,679,29,C.muted,600);
   }
 }
 modules.forEach(m=>cartridge(m,t));
 const route=[[1440,333],[1440,295],[960,295],[960,333]];
 transfer('call',t,route,C.orange,'调用');
 transfer('result',t,[...route].reverse(),C.teal,'结果');
 caption(t);
 window.semanticState={frame:f,time:t,mounted:Object.fromEntries(modules.map(m=>[m.id,finished('mount-'+m.id,t)&&!(m.id==='tools'&&finished('unload',t))])),registered:Object.fromEntries(modules.map(m=>[m.id,finished('register-'+m.id,t)&&!(m.id==='tools'&&finished('cleanup',t))])),callArrived:finished('call',t),executed:finished('execute',t),resultArrived:finished('result',t),done:t>=events.decision.start,stopped:t>=events.hold.start};
};
const toggle=document.getElementById('toggle'),seek=document.getElementById('seek'),clock=document.getElementById('clock');
let playing=false,current=0,anchor=0;
function show(f){current=clamp(f,0,599);window.renderFrame(current);seek.value=String(current);clock.textContent=`${(current/60).toFixed(2)} / 10.00 s`;}
 toggle.onclick=()=>{if(!playing&&current>=599)current=0;playing=!playing;anchor=performance.now()-current/60*1000;toggle.textContent=playing?'暂停':'播放';};
seek.oninput=()=>{playing=false;toggle.textContent='播放';show(Number(seek.value));};
function tick(now){if(playing){show(Math.floor((now-anchor)/1000*60));if(current>=599){playing=false;toggle.textContent='重播';}}requestAnimationFrame(tick);}
await document.fonts.ready;window.ready=true;show(0);requestAnimationFrame(tick);
