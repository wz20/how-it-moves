/** Original jointed cartoon rigs. Every face/arm/tool response is frame driven. */
import {C,round,line,ellipse,text,label,dots,check,cross} from './drawing.mjs';
import {clamp,pulse} from './motion.mjs';
export function robot(ctx,x,y,t,{mode='idle',reach=0,recoil=0,success=0,look=1,think=0}={}){
 ctx.save();ctx.translate(x,y);
 ellipse(ctx,0,198,146,23,'#22252B12');
 const bob=Math.sin(t*3)*3+success*-10;
 ctx.translate(recoil*-15,bob);ctx.rotate(recoil*.035);
 // two springy legs and big work shoes
 for(const s of [-1,1]){round(ctx,s*62-24,105,48,67,20,C.ink,null);line(ctx,[[s*62-20,139],[s*62+20,139]],C.muted,4);round(ctx,s*62-49,157,99,39,18,C.cream,C.ink,5,3);line(ctx,[[s*62-25,166],[s*62+10,166]],C.line,4)}
 // left elbow / jointed cable arm
 ctx.save();ctx.lineCap='round';
 const leftHand={x:-149-think*15,y:35-think*190};
 ctx.strokeStyle=C.ink;ctx.lineWidth=31;ctx.beginPath();ctx.moveTo(-98,-12);ctx.quadraticCurveTo(-194,2,leftHand.x,leftHand.y);ctx.stroke();
 ctx.strokeStyle=C.cream;ctx.lineWidth=17;ctx.beginPath();ctx.moveTo(-98,-12);ctx.quadraticCurveTo(-194,2,leftHand.x,leftHand.y);ctx.stroke();
 ellipse(ctx,leftHand.x,leftHand.y,30,29,C.cream,C.ink,5);
 line(ctx,[[leftHand.x-13,leftHand.y-6],[leftHand.x+11,leftHand.y-6]],C.ink,3);ctx.restore();
 // right arm anticipates then points to the tool
 let hx=147+reach*63,hy=28-reach*96-success*100;
 ctx.strokeStyle=C.ink;ctx.lineWidth=32;ctx.beginPath();ctx.moveTo(91,-8);ctx.quadraticCurveTo(165,44-reach*85,hx,hy);ctx.stroke();
 ctx.strokeStyle=C.cream;ctx.lineWidth=18;ctx.beginPath();ctx.moveTo(91,-8);ctx.quadraticCurveTo(165,44-reach*85,hx,hy);ctx.stroke();
 ctx.save();ctx.translate(hx,hy);ctx.rotate(-reach*.45);round(ctx,-24,-22,53,44,17,C.cream,C.ink,5);if(reach>.2)round(ctx,6,-31,54,21,10,C.cream,C.ink,4);line(ctx,[[-12,0],[6,0]],C.ink,3);ctx.restore();
 // torso with ink outline, cel highlight, exposed controls
 round(ctx,-103,-37,206,167,39,C.orange,C.ink,6,6);
 ctx.save();ctx.beginPath();ctx.roundRect(-103,-37,206,167,39);ctx.clip();dots(ctx,37,-10,76,140,{step:10,r:1.7,alpha:.17});ctx.restore();
 round(ctx,-77,-14,153,75,16,C.cream,C.ink,4);text(ctx,'LLM',0,24,44,C.ink,{align:'center',font:'mono'});
 ellipse(ctx,-55,94,10,10,C.teal,C.ink,3);ellipse(ctx,-21,94,10,10,C.yellow,C.ink,3);line(ctx,[[18,88],[69,88]],C.ink,5);line(ctx,[[18,100],[57,100]],C.ink,5);
 round(ctx,-38,-76,76,38,13,C.ink,C.ink,4);
 // head: angular monitor case, side ear cups, cell-shaded front
 const nod=think*-.08+reach*.028-success*.055;
 ctx.save();ctx.translate(0,-165);ctx.rotate(nod);
 round(ctx,-160,-30,43,83,17,C.teal,C.ink,5,2);round(ctx,117,-30,43,83,17,C.teal,C.ink,5,2);
 round(ctx,-136,-96,272,197,41,C.cream,C.ink,6,7);
 ctx.save();ctx.beginPath();ctx.roundRect(-136,-96,272,197,41);ctx.clip();round(ctx,116,-92,25,190,0,'#DBE6DD',null);dots(ctx,-125,72,239,35,{step:9,r:1.3,alpha:.1});ctx.restore();
 round(ctx,-111,-70,222,137,27,C.ink,C.ink,4);
 // display gleam
 ctx.save();ctx.globalAlpha=.09;ctx.fillStyle='#FFFFFF';ctx.beginPath();ctx.moveTo(-99,-63);ctx.lineTo(-25,-63);ctx.lineTo(-95,43);ctx.lineTo(-109,43);ctx.closePath();ctx.fill();ctx.restore();
 const blink=(t%3.7>3.54)?Math.max(.1,Math.abs(t%3.7-3.62)/.08):1;
 for(const s of [-1,1]){
  let ex=s*47+look*7,ey=-10;ctx.fillStyle=C.teal;
  if(success>.3){ctx.strokeStyle=C.teal;ctx.lineWidth=9;ctx.lineCap='round';ctx.beginPath();ctx.arc(ex,6,21,Math.PI*1.13,Math.PI*1.88);ctx.stroke()}
  else {round(ctx,ex-15,ey-23*blink,30,46*blink,13,C.teal,null);if(think>.2)line(ctx,[[ex-19,-43-s*6],[ex+17,-43+s*6]],C.yellow,5)}
 }
 if(success>.3){line(ctx,[[-16,40],[0,49],[16,40]],C.teal,5)}else line(ctx,[[-13,37],[13,37]],C.teal,5);
 // antenna follows head
 line(ctx,[[0,-96],[0,-131],[22,-147+Math.sin(t*7)*2]],C.ink,6);ellipse(ctx,22,-148+Math.sin(t*7)*2,15,15,think>.2?C.yellow:C.orange,C.ink,4);
 line(ctx,[[-27,83],[27,83]],C.line,6);ctx.restore();
 ctx.restore();
}
export function machine(ctx,x,y,t,{state='idle',working=0,patch=0,impact=0}={}){
 ctx.save();ctx.translate(x+Math.sin(t*53)*working*1.7,y+impact*-8);
 ellipse(ctx,18,219,211,22,'#22252B12');
 // side extrusion makes this a physical executable tool, not a dashboard card
 ctx.fillStyle='#2B948D';ctx.strokeStyle=C.ink;ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(176,-195);ctx.lineTo(214,-161);ctx.lineTo(214,190);ctx.lineTo(176,206);ctx.closePath();ctx.fill();ctx.stroke();
 round(ctx,-192,-195,374,397,35,C.teal,C.ink,6,0);
 round(ctx,-167,-168,324,248,22,C.ink,C.ink,5);
 // screws
 for(const sx of [-175,164])for(const sy of [-177,180]){ellipse(ctx,sx,sy,6,6,C.cream,C.ink,2);line(ctx,[[sx-3,sy-3],[sx+3,sy+3]],C.ink,2)}
 text(ctx,'CODE + TEST',-138,-137,20,'#9DAEAE',{font:'mono',weight:700});
 line(ctx,[[-138,-115],[132,-115]],'#455555',2);
 text(ctx,'add(2, 3)',-136,-76,30,C.cream,{font:'mono'});
 text(ctx,patch>.5?'return a + b':'return a - b',-135,-27,24,patch>.5?C.teal:C.orange,{font:'mono'});
 if(state==='fail'){cross(ctx,-117,31,.85,C.red);text(ctx,'FAIL',-81,30,38,C.red,{font:'mono'});text(ctx,'-1 ≠ 5',125,32,21,C.cream,{align:'right',font:'mono'})}
 else if(state==='pass'){check(ctx,-118,31,.7,C.teal);text(ctx,'PASS',-81,30,38,C.teal,{font:'mono'});text(ctx,'5 = 5',126,32,23,C.cream,{align:'right',font:'mono'})}
 else if(state==='patch'){text(ctx,'PATCH APPLIED',0,33,27,C.yellow,{font:'mono',align:'center'})}
 else if(working){text(ctx,'RUNNING',-135,29,26,C.yellow,{font:'mono'});for(let k=0;k<3;k++)ellipse(ctx,40+k*22,28,5,5,((t*6|0)%3===k)?C.yellow:'#52615C')}
 else text(ctx,'READY',0,29,30,'#749A92',{font:'mono',align:'center'});
 // front control deck
 round(ctx,-155,105,228,48,14,C.cream,C.ink,4);
 for(let i=0;i<4;i++)round(ctx,-139+i*49,117,34,22,5,(working&&i===(t*8|0)%4)?C.yellow:'#D6E1D6',C.ink,2);
 ellipse(ctx,113,128,28,28,C.yellow,C.ink,5);line(ctx,[[113,113],[113,126]],C.ink,4);
 round(ctx,-112,173,220,17,7,C.ink,C.ink,2);
 // a conveyor/reel is animated only while executing
 for(let sx of [-139,146]){ctx.save();ctx.translate(sx,181);ctx.rotate(t*working*7);ellipse(ctx,0,0,17,17,C.cream,C.ink,4);line(ctx,[[-10,0],[10,0]],C.ink,3);line(ctx,[[0,-10],[0,10]],C.ink,3);ctx.restore()}
 ctx.restore();
}
