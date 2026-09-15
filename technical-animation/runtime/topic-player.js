/* Pure frame-seekable SVG player. No network, eval, simulations or canned artwork. MIT. */
function mountTopicPlayer(spec, slots, textSlots) {
  const count = Math.round(spec.duration * spec.fps);
  const stage = document.getElementById('stage');
  const seek = document.getElementById('seek');
  const button = document.getElementById('toggle');
  const clock = document.getElementById('clock');
  let frame = 0, playing = false, origin = 0, reviewView = 'full', eventEnd = null;
  const audioTracks=(spec.audio_tracks||[]).map((track)=>{
    const el=new Audio();el.preload='auto';el.volume=track.gain;el.src=track.src;
    return {el,track};
  });
  function syncAudio(force=false){
    const now=frame/spec.fps;
    for(const {el,track} of audioTracks){
      const active=now>=track.start&&now<track.start+track.trim_out-track.trim_in;
      const wanted=active?now-track.start+track.trim_in:track.trim_in;
      if(active&&(force||Math.abs(el.currentTime-wanted)>.12))el.currentTime=wanted;
      if(!active||!playing)el.pause();
      else if(el.paused)el.play().catch(e=>{window.audioError=String(e);stop();});
    }
    window.audioStatus=audioTracks.map(({el,track})=>({role:track.role,time:el.currentTime,paused:el.paused,volume:el.volume}));
  }
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  function state(layer, f) {
    const type = layer.type || 'image', slot = layer.slot || 'center';
    let x, y;
    if (type === 'text' && textSlots[slot]) [x, y] = textSlots[slot];
    else { const b=layer.box || slots[slot]; x=b[0]+b[2]/2; y=b[1]+b[3]/2; }
    let base = {x:x*spec.width, y:y*spec.height, scale:layer.scale ?? 1,
      rotate:layer.rotate ?? 0, opacity:layer.opacity ?? 1};
    let last = {...base};
    const points=(layer.keys || []).map(k => {
      const p={...last};
      if(k.slot) {const b=slots[k.slot];p.x=(b[0]+b[2]/2)*spec.width;p.y=(b[1]+b[3]/2)*spec.height;}
      for(const name of ['x','y','scale','rotate','opacity']) if(name in k)p[name]=k[name];
      last=p;return [k.frame,p];
    });
    if(points.length) {
      if(f<=points[0][0])base={...points[0][1]};
      else if(f>=points.at(-1)[0])base={...points.at(-1)[1]};
      else for(let i=1;i<points.length;i++) {
        const [a,p]=points[i-1], [b,q]=points[i];
        if(a<=f&&f<=b) {let u=(f-a)/(b-a);if((layer.keys[i].ease||'smooth')!=='linear')u=u*u*(3-2*u);
          for(const k of Object.keys(p))base[k]=p[k]+(q[k]-p[k])*u;break;}
      }
    }
    base.opacity *= f>=(layer.start??0)&&f<(layer.end??count)?1:0;
    const box=layer.box || slots[slot] || [0,0,0,0],w=box[2]*spec.width,h=box[3]*spec.height;
    const [iw,ih]=layer.image_size || [w||1,h||1],fit=Math.min(w/iw,h/ih),pv=layer.pivot || [.5,.5];
    base.pivot_x=(pv[0]-.5)*iw*fit;base.pivot_y=(pv[1]-.5)*ih*fit;
    base.asset=layer.asset;
    for(const k of layer.asset_keys || [])if(f>=k.frame)base.asset=k.asset;
    return base;
  }
  function render(f,manual=false) {
    frame=clamp(Math.round(f),0,count-1);
    const states={};
    for(const layer of spec.layers) {
      const s=state(layer,frame), node=document.getElementById(layer.id);states[layer.id]=s;
      const purpose=node.dataset.purpose;
      const hide=(reviewView!=='full' && purpose==='narration') || (reviewView==='mechanism-only' && ['decoration','camera'].includes(purpose));
      node.setAttribute('opacity',String(hide?0:s.opacity));
      if((layer.type||'image')==='image')for(const image of node.querySelectorAll('[data-variant]'))image.setAttribute('opacity',image.dataset.variant===s.asset?'1':'0');
      if(layer.type!=='path')node.setAttribute('transform',`translate(${s.x} ${s.y}) scale(${s.scale}) rotate(${s.rotate} ${s.pivot_x} ${s.pivot_y})`);
    }
    const shot=spec.shots.find(s=>s.start<=frame&&frame<s.end);
    document.getElementById('_caption').textContent=reviewView==='full'?shot.caption:'';
    seek.value=frame;clock.textContent=`${(frame/spec.fps).toFixed(2)} / ${spec.duration.toFixed(2)} s`;
    const initial=spec.performance_initial || {},performance={frame,states:{...initial.states},contents:{...initial.contents},copies:{},receipts:{},active:[],stopped:false};
    for(const e of spec.compiled_actions || []){
      if(e.start<=frame&&frame<e.end)performance.active.push(e.id);
      if(e.kind==='verify'&&e.contact<=frame&&frame<e.commit)performance.states[e.target]='checking';
      if(frame>=e.commit){if(e.received){performance.receipts[e.target]??=[];performance.receipts[e.target].push(e.received);}if(e.new_state)performance.states[e.target]=e.new_state;
        if(e.kind==='store')performance.contents[e.target]=e.object;
        if(e.kind==='retrieve')performance.copies[e.object]=e.derived_from;}
    }
    const ev=spec.compiled_actions || [];performance.stopped=Boolean(ev.length&&frame>=ev.at(-1).end);
    window.semanticState={frame,shot:shot.id,action:shot.action,change:shot.change,layers:states,performance};
    syncAudio(manual);return window.semanticState;
  }
  function stop(){playing=false;for(const {el} of audioTracks)el.pause();button.textContent='播放';syncAudio(true);}
  function tick(now){if(!playing)return;render(Math.min((now-origin)*spec.fps/1000,eventEnd??(count-1)));if(frame===count-1||(eventEnd!==null&&frame>=eventEnd)){eventEnd=null;stop();}else requestAnimationFrame(tick);}
  seek.max=count-1;seek.addEventListener('input',()=>{stop();render(Number(seek.value),true);});
  button.addEventListener('click',()=>{if(playing)stop();else{eventEnd=null;if(frame===count-1)frame=0;origin=performance.now()-frame/spec.fps*1000;playing=true;button.textContent='暂停';requestAnimationFrame(tick);}});
  window.renderFrame=(f)=>render(f,true);window.videoMeta=spec;
  window.setReviewView=(view)=>{if(!['full','labels-only','mechanism-only'].includes(view))throw new Error('E_REVIEW_VIEW');reviewView=view;return render(frame,true);};
  window.playEvent=(id)=>{const e=(spec.mechanism_trace||[]).find(x=>x.id===id);if(!e)throw new Error('E_EVENT_ID');stop();eventEnd=e.end-1;render(e.start,true);origin=performance.now()-frame/spec.fps*1000;playing=true;button.textContent='暂停';requestAnimationFrame(tick);};
  for(const b of document.querySelectorAll('[data-review-view]'))b.addEventListener('click',()=>window.setReviewView(b.dataset.reviewView));
  for(const b of document.querySelectorAll('[data-event]'))b.addEventListener('click',()=>window.playEvent(b.dataset.event));
  const images=[...stage.querySelectorAll('image')].map(node=>new Promise((resolve,reject)=>{
    const image=new Image();image.onload=resolve;image.onerror=()=>reject(new Error('ASSET_BLOCKED: image failed to decode'));image.src=node.getAttribute('href');
  }));
  const audioReady=audioTracks.map(({el})=>new Promise((resolve,reject)=>{
    if(el.readyState>=1)return resolve();el.addEventListener('loadedmetadata',resolve,{once:true});
    el.addEventListener('error',()=>reject(new Error('AUDIO_BLOCKED: unsupported/invalid embedded audio')),{once:true});el.load();
  }));
  Promise.all([document.fonts.ready,...images,...audioReady]).then(()=>{render(0);window.ready=true;}).catch(e=>{window.renderError=String(e);});
}
