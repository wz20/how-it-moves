/** Physical, layered comic props. Original MIT artwork; not screenshots or generic UI cards. */
import {C,round,line,ellipse,text,dots,check,cross,label} from './drawing.mjs';
import {clamp,lerp,smooth} from './motion.mjs';
import {machine} from './rigs.mjs';
export {C,round,line,ellipse,dots,check,cross,label};
export function ink(ctx,s,x,y,size=30,color=C.ink,opts={}) {
 ctx.save();ctx.font=`${opts.weight||800} ${size}px ${opts.mono?'"DejaVu Sans Mono",monospace':'"Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif'}`;
 ctx.textAlign=opts.align||'left';ctx.textBaseline='middle';ctx.fillStyle=color;
 const w=ctx.measureText(String(s)).width;
 if(opts.width && w>opts.width+1 && ctx.globalAlpha>.08) (ctx.artIssues??=[]).push({text:String(s),width:w,allowed:opts.width});
 ctx.fillText(String(s),x,y);ctx.restore();
}
export function wrap(ctx,s,x,y,maxWidth,size=28,color=C.ink,align='left') {
 ctx.save();ctx.font=`800 ${size}px "Noto Sans CJK SC",sans-serif`;
 let lines=[],v='';for(const ch of String(s)){if(ctx.measureText(v+ch).width>maxWidth&&v){lines.push(v);v=ch}else v+=ch}if(v)lines.push(v);ctx.restore();
 if(lines.length>1 && lines.at(-1).length<2 && lines.at(-2).length>3){const tail=lines.at(-2).slice(-1);lines[lines.length-2]=lines.at(-2).slice(0,-1);lines[lines.length-1]=tail+lines.at(-1)}
 lines.forEach((l,i)=>ink(ctx,l,x,y+i*size*1.45,size,color,{align,width:maxWidth}));return lines.length;
}
export function at(ctx,x,y,s,fn,a=0){ctx.save();ctx.translate(x,y);ctx.rotate(a);ctx.scale(s,s);fn();ctx.restore()}
export function shadow(ctx,x,y,rx,ry){ellipse(ctx,x,y,rx,ry,'#22252B12')}
export function screw(ctx,x,y){ellipse(ctx,x,y,6,6,C.cream,C.ink,2);line(ctx,[[x-3,y-3],[x+3,y+3]],C.ink,2)}
export function gear(ctx,x,y,r,angle=0,color=C.yellow){at(ctx,x,y,1,()=>{for(let i=0;i<8;i++)at(ctx,0,0,1,()=>round(ctx,-5,-r-4,10,11,2,color,C.ink,2),i*Math.PI/4);ellipse(ctx,0,0,r,r,color,C.ink,3);ellipse(ctx,0,0,r*.35,r*.35,C.cream,C.ink,3)},angle)}
export function sheet(ctx,x,y,w,h,{id='',lines=[],accent=C.yellow,angle=0,stamp='',progress=1}={}){
 at(ctx,x,y,1,()=>{round(ctx,-w/2,-h/2,w,h,9,C.cream,C.ink,3,5);
 line(ctx,[[-w/2+18,-h/2+64],[w/2-18,-h/2+64]],C.line,2);
 round(ctx,-w/2+12,-h/2-13,Math.min(w-24,96),38,8,accent,C.ink,3);
 ink(ctx,id,-w/2+27,-h/2+6,23,C.ink,{width:w-42});
 let yy=-h/2+92;for(const s of lines){const n=wrap(ctx,s,-w/2+19,yy,w-38,25);yy+=n*34+10}
 if(!lines.length)for(let i=0;i<3;i++)line(ctx,[[-w/2+20,-h/2+92+i*28],[w/2-26,-h/2+92+i*28]],C.line,3);
 if(stamp)label(ctx,stamp,0,h/2-24,{size:23,fill:accent,height:37,angle:-.1,shadow:2});
 // folded paper corner, not a separate UI header
 ctx.fillStyle='#E4DECD';ctx.beginPath();ctx.moveTo(w/2-24,-h/2);ctx.lineTo(w/2-24,-h/2+24);ctx.lineTo(w/2,-h/2+24);ctx.closePath();ctx.fill();
 },angle)
}
export function clipboard(ctx,x,y,{goal='让测试通过',done=false}={}){
 at(ctx,x,y,1,()=>{shadow(ctx,12,132,126,17);round(ctx,-128,-126,256,243,12,C.cream,C.ink,4,7);
 round(ctx,-63,-149,126,39,8,C.yellow,C.ink,3);ink(ctx,'任务',0,-85,27,C.muted,{align:'center'});
 wrap(ctx,goal,0,-29,229,30,C.ink,'center');line(ctx,[[-100,54],[100,54]],C.line,2);ink(ctx,'观察 → 行动',0,82,25,C.ink,{align:'center'});
 if(done){ellipse(ctx,111,-100,35,35,C.teal,C.ink,4);check(ctx,111,-101,.85)}
 },-.035)
}
export function notebook(ctx,x,y,{feedback='',state='idle'}={}){
 at(ctx,x,y,1,()=>{for(let k=3;k>0;k--)round(ctx,-81+k*5,-68-k*4,165,141,10,'#ECE8DA',C.ink,2);
 round(ctx,-84,-66,169,142,10,C.cream,C.ink,3,4);round(ctx,-88,-93,179,39,10,state==='pass'?C.teal:C.yellow,C.ink,3);
 ink(ctx,'上下文',0,-74,24,C.ink,{align:'center'});ink(ctx,'观察记录',0,-23,23,C.muted,{align:'center'});
 ink(ctx,feedback||'等待反馈',0,30,26,state==='fail'?C.red:state==='pass'?'#087B70':C.ink,{align:'center',width:153});
 },-.07)
}
export function terminal(ctx,x,y,t,c,{working=false,state='idle',patched=false,progress=0}={}){
 at(ctx,x+(working?Math.sin(t*42)*1.5:0),y,1,()=>{
 machine(ctx,0,0,t,{state:'idle'});
 round(ctx,-163,-164,316,240,20,C.ink,null);
 ink(ctx,'CODE + TEST',-138,-137,20,'#A9BBBB',{mono:true});line(ctx,[[-138,-115],[132,-115]],'#526162',2);
 ink(ctx,c.action,-134,-79,30,C.cream,{mono:true,width:280});
 ink(ctx,patched?c.after:c.before,-134,-27,24,patched?C.teal:C.orange,{mono:true,width:290});
 if(state==='fail'){cross(ctx,-117,30,.8,C.red);ink(ctx,c.failure,-84,30,35,C.red,{mono:true,width:180})}
 else if(state==='pass'){check(ctx,-118,31,.7,C.teal);ink(ctx,c.success,-81,30,35,C.teal,{mono:true,width:180})}
 else if(state==='patching'){ink(ctx,'正在修改',-132,28,28,C.yellow)}
 else if(state==='patch'){ink(ctx,'修改已应用',-132,28,28,C.yellow)}
 else if(working){ink(ctx,'RUNNING',-135,27,26,C.yellow,{mono:true});for(let k=0;k<3;k++)ellipse(ctx,55+k*23,26,5,5,Math.floor(t*7)%3===k?C.yellow:'#63706D')}
 else ink(ctx,'READY',-134,27,27,'#96ACA6',{mono:true});
 if(working){for(let k=0;k<4;k++)round(ctx,-139+k*49,117,34,22,5,k===Math.floor(t*8)%4?C.yellow:'#D6E1D6',C.ink,2)}
 if(state==='patching'){line(ctx,[[-136,0],[130,0]],C.yellow,4);gear(ctx,212,-106,26,progress*3,C.yellow)}
 });
}
export function archive(ctx,x,y,t,docs,{scan=0,selected=false}={}){
 at(ctx,x,y,1,()=>{shadow(ctx,15,270,265,23);
 // ink extrusion, outer case, inset panel and lower card catalog
 ctx.fillStyle='#B99061';ctx.strokeStyle=C.ink;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(220,-227);ctx.lineTo(250,-207);ctx.lineTo(250,246);ctx.lineTo(220,262);ctx.closePath();ctx.fill();ctx.stroke();
 round(ctx,-226,-228,451,478,24,'#E8BF86',C.ink,5,4);round(ctx,-206,-199,411,270,12,'#796D5F',C.ink,3);
 round(ctx,-163,-252,326,46,10,C.yellow,C.ink,4,3);ink(ctx,'知识档案 · 原件',0,-230,27,C.ink,{align:'center'});
 docs.forEach((d,i)=>{let bx=-135+i*135;const good=selected&&d.selected;
  const a=good?-.025:0;at(ctx,bx,-63,1,()=>{
   round(ctx,-52,-115,104,219,7,[C.teal,C.blue,C.orange][i],C.ink,4,4);round(ctx,-41,-106,16,199,2,'#FFFFFF25',null);
   round(ctx,-21,-81,57,51,7,C.cream,C.ink,3);ink(ctx,d.id,8,-56,24,C.ink,{align:'center',width:54});
   line(ctx,[[-9,-7],[29,-7]],C.ink,3);line(ctx,[[-9,15],[22,15]],C.ink,3);ellipse(ctx,7,62,14,14,C.cream,C.ink,3);
   if(good){ellipse(ctx,34,-115,22,22,C.yellow,C.ink,3);check(ctx,34,-114,.55)}
   if(selected&&!d.selected){ctx.globalAlpha=.35;round(ctx,-55,-118,111,228,9,C.paper,null);ctx.globalAlpha=1}
  },a)
 });
 line(ctx,[[-211,83],[212,83]],C.ink,8);
 for(let i=0;i<2;i++){round(ctx,-194+i*201,111,180,94,9,'#F4D9B4',C.ink,3,3);round(ctx,-140+i*201,136,72,24,6,C.cream,C.ink,2);line(ctx,[[-144+i*201,178],[-66+i*201,178]],C.ink,5)}
 for(const sx of [-207,206])for(const sy of [-210,227])screw(ctx,sx,sy);
 if(scan>0&&scan<1){const mx=lerp(-153,153,scan);at(ctx,mx,-72,1,()=>{ellipse(ctx,0,0,56,56,'#FFF9D538',C.ink,6);ellipse(ctx,-7,-9,39,39,null,C.yellow,3);line(ctx,[[40,41],[81,93]],C.ink,17);line(ctx,[[43,43],[78,86]],C.orange,10)})}
 });
}
export function binder(ctx,x,y,{question='',docs=[],opened=1}={}){
 at(ctx,x,y,1,()=>{shadow(ctx,7,197,248,21);
 // Two separate pages, sewn spine, metal rings and a cover protruding beyond paper.
 round(ctx,-218,-174,436,361,15,C.purple,C.ink,5,7);
 round(ctx,-204,-163,201,334,10,C.cream,C.ink,3);round(ctx,3,-163,201,334,10,C.cream,C.ink,3);
 round(ctx,-13,-161,26,332,5,'#D6D0BA',C.ink,2);
 for(let k=0;k<4;k++){ellipse(ctx,0,-120+k*79,22,8,null,C.ink,4);line(ctx,[[-15,-126+k*79],[14,-126+k*79]],C.cream,3)}
 round(ctx,-193,-192,168,40,8,C.yellow,C.ink,3);ink(ctx,'本次上下文',-109,-173,23,C.ink,{align:'center'});
 ink(ctx,'问题',-174,-125,25,C.muted);wrap(ctx,question,-174,-78,149,26);
 line(ctx,[[-174,36],[-41,36]],C.line,2);ink(ctx,'不是训练',-174,80,23,C.muted);
 if(!docs.length){ink(ctx,'待放入',35,-48,25,C.muted);ink(ctx,'相关证据',35,-4,25,C.muted)}
 docs.forEach((d,i)=>{const yy=-115+i*139;round(ctx,26,yy-18,151,111,8,i? '#FFE8CD':'#DFF6EF',C.ink,2,2);
  ink(ctx,d.id,40,yy+4,22,C.ink,{width:118});wrap(ctx,d.text,40,yy+43,123,22);
 });
 });
}
export function press(ctx,x,y,t,{working=false,ready=false,progress=0,answer='',citations=[]}={}){
 at(ctx,x,y,1,()=>{shadow(ctx,10,261,202,21);
 ctx.fillStyle='#776AAC';ctx.strokeStyle=C.ink;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(157,-193);ctx.lineTo(191,-169);ctx.lineTo(191,201);ctx.lineTo(157,219);ctx.closePath();ctx.fill();ctx.stroke();
 round(ctx,-163,-198,326,414,27,C.purple,C.ink,5,4);
 round(ctx,-140,-175,280,144,19,C.ink,C.ink,4);ink(ctx,'LLM',0,-125,49,C.cream,{align:'center',mono:true});
 ink(ctx,working?'根据证据生成':ready?'回答已生成':'等待上下文',0,-69,25,working?C.yellow:ready?C.teal:'#B0BCB5',{align:'center',width:260});
 for(let i=0;i<3;i++)ellipse(ctx,-102+i*38,0,9,9,working&&i===Math.floor(t*5)%3?C.yellow:C.cream,C.ink,2);
 gear(ctx,93,2,23,working?t*3:0,C.yellow);
 round(ctx,-128,48,255,25,9,C.ink,C.ink,3);
 const feed=ready?1:working?progress:0;
 if(feed>0){ctx.save();ctx.beginPath();ctx.rect(-129,63,271,178);ctx.clip();
 round(ctx,-115,72-155*(1-feed),230,157,5,C.cream,C.ink,3,2);
 const py=72-155*(1-feed);if(ready){wrap(ctx,answer,0,py+35,202,27,C.ink,'center');ink(ctx,citations.map(x=>'['+x+']').join(' '),0,py+121,23,'#117E71',{align:'center',width:210})}
 else {line(ctx,[[-90,py+39],[91,py+39]],C.line,4);line(ctx,[[-90,py+73],[63,py+73]],C.line,4)}
 ctx.restore()}
 for(const sx of [-144,141])for(const sy of [-182,190])screw(ctx,sx,sy);
 line(ctx,[[-143,89],[-129,89]],C.ink,5);line(ctx,[[128,89],[142,89]],C.ink,5);
 });
}
export function kiosk(ctx,x,y,{request='',responses=0}={}){
 at(ctx,x,y,1,()=>{shadow(ctx,7,256,159,20);round(ctx,-86,149,170,78,13,C.orange,C.ink,5,5);round(ctx,-131,217,263,25,10,C.cream,C.ink,4,3);
 round(ctx,-144,-156,289,334,28,C.orange,C.ink,5,6);round(ctx,-123,-129,248,178,18,C.ink,C.ink,4);
 ink(ctx,'APP',0,-88,43,C.cream,{align:'center',mono:true});wrap(ctx,request,0,-26,213,27,C.cream,'center');
 round(ctx,-120,79,185,56,12,C.cream,C.ink,3);ink(ctx,'返回 '+responses+' 次',-26,106,25,C.ink,{align:'center'});
 ellipse(ctx,98,106,20,20,responses?C.teal:C.yellow,C.ink,4);
 for(let k=0;k<3;k++)line(ctx,[[-44+k*28,160],[-26+k*28,160]],C.ink,3);
 for(const sx of [-130,131])for(const sy of [-140,156])screw(ctx,sx,sy);
 });
}
export function cacheDrawer(ctx,x,y,{open=0,filled=false,key='',value='',status=''}={}){
 at(ctx,x,y,1,()=>{shadow(ctx,17,235+open*42,248,24);
 // opening exposes the cavity, preserving the same drawer and label.
 ctx.fillStyle='#279990';ctx.strokeStyle=C.ink;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(202,-159);ctx.lineTo(238,-132);ctx.lineTo(238,183);ctx.lineTo(202,205);ctx.closePath();ctx.fill();ctx.stroke();
 round(ctx,-210,-164,420,367,25,C.teal,C.ink,5,5);round(ctx,-177,-117,354,221,14,'#223638',C.ink,4);
 round(ctx,-143,-193,286,49,9,C.yellow,C.ink,4,3);ink(ctx,'CACHE · 快取柜',0,-167,27,C.ink,{align:'center'});
 if(filled){sheet(ctx,0,-29+open*27,264,137,{id:'键 → 值',accent:C.yellow,lines:[]});ink(ctx,key,0,-41+open*27,26,C.ink,{align:'center',mono:true,width:244});ink(ctx,value,0,1+open*27,33,'#147C70',{align:'center',width:230})}
 else if(open>.3){ink(ctx,'空',0,-35,41,'#CBDDD5',{align:'center'});line(ctx,[[-27,0],[27,0]],'#7D9390',4)}
 const yy=lerp(-82,109,open);round(ctx,-174,yy,349,195-80*open,12,'#69D5C0',C.ink,4,4);
 line(ctx,[[-158,yy+14],[153,yy+14]],'#DAFFF0',4);round(ctx,-63,yy+39,126,32,10,C.cream,C.ink,4);
 if(open<.55){ink(ctx,filled?'已保存键值':'先查这里',0,yy+108,31,C.ink,{align:'center'})}
 for(const sx of [-191,189])for(const sy of [-143,181])screw(ctx,sx,sy);
 if(status)label(ctx,status,145,-216,{fill:status==='MISS'?C.red:C.yellow,size:30,shadow:4,angle:.06});
 });
}
export function vault(ctx,x,y,t,{reads=0,working=false,value=''}={}){
 at(ctx,x,y,1,()=>{shadow(ctx,12,253,184,23);
 round(ctx,-157,-173,314,369,17,C.purple,C.ink,5,5);ellipse(ctx,0,-174,158,47,'#C9C1EA',C.ink,5);
 for(let k=0;k<3;k++){const yy=-57+k*102;ctx.save();ctx.beginPath();ctx.rect(-164,yy-2,333,57);ctx.clip();ellipse(ctx,0,yy,158,45,C.purple,C.ink,4);ctx.restore()}
 line(ctx,[[-131,-118],[-131,161]],'#DDD7ED',4);
 for(let k=0;k<3;k++){ellipse(ctx,106,-67+k*91,8,8,working?C.yellow:C.teal,C.ink,2);line(ctx,[[-92,-55+k*91],[-26,-55+k*91]],C.ink,5)}
 round(ctx,-115,-204,230,55,9,C.cream,C.ink,4,3);ink(ctx,'DATABASE',0,-176,28,C.ink,{align:'center',mono:true});
 round(ctx,-121,77,226,71,11,C.ink,C.ink,3);ink(ctx,'读取 '+reads+' 次',-7,111,31,C.yellow,{align:'center'});
 if(working){gear(ctx,-67,-6,34,t*3,C.yellow);gear(ctx,6,10,24,-t*4,C.orange)}
 if(reads)label(ctx,value,0,220,{fill:C.yellow,size:25,shadow:3});
 });
}
