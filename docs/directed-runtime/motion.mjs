/** Deterministic motion primitives. Time is seconds; no mutable simulation. MIT. */
export const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
export const lerp=(a,b,t)=>a+(b-a)*t;
export const inv=(t,a,b)=>clamp((t-a)/(b-a));
export const smooth=t=>{t=clamp(t);return t*t*(3-2*t)};
export const easeOut=t=>1-Math.pow(1-clamp(t),3);
export const easeInOut=t=>{t=clamp(t);return t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2};
export const backOut=t=>{t=clamp(t)-1;return 1+2.25*t*t*t+1.25*t*t};
export function spring(t,{frequency=3.4,damping=8}={}){return t<=0?0:1-Math.exp(-damping*t)*Math.cos(2*Math.PI*frequency*t)}
export function envelope(t,start,end,ramp=.2){return smooth(inv(t,start,start+ramp))*(1-smooth(inv(t,end-ramp,end)))}
export const pulse=(t,start,duration=.7)=>t<start||t>start+duration?0:Math.sin(Math.PI*(t-start)/duration)*Math.exp(-2*(t-start));
export function bezier(points,u){u=clamp(u);const q=1-u;return {x:q*q*q*points[0][0]+3*q*q*u*points[1][0]+3*q*u*u*points[2][0]+u*u*u*points[3][0],y:q*q*q*points[0][1]+3*q*q*u*points[1][1]+3*q*u*u*points[2][1]+u*u*u*points[3][1]}}
export function tangent(points,u){const a=bezier(points,clamp(u-.002)),b=bezier(points,clamp(u+.002));return Math.atan2(b.y-a.y,b.x-a.x)}
export function keyframes(t,keys){if(t<=keys[0][0])return keys[0][1];for(let i=1;i<keys.length;i++){if(t<=keys[i][0])return lerp(keys[i-1][1],keys[i][1],smooth(inv(t,keys[i-1][0],keys[i][0])))}return keys.at(-1)[1]}
export function rng(seed=12345){let s=seed>>>0;return()=>{s=(Math.imul(s,1664525)+1013904223)>>>0;return s/4294967296}}
