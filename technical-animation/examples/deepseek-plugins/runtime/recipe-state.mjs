/** Pure reducer shared by renderer/debug state. End-exclusive events; no mutable simulation. MIT. */
export function stateAtFrame(project,frame){
 const f=Math.max(0,Math.min(Math.round(project.duration*project.fps)-1,Math.trunc(frame)));
 const state={frame:f,stopped:false,feedback_received:false,code_changed:false,test_runs:0,db_reads:0,responses:0,cache_filled:false,context_ready:false,selected_ids:[]};
 for(const e of project.events){
  if(f>=e.end_frame)Object.assign(state,e.effect||{});
  if(e.start_frame<=f&&f<e.end_frame){Object.assign(state,{active_event:e.id,active_kind:e.kind,caption:e.caption});if(e.kind==='stop')state.stopped=true;}
 }
 return state;
}
export const eventProgress=(event,frame)=>Math.max(0,Math.min(1,(frame-event.start_frame)/(event.end_frame-event.start_frame)));
export function activeEvent(project,frame){return project.events.find(e=>e.start_frame<=frame&&frame<e.end_frame)||project.events.at(-1);}
