// Draft scaffold. The host coding agent replaces this with the actual mechanism.
import {C,text} from './runtime/drawing.mjs';
const spec=window.__PROJECT__ ?? await(await fetch('./project.json')).json();
const canvas=document.getElementById('stage');canvas.width=spec.width;canvas.height=spec.height;
const ctx=canvas.getContext('2d');window.videoMeta=spec;
window.renderFrame=(frame)=>{
 ctx.setTransform(1,0,0,1,0,0);ctx.fillStyle=C.paper;ctx.fillRect(0,0,canvas.width,canvas.height);
 text(ctx,spec.title,80,170,60,C.ink);
 text(ctx,'DRAFT — design the mechanism before rendering',80,300,30,C.muted);
 window.semanticState={frame,draft:true};
};
await document.fonts.ready;window.ready=true;window.renderFrame(0);
