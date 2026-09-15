/* Pure frame-seekable SVG player. No network, eval, simulations or canned artwork. MIT. */
function mountTopicPlayer(spec, slots, textSlots) {
  const count = Math.round(spec.duration * spec.fps);
  const stage = document.getElementById('stage');
  const seek = document.getElementById('seek');
  const button = document.getElementById('toggle');
  const clock = document.getElementById('clock');
  let frame = 0, playing = false, origin = 0;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  function state(layer, f) {
    const type = layer.type || 'image', slot = layer.slot || 'center';
    let x, y;
    if (type === 'text' && textSlots[slot]) [x, y] = textSlots[slot];
    else { const b=slots[slot]; x=b[0]+b[2]/2; y=b[1]+b[3]/2; }
    let base = {x:x*spec.width, y:y*spec.height, scale:layer.scale ?? 1,
      rotate:layer.rotate ?? 0, opacity:layer.opacity ?? 1};
    let last = {...base};
    const points=(layer.keys || []).map(k => {
      const p={...last};
      if(k.slot) {const b=slots[k.slot];p.x=(b[0]+b[2]/2)*spec.width;p.y=(b[1]+b[3]/2)*spec.height;}
      for(const name of ['scale','rotate','opacity']) if(name in k)p[name]=k[name];
      last=p;return [k.frame,p];
    });
    if(points.length) {
      if(f<=points[0][0])base={...points[0][1]};
      else if(f>=points.at(-1)[0])base={...points.at(-1)[1]};
      else for(let i=1;i<points.length;i++) {
        const [a,p]=points[i-1], [b,q]=points[i];
        if(a<=f&&f<=b) {let u=(f-a)/(b-a);u=u*u*(3-2*u);
          for(const k of Object.keys(p))base[k]=p[k]+(q[k]-p[k])*u;break;}
      }
    }
    base.opacity *= f>=(layer.start??0)&&f<(layer.end??count)?1:0;
    return base;
  }
  function render(f) {
    frame=clamp(Math.round(f),0,count-1);
    const states={};
    for(const layer of spec.layers) {
      const s=state(layer,frame), node=document.getElementById(layer.id);states[layer.id]=s;
      node.setAttribute('opacity',String(s.opacity));
      if(layer.type!=='path')node.setAttribute('transform',`translate(${s.x} ${s.y}) rotate(${s.rotate}) scale(${s.scale})`);
    }
    const shot=spec.shots.find(s=>s.start<=frame&&frame<s.end);
    document.getElementById('_caption').textContent=shot.caption;
    seek.value=frame;clock.textContent=`${(frame/spec.fps).toFixed(2)} / ${spec.duration.toFixed(2)} s`;
    window.semanticState={frame,shot:shot.id,action:shot.action,change:shot.change,layers:states};
    return window.semanticState;
  }
  function stop(){playing=false;button.textContent='播放';}
  function tick(now){if(!playing)return;render((now-origin)*spec.fps/1000);if(frame===count-1)stop();else requestAnimationFrame(tick);}
  seek.max=count-1;seek.addEventListener('input',()=>{stop();render(Number(seek.value));});
  button.addEventListener('click',()=>{if(playing)stop();else{if(frame===count-1)frame=0;origin=performance.now()-frame/spec.fps*1000;playing=true;button.textContent='暂停';requestAnimationFrame(tick);}});
  window.renderFrame=render;window.videoMeta=spec;
  const images=[...stage.querySelectorAll('image')].map(node=>new Promise((resolve,reject)=>{
    const image=new Image();image.onload=resolve;image.onerror=()=>reject(new Error('ASSET_BLOCKED: image failed to decode'));image.src=node.getAttribute('href');
  }));
  Promise.all([document.fonts.ready,...images]).then(()=>{render(0);window.ready=true;}).catch(e=>{window.renderError=String(e);});
}
