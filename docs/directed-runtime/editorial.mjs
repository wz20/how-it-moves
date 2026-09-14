/** Original directing primitives: persistent IDs, bounded focus, reveal and transfer. MIT. */
import {clamp, lerp, smooth, easeInOut} from './motion.mjs';
export const P = Object.freeze({paper:'#F7F8FA', ink:'#23354C', muted:'#718094', line:'#C8D5E2', blue:'#2466B5', blueLight:'#E2EFFB', green:'#247967', greenLight:'#E4F3EA', purple:'#79609B', purpleLight:'#EEE9F7', amber:'#AE6936', amberLight:'#F9ECDD', white:'#FFFFFF'});
export const between = (f,a,b) => b<=a ? (f>=b?1:0) : clamp((f-a)/(b-a));
export const mixBox = (a,b,t) => a.map((v,i)=>lerp(v,b[i],clamp(t)));
export function shotAt(shots, frame) {
  return shots.find(s=>frame>=s.start_frame && frame<s.end_frame) || shots.at(-1);
}
export function fitCamera(box, view=[60,245,1800,635], maxScale=1.25, padding=50) {
  if (![...box,...view,maxScale,padding].every(Number.isFinite) || box[2]<=0 || box[3]<=0 || view[2]<=0 || view[3]<=0 || maxScale<=0 || padding<0) throw new Error('Invalid camera bounds');
  const s=Math.min(maxScale,view[2]/(box[2]+padding*2),view[3]/(box[3]+padding*2));
  return {s,x:view[0]+view[2]/2-(box[0]+box[2]/2)*s,y:view[1]+view[3]/2-(box[1]+box[3]/2)*s};
}
export const mixCamera = (a,b,t) => ({s:lerp(a.s,b.s,t),x:lerp(a.x,b.x,t),y:lerp(a.y,b.y,t)});
export function withCamera(ctx,c,draw) {ctx.save();ctx.translate(c.x,c.y);ctx.scale(c.s,c.s);draw();ctx.restore();}
export function reveal(ctx,box,progress,draw) {ctx.save();ctx.beginPath();ctx.rect(box[0]-5,box[1]-5,box[2]+10,(box[3]+10)*clamp(progress));ctx.clip();draw();ctx.restore();}
export function rounded(ctx,box,{fill=P.white,stroke=P.ink,width=3,r=18}={}) {
  ctx.beginPath();ctx.roundRect(...box,r);if(fill){ctx.fillStyle=fill;ctx.fill()}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=width;ctx.stroke()}
}
export function text(ctx,str,x,y,size=32,color=P.ink,{align='left',weight=700,mono=false,width,issues=null}={}) {
  ctx.save();ctx.font=`${weight} ${size}px ${mono?'"DejaVu Sans Mono",monospace':'"Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif'}`;
  ctx.textBaseline='middle';ctx.textAlign=align;ctx.fillStyle=color;
  const measured=ctx.measureText(String(str)).width;
  if(issues && ctx.globalAlpha>.1 && width && measured>width+.5) issues.push({type:'text_overflow',text:String(str),measured,allowed:width});
  ctx.fillText(String(str),x,y);ctx.restore();return measured;
}
export function circle(ctx,x,y,r,fill=P.white,stroke=P.ink,lw=3) {ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);if(fill){ctx.fillStyle=fill;ctx.fill()}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=lw;ctx.stroke()}}
export function routePoint(points,u) {
  const lengths=points.slice(1).map((p,i)=>Math.hypot(p[0]-points[i][0],p[1]-points[i][1]));
  const total=lengths.reduce((a,b)=>a+b,0);if(!total)return points[0];
  let remaining=clamp(u)*total;
  for(let i=0;i<lengths.length;i++){if(remaining<=lengths[i] || i===lengths.length-1){const q=lengths[i]?remaining/lengths[i]:0;return [lerp(points[i][0],points[i+1][0],q),lerp(points[i][1],points[i+1][1],q)]}remaining-=lengths[i]}
  return points.at(-1);
}
export function trace(ctx,points,{color=P.line,width=4,progress=1,dash=[]}={}) {
  ctx.save();ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineCap='round';ctx.lineJoin='round';ctx.setLineDash(dash);ctx.beginPath();
  for(let i=0;i<=60;i++){const p=routePoint(points,i/60*clamp(progress));i?ctx.lineTo(...p):ctx.moveTo(...p)}ctx.stroke();ctx.restore();
}
export function parcel(ctx,points,frame,event,{label='Q1',color=P.blue,fill=P.blueLight}={}) {
  if(frame<event.start_frame || frame>=event.end_frame)return null;
  const u=between(frame,event.start_frame,event.end_frame),p=routePoint(points,u);
  trace(ctx,points,{color,width:5,progress:u});
  rounded(ctx,[p[0]-31,p[1]-20,62,40],{fill,stroke:color,r:10,width:2.5});text(ctx,label,p[0],p[1],20,color,{align:'center',mono:true});
  return p;
}
export function magnifier(ctx,x,y,r=21,color=P.blue) {
  circle(ctx,x,y,r,null,color,4);trace(ctx,[[x+r*.72,y+r*.72],[x+r*1.4,y+r*1.4]],{color,width:6});
}
export function picture(ctx,x,y,w,h,color=P.blue) {
  rounded(ctx,[x,y,w,h],{fill:P.blueLight,stroke:color,r:8,width:2});circle(ctx,x+w*.75,y+h*.25,h*.085,P.white,null);
  ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(x+5,y+h-5);ctx.lineTo(x+w*.38,y+h*.28);ctx.lineTo(x+w*.6,y+h*.65);ctx.lineTo(x+w*.77,y+h*.45);ctx.lineTo(x+w-5,y+h-5);ctx.closePath();ctx.fill();
}
export function semanticAt(spec,frame) {
  const E=Object.fromEntries(spec.events.map(e=>[e.id,e]));const dir=spec.direction,cfg=dir.config;
  const returned=cfg.segments.filter(s=>frame>=E['return_'+s.id].end_frame).map(s=>s.id);
  const rankReady=frame>=E.rank.end_frame;
  return {frame,shot:shotAt(dir.shots,frame).id,queryId:dir.query_id,selected:frame>=E.choose.end_frame?cfg.selected_group:null,
    expanded:frame>=E.expand.end_frame,returned,ranking:frame>=E.rank.start_frame,rankedIds:rankReady?dir.ranked.map(r=>r.id):[],
    answerIds:frame>=E.deliver.end_frame?dir.ranked.slice(0,cfg.top_k).map(r=>r.id):[],stopped:frame>=E.deliver.end_frame};
}

/** Collapse before relocation, then expand: prevents interpolating big overlapping cards. */
export function stagedReflow(a,b,t) {
 const center=r=>[r[0]+r[2]/2,r[1]+r[3]/2];const ac=center(a),bc=center(b);
 const small=c=>[c[0]-72,c[1]-32,144,64];
 if(t<.3)return mixBox(a,small(ac),smooth(t/.3));
 if(t<.75)return mixBox(small(ac),small(bc),smooth((t-.3)/.45));
 return mixBox(small(bc),b,smooth((t-.75)/.25));
}
