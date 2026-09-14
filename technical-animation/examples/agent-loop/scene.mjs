import {clamp,lerp,inv,smooth,easeOut,easeInOut,backOut,spring,envelope,pulse,bezier,tangent,keyframes} from '../../runtime/motion.mjs';
import {C,round,line,ellipse,text,label,burst,dots,path,arrowHead,packet,check,cross} from '../../runtime/drawing.mjs';
import {robot,machine} from '../../runtime/rigs.mjs';
const spec=window.__PROJECT__ ?? await(await fetch('./project.json')).json();
const canvas=document.getElementById('stage'),ctx=canvas.getContext('2d');
const E=Object.fromEntries(spec.events.map(e=>[e.id,e]));
window.videoMeta=spec;
const outgoing=[[838,498],[1010,287],[1220,282],[1360,430]];
const feedback=[[1350,761],[1260,916],[982,914],[813,731]];
// A paper stage with intentional asymmetry. It is a location, not a card grid.
function background(t){
 ctx.fillStyle=C.paper;ctx.fillRect(0,0,1920,1080);
 ctx.save();ctx.globalAlpha=.17;dots(ctx,35,0,1890,1080,{step:25,r:1.1,alpha:1,color:'#8D9689'});ctx.restore();
 ctx.save();ctx.globalAlpha=.44;ctx.fillStyle='#E5E8DC';ctx.beginPath();ctx.ellipse(1060,664,846,290,0,0,Math.PI*2);ctx.fill();ctx.restore();
 line(ctx,[[72,102],[1848,102]],C.ink,2);
 text(ctx,'EXPLAIN / MOTION',75, sixty(),25,C.ink,{font:'mono'});
 text(ctx,'01  /  AGENT LOOP',1845,60,23,C.muted,{align:'right',font:'mono'});
 function sixty(){return 60}
}
const headings=[
 [0,'Agent，怎么把事情做完？','一个目标，多次行动。'],
 [1.35,'①  先调用工具','模型选择动作，工具负责执行。'],
 [2.70,'②  把结果带回来','报错进入上下文，成为下一步的依据。'],
 [4.45,'③  改完，再验证','修改代码，再次调用测试工具。'],
 [6.75,'④  达标，才结束','验证结果满足目标，停止循环。'],
 [8.10,'Agent 的关键，是反馈闭环','调用  →  反馈  →  再决策']
];
function heading(t){
 let index=0;for(let i=0;i<headings.length;i++)if(t>=headings[i][0])index=i;
 const h=headings[index],age=t-h[0],a=easeOut(inv(age,0,.23));
 ctx.save();ctx.beginPath();ctx.rect(70,126,1790,130);ctx.clip();ctx.globalAlpha=a;ctx.translate(0,(1-a)*32);
 text(ctx,h[1],80,181,index===5?68:65,C.ink);
 let underlineW=index===5?930:index===0?950:570;
 line(ctx,[[83,239],[83+underlineW*smooth(inv(age,.08,.48)),239]],index===2?C.red:index===4?C.teal:C.orange,9);
 ctx.restore();
 // one sentence per beat; strong contrast, no lecture on screen
 round(ctx,78,945,1764,86,21,C.ink,null,0);
 text(ctx,h[2],960,989,index===5?46:37,index===5?C.yellow:C.cream,{align:'center'});
 text(ctx,'机制示意 · 非实时 Agent 录屏',1839,1053,19,C.muted,{align:'right',weight:500});
 return index;
}
function task(t){
 let s=lerp(.85,1,backOut(inv(t,0,.7)));let tx=lerp(-370,316,easeOut(inv(t,0,.65)));
 ctx.save();ctx.translate(tx,521);ctx.rotate(lerp(-.2,-.045,easeOut(inv(t,0,.75))));ctx.scale(s,s);
 round(ctx,-155,-115,310,221,13,C.cream,C.ink,4,9);
 round(ctx,-68,-136,136,38,8,C.yellow,C.ink,3);
 text(ctx,'任务',0,-69,27,C.muted,{align:'center'});
 text(ctx,'让测试通过',0,-15,40,C.ink,{align:'center'});
 line(ctx,[[-112,31],[110,31]],C.line,2);
 text(ctx,'add(2,3) = 5',0,70,26,C.ink,{align:'center',font:'mono'});
 if(t>=8){const p=backOut(inv(t,8,8.4));ctx.save();ctx.translate(80,-87);ctx.rotate(-.13);ctx.scale(p,p);ellipse(ctx,0,0,45,45,C.teal,C.ink,4);check(ctx,0,0,1);ctx.restore()}
 ctx.restore();
 let p=bezier([[490,535],[500,521],[515,521],[530,535]],1);path(ctx,[[490,535],[500,521],[515,521],[530,535]],{color:C.muted,width:4,progress:smooth(inv(t,.45,1.1)),dash:[7,9]});
 if(t>1)arrowHead(ctx,p.x,p.y,0,C.muted,11);
}
function contextStack(t){
 let active=smooth(inv(t,E.fail.end,E.fail.end+.35));
 ctx.save();ctx.translate(474,750);ctx.rotate(-.08);
 for(let i=2;i>=0;i--)round(ctx,-34+i*9,-37-i*9,120,82,10,i===0?C.cream:'#DDD8EA',C.ink,3);
 text(ctx,'上下文',24,-4,21,C.ink,{align:'center'});
 if(active){ctx.save();ctx.globalAlpha=active;ctx.translate(lerp(250,0,easeOut(inv(t,3.5,3.8))),-62*active);label(ctx,t>=7.45?'FAIL → PASS':'FAIL 已读',31,5,{fill:t>=7.45?C.teal:C.red,size:18,height:36,shadow:3});ctx.restore()}
 ctx.restore();
}
function receipt(t){
 if(t<2.7)return;
 let success=t>=6.75;let birth=success?6.75:2.70;let p=spring(t-birth,{frequency:3.4,damping:10});
 let alpha=success?1:1-smooth(inv(t,4.4,4.7));if(alpha<.001)return;
 ctx.save();ctx.globalAlpha=alpha;ctx.translate(1630,362);ctx.rotate(-.07);ctx.scale(p,p);
 label(ctx,success?'PASS ✓':'FAIL ×',0,0,{fill:success?C.teal:C.red,size:37,height:71,pad:25,shadow:7});
 ctx.restore();
}
function decideBubble(t){
 let isSuccess=t>=7.45,start=isSuccess?7.45:3.5,end=isSuccess?8.05:4.45;
 if(t<start||t>end)return;
 let a=envelope(t,start-.01,end+.1,.15);
 ctx.save();ctx.globalAlpha=a;ctx.translate(650,317-20*(1-a));
 round(ctx,-136,-34,272,67,20,isSuccess?C.teal:C.yellow,C.ink,4,5);
 text(ctx,isSuccess?'可以结束了':'减号写错了！',0,0,30,C.ink,{align:'center'});
 ctx.fillStyle=isSuccess?C.teal:C.yellow;ctx.strokeStyle=C.ink;ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(-30,34);ctx.lineTo(-8,57);ctx.lineTo(6,34);ctx.fill();ctx.stroke();
 ctx.restore();
}
function endLoop(t){
 let a=smooth(inv(t,8.05,8.5));if(!a)return;
 ctx.save();ctx.globalAlpha=a;
 // the loop surrounds both the decision maker AND the tool executor
 // Final headline carries the loop takeaway; no duplicate label over the path.
 path(ctx,outgoing,{color:C.orange,width:8,progress:1});let pt=bezier(outgoing,1);arrowHead(ctx,pt.x,pt.y,tangent(outgoing,1),C.orange,16);
 path(ctx,feedback,{color:C.teal,width:8,progress:1});pt=bezier(feedback,1);arrowHead(ctx,pt.x,pt.y,tangent(feedback,1),C.teal,16);
 // no packets after STOP: only the explanatory loop remains
 label(ctx,'完成',1115,653,{fill:C.teal,size:38,height:75,shadow:7});
 ctx.restore();
}
function renderFrame(frame){
 const t=clamp(frame/spec.fps,0,spec.duration-1/spec.fps);
 ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;ctx.lineCap='round';ctx.lineJoin='round';
 background(t);
 let camScale=keyframes(t,[[0,1.07],[.85,1],[1.8,1],[2.28,1.07],[2.68,1.07],[3.45,1],[3.8,1.055],[4.4,1.055],[4.8,1],[6.12,1.07],[6.65,1.07],[7.4,1],[10,1]]);
 let camX=keyframes(t,[[0,-12],[1,0],[2.28,-26],[2.68,-26],[3.45,0],[3.8,12],[4.4,12],[4.8,0],[6.12,-26],[6.65,-26],[7.4,0]]);
 ctx.save();ctx.translate(960+camX,650);ctx.scale(camScale,camScale);ctx.translate(-960,-650);
 // background lanes grow ahead of the traveling messages
 let lane=smooth(inv(t,.65,1.35));ctx.save();ctx.globalAlpha=lane;
 path(ctx,outgoing,{width:5,color:'#B8B9AF',dash:[7,11]});path(ctx,feedback,{width:5,color:'#B8B9AF',dash:[7,11]});
 text(ctx,'调用',1108,296,26,C.muted,{align:'center'});text(ctx,'工具结果',1128,894,25,C.muted,{align:'center'});ctx.restore();
 task(t);contextStack(t);
 // lamps respond only once a packet has arrived (not when it leaves)
 let working=(t>=2.05&&t<2.7)||(t>=5.15&&t<5.5)||(t>=6.1&&t<6.75)?1:0;
 let state=t>=6.75?'pass':t>=6.1?'running':t>=5.15?'patch':t>=2.7?'fail':t>=2.05?'running':'idle';
 let impact=pulse(t,2.05,.4)+pulse(t,5.15,.4)+pulse(t,6.1,.4);
 machine(ctx,1460,616,t,{state,working,patch:t>=5.15?1:0,impact});
 let reach=pulse(t,1.2,1.25)*1.5+pulse(t,4.28,1.26)*1.5+pulse(t,5.34,1.12)*1.5;
 let recoil=pulse(t,3.5,.75),success=smooth(inv(t,7.45,7.9));
 let think=envelope(t,3.52,4.45,.13);
 let entrance=backOut(inv(t,.12,.78));
 ctx.save();ctx.translate(690,636);ctx.scale(entrance,entrance);robot(ctx,0,0,t,{reach,think,recoil,success,look:state==='fail'?-1:1});ctx.restore();
 if(t>=3.5&&t<3.94){ctx.save();ctx.globalAlpha=1-inv(t,3.5,3.94);line(ctx,[[477,374],[449,350]],C.red,6);line(ctx,[[469,415],[432,411]],C.red,6);ctx.restore()}
 label(ctx,'LLM · 决定下一步',688,878,{fill:C.orange,size:28,height:55,shadow:5});
 label(ctx,'工具 · 执行与验证',1450,878,{fill:C.teal,size:28,height:55,shadow:5});
 receipt(t);decideBubble(t);
 for (const id of ['test1','patch','test2','fail','pass']) {
   const e=E[id]; if(t<e.start||t>e.end)continue;
   const returning=e.kind==='result',points=returning?feedback:outgoing;
   ctx.save();ctx.globalAlpha=.55;
   path(ctx,points,{color:id==='fail'?C.red:returning?C.teal:id==='patch'?C.yellow:C.orange,width:7,progress:easeInOut(inv(t,e.start,e.end))});
   ctx.restore();
 }
 for (const id of ['test1','patch','test2']) {
   const at=E[id].end,u=inv(t,at,at+.38);if(t<at||u>=1)continue;
   ctx.save();ctx.globalAlpha=(1-u)*.8;
   const cx=1460,cy=400;
   for(let i=0;i<3;i++){let x=cx-90+i*90;line(ctx,[[x,cy-15-u*18],[x+(i-1)*14,cy-41-u*34]],id==='patch'?C.yellow:C.orange,5*(1-u))}
   ctx.restore();
 }
 for(const id of ['test1','patch','test2']){let e=E[id];packet(ctx,outgoing,t,e.start,e.end,{color:id==='patch'?C.yellow:C.orange,str:e.label})}
 for(const id of ['fail','pass']){let e=E[id];packet(ctx,feedback,t,e.start,e.end,{color:id==='fail'?C.red:C.teal,str:e.label})}
 // a short code-diff lens at the moment of the patch: state change is visible
 if(t>=4.77&&t<5.75){let a=envelope(t,4.77,5.75,.12);ctx.save();ctx.globalAlpha=a;ctx.translate(1080,612);ctx.rotate(-.055);round(ctx,-139,-60,278,120,17,C.cream,C.ink,4,7);text(ctx,'−  a − b',-103,-24,29,C.red,{font:'mono'});text(ctx,'+  a + b',-103,28,29,'#188875',{font:'mono'});ctx.restore()}
 // green arrival impact spreads from the model, then comes to rest
 if(t>=7.45&&t<8.1){let u=inv(t,7.45,8.1);ctx.save();ctx.globalAlpha=(1-u)*.7;ctx.strokeStyle=C.teal;ctx.lineWidth=8*(1-u);ctx.beginPath();ctx.arc(690,548,145+u*75,0,Math.PI*2);ctx.stroke();ctx.restore()}
 endLoop(t);
 ctx.restore();
 const phase=heading(t);
 // understated bottom progress rail (not data motion)
 ctx.fillStyle=C.orange;ctx.fillRect(78,1039,1764*t/10,3);
 window.semanticState={frame,t,phase,tool:state,working:!!working,patched:t>=5.15,feedbackReceived:t>=3.5,done:t>=8};
 document.getElementById('seek').value=frame;
 document.getElementById('clock').textContent=t.toFixed(2)+' / 10.00 s';
}
window.renderFrame=renderFrame;
await document.fonts.ready;window.ready=true;
if(new URLSearchParams(location.search).has('capture'))document.body.classList.add('capture');
renderFrame(0);
let playing=false,current=0,origin=0;
const button=document.getElementById('toggle'),seek=document.getElementById('seek');
button.onclick=()=>{playing=!playing;button.textContent=playing?'暂停':'播放';if(playing){origin=performance.now()-current/spec.fps*1000;requestAnimationFrame(tick)}};
seek.oninput=()=>{playing=false;button.textContent='播放';current=+seek.value;renderFrame(current)};
function tick(now){if(!playing)return;current=Math.min(599,Math.floor((now-origin)/1000*60));renderFrame(current);if(current>=599){playing=false;button.textContent='重播';current=0}else requestAnimationFrame(tick)}
