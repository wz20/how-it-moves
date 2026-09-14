/** Six directed shots of a partition-scoped search. Original vector assets; no reference footage. */
import {clamp,lerp,smooth,easeInOut} from './motion.mjs';
import {P,between,mixBox,stagedReflow,shotAt,fitCamera,mixCamera,withCamera,reveal,rounded,text,circle,trace,parcel,magnifier,picture,semanticAt} from './editorial.mjs';

export function drawFrame(ctx,spec,rawFrame) {
 const f=clamp(Math.floor(rawFrame),0,Math.round(spec.duration*spec.fps)-1),d=spec.direction,cfg=d.config;
 const E=Object.fromEntries(spec.events.map(e=>[e.id,e]));const S=Object.fromEntries(d.shots.map(s=>[s.id,s]));
 const state=semanticAt(spec,f),issues=[];const shot=shotAt(d.shots,f),idx=d.shots.indexOf(shot);
 const selected=cfg.groups.findIndex(g=>g.id===cfg.selected_group),palette=[P.purple,P.blue,P.green];
 const tint=[P.purpleLight,P.blueLight,P.greenLight];
 const tx=(str,x,y,size=32,color=P.ink,opts={})=>text(ctx,str,x,y,size,color,{issues,...opts});
 const oldBoxes=cfg.groups.map((g,i)=>[510+i*420,355,335,310]);
 const fullParent=[450,302,1300,555],resultParent=[445,330,620,485];
 const expand=smooth(between(f,E.expand.start_frame,E.expand.end_frame));
 const collapse=smooth(between(f,S.recap.start_frame,S.recap.start_frame+spec.fps*.85));
 const compact=smooth(between(f,S.rank.start_frame,S.rank.start_frame+spec.fps*.8))*(1-collapse);
 const expanded=expand*(1-collapse);
 const parent=mixBox(mixBox(oldBoxes[selected],fullParent,expanded),resultParent,compact);
 const query=[110,434,265,176];
 const boxFor=(i)=>stagedReflow([525+i*389,416,332,260],[490,420+i*113,530,94],compact);
 const headings=[cfg.title,'先指定目标分区','同一个分区，展开内部','同一请求，并行发给各段','候选齐了，再统一排序','回到全局：少查，不乱查'];
 const captions=['已知范围，为什么还要全库找？','其他分区仍在，但不参与这次查询。','保留父级身份，不把展开画成复制。','请求抵达才检索；结果随后返回。','只对返回的候选排序，不承诺精确召回。',cfg.takeaway];
 ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;ctx.lineCap='round';ctx.lineJoin='round';ctx.fillStyle=P.paper;ctx.fillRect(0,0,1920,1080);
 // Subtle domain board. No unrelated pet, meme, logo or particle wallpaper.
 trace(ctx,[[70,110],[1850,110]],{color:P.line,width:2});
 tx('HOW IT MOVES',72,63,24,P.muted,{mono:true});tx(`${idx+1} / 6  ·  ${shot.id.toUpperCase()}`,1848,63,23,P.muted,{align:'right',mono:true});
 tx(headings[idx],78,181,55,P.ink,{width:1730});
 trace(ctx,[[80,228],[80+Math.min(620,headings[idx].length*39),228]],{color:palette[selected],width:6});
 const zoom=smooth(between(f,E.choose.start_frame+spec.fps*.35,E.choose.end_frame+spec.fps*.45))*(1-expand)*(1-collapse);
 const focus=fitCamera(oldBoxes[selected],[75,275,1770,590],1.28,100);
 const camera=mixCamera({s:1,x:0,y:0},focus,zoom);
 ctx.save();ctx.beginPath();ctx.rect(60,248,1800,650);ctx.clip();
 withCamera(ctx,camera,()=>{
   // Wide -> selection is a visual contrast, not a benchmark or a deletion.
   if(expanded<.99 && f<S.rank.start_frame){
     const y=712;
     const scanning=between(f,spec.fps*.45,E.choose.start_frame);
     trace(ctx,[[350,653],[415,y],[1712,y]],{color:state.selected?P.line:P.muted,width:3,progress:scanning,dash:[8,7]});
     for(let i=0;i<3;i++)trace(ctx,[[oldBoxes[i][0]+165,665],[oldBoxes[i][0]+165,y]],{color:P.line,width:2,dash:[6,7]});
     if(f<E.choose.start_frame)tx('不指定范围：所有分区都要考虑',1040,779,31,P.muted,{align:'center'});
   }
   cfg.groups.forEach((g,i)=>{
     const isSelected=i===selected;
     if(isSelected && expanded>.005)return;
     const opacity=(state.selected&&!isSelected?.22:1)*(1-expanded);
     if(opacity<.01)return;
     ctx.save();ctx.globalAlpha=opacity;
     reveal(ctx,oldBoxes[i],smooth(between(f,spec.fps*(.12+i*.22),spec.fps*(.65+i*.22))),()=>drawGroup(g,i,oldBoxes[i],state.selected===g.id));
     ctx.restore();
   });
   if(state.selected && expanded<.99 && f<S.recap.start_frame){
     const q=[[(375-camera.x)/camera.s,(522-camera.y)/camera.s],[435,522],[435,748],[oldBoxes[selected][0]+166,748],[oldBoxes[selected][0]+166,665]];
     trace(ctx,q,{color:palette[selected],width:4,progress:smooth(between(f,E.choose.start_frame,E.choose.end_frame))});
   }
   if(expanded>.005){
     rounded(ctx,parent,{fill:P.white,stroke:palette[selected],width:3,r:22});
     const lab=cfg.groups[selected].label+' · 指定分区';
     rounded(ctx,[parent[0]+24,parent[1]-22,310,44],{fill:palette[selected],stroke:null,r:10});tx(lab,parent[0]+179,parent[1],25,P.white,{align:'center',width:295});
     if(expanded<.96){ctx.save();ctx.globalAlpha=1-expanded;picture(ctx,parent[0]+parent[2]/2-55,parent[1]+70,110,75,palette[selected]);ctx.restore()}
     if(expanded>.65){
       ctx.save();ctx.globalAlpha=between(expanded,.65,1);
       tx(compact>.8?'同一分区的候选，保留来源':'分区内部：三个已加载的段',parent[0]+38,parent[1]+50,26,P.muted,{width:parent[2]-70});
       cfg.segments.forEach((seg,i)=>{
         const b=boxFor(i);const r=smooth(between(f,E.expand.end_frame+spec.fps*(i*.14),E.expand.end_frame+spec.fps*(.4+i*.14)));
         reveal(ctx,b,r,()=>drawSegment(seg,i,b));
       });
       ctx.restore();
     }
   }
   // Fan-out uses one logical query with separate invocation identities, all within selected parent.
   if(f>=S.parallel.start_frame && f<S.rank.start_frame){
     cfg.segments.forEach((seg,i)=>{
       const b=boxFor(i),path=[[375,505],[412,505],[412,388],[b[0]+b[2]/2,388],[b[0]+b[2]/2,b[1]]];
       trace(ctx,path,{color:P.line,width:2,progress:smooth(between(f,S.parallel.start_frame,E['call_'+seg.id].start_frame))});
       parcel(ctx,path,f,E['call_'+seg.id],{label:'Q1',color:P.blue});
       const rp=[[b[0]+b[2]/2,b[1]+b[3]],[b[0]+b[2]/2,744],[1620,744],[1620,793]];
       trace(ctx,rp,{color:P.line,width:2,progress:smooth(between(f,E['work_'+seg.id].end_frame,E['return_'+seg.id].start_frame))});
       parcel(ctx,rp,f,E['return_'+seg.id],{label:'2',color:P.green,fill:P.greenLight});
     });
     rounded(ctx,[1265,785,450,53],{fill:P.greenLight,stroke:P.green,r:12,width:2});
     tx(`候选到达 ${state.returned.length} / 3 · 等全部返回`,1490,812,26,P.green,{align:'center'});
   }
   if(compact>.90){ctx.save();ctx.globalAlpha=smooth(between(compact,.90,1));drawRank();ctx.restore()}
   if(collapse>.1){
     ctx.save();ctx.globalAlpha=collapse;
     rounded(ctx,[515,765,1218,103],{fill:P.greenLight,stroke:P.green,r:16,width:2});
     tx(`返回 Top ${cfg.top_k}`,546,797,25,P.green);
     tx(d.ranked.slice(0,cfg.top_k).map(r=>`${r.id}  ${r.score.toFixed(2)}`).join('     '),1130,823,30,P.ink,{align:'center',mono:true,width:1090});ctx.restore();
   }
 });ctx.restore();
   // The query retains Q1 through overview, fan-out, return and recap.
   rounded(ctx,query,{fill:P.white,stroke:P.blue,r:20});
   rounded(ctx,[query[0]+18,query[1]-23,66,44],{fill:P.blue,stroke:null,r:10});tx('Q1',query[0]+51,query[1]-1,25,P.white,{mono:true,align:'center'});
   magnifier(ctx,query[0]+49,query[1]+58,20);
   tx(cfg.query,query[0]+132,query[1]+111,29,P.ink,{align:'center',width:245});
   tx(state.stopped?'结果已返回':'一个查询',query[0]+149,query[1]+55,26,state.stopped?P.green:P.muted,{align:'center'});

 // Persistent breadcrumb and mini-map preserve orientation during detail views.
 rounded(ctx,[78,914,1764,91],{fill:P.ink,stroke:null,r:16});tx(captions[idx],960,958,36,P.white,{align:'center',width:1690});
 tx('示意数据 · 显式指定分区 · 分数非概率 · 不代表生产延迟或完整 Milvus 架构',79,1045,21,P.muted,{weight:500});
 for(let i=0;i<6;i++)rounded(ctx,[1494+i*55,1040,41,7],{fill:i<=idx?P.blue:P.line,stroke:null,r:3});
 state.focusedIds=idx===0?cfg.groups.map(g=>g.id):idx===1?[cfg.selected_group]:idx<4?cfg.segments.map(s=>s.id):idx===4?['reducer']:[cfg.selected_group,'Q1'];
 state.camera=camera;state.layoutIssues=issues;state.packetCount=spec.events.filter(e=>['call','result'].includes(e.kind)&&f>=e.start_frame&&f<e.end_frame).length;
 return state;

 function drawGroup(g,i,b,active){
   rounded(ctx,b,{fill:P.white,stroke:active?palette[i]:P.ink,r:20,width:active?4:2.5});
   rounded(ctx,[b[0]+22,b[1]-21,b[2]-44,42],{fill:palette[i],stroke:null,r:10});tx(g.label,b[0]+b[2]/2,b[1],31,P.white,{align:'center',width:b[2]-60});
   picture(ctx,b[0]+b[2]/2-52,b[1]+46,104,76,palette[i]);
   for(let j=0;j<3;j++){
     rounded(ctx,[b[0]+28,b[1]+145+j*48,b[2]-56,36],{fill:tint[i],stroke:palette[i],width:1.5,r:8});
     for(let k=0;k<4;k++)circle(ctx,b[0]+47+k*22,b[1]+163+j*48,5,palette[i],null);
     trace(ctx,[[b[0]+170,b[1]+163+j*48],[b[0]+b[2]-42,b[1]+163+j*48]],{color:palette[i],width:2});
   }
   if(active){circle(ctx,b[0]+b[2]-18,b[1]+b[3]-13,22,P.green,P.white,3);tx('✓',b[0]+b[2]-18,b[1]+b[3]-14,28,P.white,{align:'center'})}
 }
 function drawSegment(seg,i,b){
   const done=state.returned.includes(seg.id),running=f>=E['work_'+seg.id].start_frame&&f<E['work_'+seg.id].end_frame;
   rounded(ctx,b,{fill:done?P.greenLight:P.blueLight,stroke:done?P.green:P.blue,width:2.5,r:15});
   if(compact>.12 && compact<.88){
     tx(seg.label,b[0]+b[2]/2,b[1]+b[3]/2,24,P.ink,{align:'center',width:b[2]-15});
   }else if(compact<=.12){
     tx(seg.label,b[0]+22,b[1]+35,32,P.ink,{width:b[2]-45});
     ctx.save();ctx.globalAlpha*=1-smooth(compact/.12);
     const nodes=[[.19,.34],[.40,.28],[.65,.4],[.8,.28],[.3,.50],[.56,.56]];
     const pts=nodes.map(p=>[b[0]+p[0]*b[2],b[1]+p[1]*b[3]]);
     [[0,1],[1,2],[2,3],[0,4],[4,5],[1,5],[2,5]].forEach(([a,z])=>trace(ctx,[pts[a],pts[z]],{color:P.blue,width:2}));
     pts.forEach((p,k)=>circle(ctx,...p,5,k===2&&running?P.amber:P.white,P.blue,2));
     if(running){const u=between(f,E['work_'+seg.id].start_frame,E['work_'+seg.id].end_frame);magnifier(ctx,b[0]+lerp(50,b[2]-70,u),b[1]+b[3]*.46,17,P.amber)}
     for(let j=0;j<2;j++){const y=b[1]+b[3]-69+j*35;
       if(f>=E['work_'+seg.id].end_frame){tx(seg.candidates[j].id,b[0]+20,y,24,P.ink,{mono:true,width:177});tx(seg.candidates[j].score.toFixed(2),b[0]+b[2]-22,y,24,P.blue,{mono:true,align:'right'})}
       else{rounded(ctx,[b[0]+19,y-8,b[2]-40,16],{fill:P.white,stroke:null,r:6})}
     }
     ctx.restore();
   }else{
     tx(seg.label,b[0]+20,b[1]+27,29,P.ink,{width:150});
     ctx.save();ctx.globalAlpha*=smooth(between(compact,.88,1));
     tx(seg.candidates.map(r=>r.id).join('  '),b[0]+b[2]-20,b[1]+62,24,P.muted,{align:'right',mono:true,width:b[2]-35});
     if(done)tx('已返回',b[0]+b[2]-20,b[1]+27,24,P.green,{align:'right'});
     ctx.restore();
   }
 }
 function drawRank(){
   const panel=[1175,321,577,527];rounded(ctx,panel,{fill:P.white,stroke:P.green,width:3,r:20});
   tx(`候选汇总  →  Top ${cfg.top_k}`,panel[0]+30,panel[1]+42,31,P.ink,{width:520});
   const original=cfg.segments.flatMap(s=>s.candidates.map(r=>({...r,segment:s.id})));
   const sorting=smooth(between(f,E.rank.start_frame,E.rank.end_frame));
   original.forEach((row,i)=>{
     const dest=d.ranked.findIndex(r=>r.id===row.id),y=lerp(405+i*62,405+dest*62,sorting),keep=dest<cfg.top_k;
     ctx.save();if(sorting>.98&&!keep)ctx.globalAlpha*=.30;
     rounded(ctx,[panel[0]+22,y,532,48],{fill:keep&&sorting>.9?P.greenLight:P.paper,stroke:keep&&sorting>.9?P.green:P.line,width:2,r:9});
     tx(row.id,panel[0]+41,y+25,26,P.ink,{mono:true,width:215});
     rounded(ctx,[panel[0]+276,y+19,Math.max(7,154*row.score),12],{fill:keep&&sorting>.9?P.green:P.blue,stroke:null,r:4});
     tx(row.score.toFixed(2),panel[0]+531,y+25,26,P.ink,{mono:true,align:'right'});ctx.restore();
   });
   const path=[[1175,795],[1130,795],[1130,855],[405,855],[405,600],[375,600]];
   if(f>=E.deliver.start_frame){trace(ctx,path,{color:P.line,width:3});parcel(ctx,path,f,E.deliver,{label:'TopK',color:P.green,fill:P.greenLight})}
 }
}

export function start(spec) {
 const canvas=document.getElementById('stage'),ctx=canvas.getContext('2d'),seek=document.getElementById('seek'),toggle=document.getElementById('toggle'),clock=document.getElementById('clock');
 const count=Math.round(spec.duration*spec.fps);let playing=false,frame=0,origin=0;
 canvas.width=spec.width;canvas.height=spec.height;seek.max=count-1;
 const draw=(f)=>{frame=clamp(Math.round(f),0,count-1);window.semanticState=drawFrame(ctx,spec,frame);window.layoutIssues=window.semanticState.layoutIssues;seek.value=frame;clock.textContent=`${(frame/spec.fps).toFixed(2)} / ${spec.duration.toFixed(2)} s`;return window.semanticState};
 window.renderFrame=draw;window.videoMeta=spec;
 function stop(){playing=false;toggle.textContent='播放'}
 toggle.addEventListener('click',()=>{if(playing)stop();else{if(frame>=count-1)frame=0;origin=performance.now()-frame/spec.fps*1000;playing=true;toggle.textContent='暂停';requestAnimationFrame(tick)}});
 function tick(now){if(!playing)return;draw(Math.floor((now-origin)/1000*spec.fps));if(frame>=count-1)stop();else requestAnimationFrame(tick)}
 seek.addEventListener('input',()=>{stop();draw(Number(seek.value))});
 document.fonts.ready.then(()=>{draw(0);window.ready=true});
}
