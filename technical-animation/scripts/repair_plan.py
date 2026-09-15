"""Convert production failures into scoped repair instructions; never approve or bypass quality."""
from __future__ import annotations
import json
from pathlib import Path
import topic_model as m

RULES={
 'E_MECHANISM_REQUIRED':('mechanism','Write typed events, requirements, effects and visible bindings. Do not substitute zoom for an operation.'),
 'E_MECHANISM_DIVERGENCE':('mechanism','Compare the specific event effect with the actual operation backend. Fix the effect or choose a supported operation; do not relabel the outcome.'),
 'E_EVENT_DEPENDENCY':('mechanism','Reference a previous enabled event milestone. Inspect false branches rather than guessing a timestamp.'),
 'E_VISUAL_OCCLUDED':('layout','The effect exists in state but contributes no visible pixels. Repair only its masking/layer order and rerun the event views.'),
 'E_EVENT_REVIEW':('review','Inspect pre/contact/commit/post and reduced-text/mechanism-only views for the named event. Record real findings; do not auto-approve.'),
 'E_CLAIM_REVIEW':('subject-review','Read the cited source at the stated locator and obtain subject review before handoff.'),
 'E_STAGE_BOUNDS':('layout','Reposition the identified rig or correct its verified hinge/angle. Check swept bounds and neighbouring shots, not just the closed pose; never shrink text to compensate.'),
 'E_PORT':('asset-rig','Locate the contact/entry/inside point on the actual generated art. Record normalized coordinates; do not invent an off-image entry.'),
 'E_RIG_PART':('asset-rig','Generate only the missing gate/front-mask/probe on the SAME registered canvas and viewpoint; keep approved body artwork.'),
 'E_REGISTRATION':('asset-rig','Normalize registered layers together with asset_pack.py. Differing viewpoints need regeneration, not a guessed crop.'),
 'E_STATE_ART':('asset-rig','Generate the missing state for the same entity. Preserve silhouette/viewpoint, keep exact labels editable; do not reuse unrelated art.'),
 'E_CAUSAL_STATE':('semantics','Correct stored identity, initial occupancy or copy derivation; preserve originals. Repair dependencies rather than declaring success.'),
 'E_DEPENDENCY':('timeline','Reference an earlier operation; remove cycles. Results must follow the operation that creates them.'),
 'E_CUE_CONFLICT':('timeline','Move the conflicting cue or re-record its line; leave completed operations unchanged. Never speed up the entire video.'),
 'E_PACING':('timeline','Increase the affected cue/project span or reduce explanation content. Keep contact, response and final reading hold.'),
 'E_TRACK_CONFLICT':('timeline','Remove hand-authored tracks only from the named rig after preserving the source. Let the operation compiler own that motion.'),
 'E_AUDIO_RANGE':('audio','Correct explicit trim/start using real audio metadata, or revise the line. Do not silently truncate required narration.'),
 'E_AUDIO_HASH':('audio','Confirm the changed local audio file; update its actual hash, then recapture and review sound/timing.'),
 'E_AUDIO_GAIN':('audio','Reduce music/narration gains so their sum is at most 1. Listen again; do not assert mix quality from a peak number.'),
 'ASSET_BLOCKED':('generation','Invoke the actual authorized image tool for this topic and record returned files. Retain prompts; never substitute boxes.'),
 'E_ART':('art-direction','Inspect the named frame. Enlarge relevant subjects, remove paragraph panels, and show an operation/state change. Do not pad image bounds.'),
 'E_TEXT_FIT':('layout','Shorten only the identified label; keep the subject scale and identity, then re-check the affected shot.'),
 'E_REVIEW_STALE':('review','Recapture changed shots and transitions with current assets/runtime/audio. Prior approval cannot authorize changed pixels.'),
 'E_REUSE':('generation','Generate a genuinely new topic asset, or obtain explicit scoped reuse consent; renaming files is not freshness.'),
}


def diagnose(data,root,review=None):
    issues=[]
    try:
        import mechanism_core as mc
        mc.production_gate(data);m.validate(data,root)
    except m.Problem as exc:
        stage,fix=RULES.get(exc.code,('source','Correct the exact source field identified by the error, then rerun create.py check.'))
        issues.append(dict(code=exc.code,message=str(exc),stage=stage,repair=fix,invalidates_review=True))
    if review is not None:
        path=Path(review).resolve();m.require(path.is_relative_to(Path(root).resolve()) and path.is_file(),'E_REVIEW','review must be inside project')
        report=json.loads(path.read_text())
        for shot in report.get('shots',[]):
            if shot.get('verdict')=='rejected':
                issues.append(dict(code='VISUAL_REJECT',stage='art-direction',shot=shot.get('id'),message=shot.get('findings',{}),
                    repair='Repair only the rejected asset/action plus touching transitions, recapture, then obtain a real visual review.',invalidates_review=True))
    return {'status':'blocked' if issues else 'awaiting-visual-review','issues':issues,
            'auto_approved':False,'source_modified':False,'next':'Repair the scoped cause, then check and create a NEW review folder. Two unresolved repair rounds need human/vision diagnosis, not weaker thresholds.'}
