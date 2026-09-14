#!/usr/bin/env python3
"""Validate the temporal/asset contract, independent of the rendering engine."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from typing import Any

def validate_project(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if isinstance(data,dict) and 'recipe' in data:
        from recipe_core import validate_compiled
        errors.extend(e['code']+': '+e['message'] for e in validate_compiled(data))
    if data.get('ready_for_render') is False:errors.append('draft project: ready_for_render must be explicitly enabled after scene authoring')
    for key in ('title','width','height','fps','duration','takeaway','entry','events','assets','sources'):
        if key not in data: errors.append(f'missing {key}')
    if errors: return errors
    for key in ('title','takeaway'):
        if not isinstance(data[key],str) or not data[key].strip():errors.append(f'{key} must be nonempty')
    for key in ('width','height','fps','duration'):
        value=data[key]
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or value<=0:
            errors.append(f'{key} must be a positive finite number')
    if errors:return errors
    if any(int(data[k])!=data[k] for k in ('width','height','fps')):
        errors.append('dimensions and fps must be integer values')
    if data['width']%2 or data['height']%2:errors.append('dimensions must be even for yuv420p')
    frames=data['fps']*data['duration']
    if abs(frames-round(frames))>1e-6:errors.append('duration * fps must be an integer frame count')
    entry=Path(data['entry'])
    if entry.is_absolute() or '..' in entry.parts or entry.suffix!='.html':errors.append('entry must be a local relative .html path')
    events=data['events']
    if not isinstance(events,list) or not all(isinstance(e,dict) for e in events):
        return errors+['events must be an array of objects']
    by_id={}
    for e in events:
        eid=e.get('id','<missing>')
        if eid in by_id: errors.append(f'duplicate event id: {eid}')
        by_id[eid]=e
        if not all(k in e for k in ('id','kind','start','end','actor','label')):
            errors.append(f'{eid}: missing required event fields');continue
        a,b=e['start'],e['end']
        if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in (a,b)):
            errors.append(f'{eid}: invalid time');continue
        if not 0<=a<b<=data['duration']:errors.append(f'{eid}: outside duration / nonpositive span')
    for e in events:
        cause=e.get('caused_by')
        if cause and cause not in by_id:errors.append(f'{e.get("id")}: unknown cause {cause}')
        elif cause:
            previous=by_id[cause]
            if isinstance(previous.get('end'),(int,float)) and e.get('start',-1)<previous['end']-1e-6:
                errors.append(f'{e.get("id")}: causality violation: starts before {cause} arrives/finishes')
    if data.get('requires_feedback',True):
        if not any(e.get('kind')=='result' for e in events):errors.append('feedback result event required')
        if not any(e.get('kind')=='decision' and e.get('caused_by') in by_id and by_id[e['caused_by']].get('kind')=='result' for e in events):
            errors.append('feedback must cause a subsequent decision')
    for a in data['assets']:
        if a.get('used') and a.get('status') in ('rejected','missing','unlicensed'):
            errors.append(f'rejected/missing/unlicensed asset used: {a.get("path")}')
        if a.get('used') and not a.get('origin'):errors.append(f'asset origin missing: {a.get("path")}')
    return errors

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);args=p.parse_args()
    path=args.project/'project.json' if args.project.is_dir() else args.project
    try:
        data=json.loads(path.read_text(encoding='utf-8')); errors=validate_project(data)
    except (OSError,ValueError,TypeError) as exc:raise SystemExit(f'Cannot validate: {exc}')
    if errors:raise SystemExit('\n'.join('ERROR '+x for x in errors))
    print(f'PASS: {data["title"]}; {round(data["fps"]*data["duration"])} frames; event causality and asset metadata valid')
if __name__=='__main__':main()
