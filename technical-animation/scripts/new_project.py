#!/usr/bin/env python3
"""Create a new isolated drafting workspace. Never overwrites an existing path."""
from __future__ import annotations
import argparse,json,shutil
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--topic',required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--duration',type=float,default=10);a=p.parse_args()
    if a.duration<=0 or abs(a.duration*60-round(a.duration*60))>1e-6:p.error('duration must be positive with an integer frame count at 60fps')
    out=a.out.resolve()
    if out.exists():raise SystemExit(f'Refusing to overwrite {out}. Choose a new project directory.')
    root=Path(__file__).resolve().parents[1];out.mkdir(parents=True)
    shutil.copytree(root/'runtime',out/'runtime')
    shutil.copy2(root/'templates'/'index.html',out/'index.html')
    shutil.copy2(root/'templates'/'scene.mjs',out/'scene.mjs')
    data={'title':a.topic,'takeaway':'','width':1920,'height':1080,'fps':60,'duration':a.duration,'entry':'index.html','audio':'none','requires_feedback':False,'ready_for_render':False,'events':[],'assets':[],'sources':[]}
    (out/'project.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'brief.md').write_text(f'# {a.topic}\n\nStatus: drafting.\n\nDefine the one takeaway, audience, technical source, and deliberately omitted details before authoring.\n',encoding='utf-8')
    (out/'semantic-map.json').write_text(json.dumps({'status':'draft','entities':[],'relationships':[],'simplifications':[]},indent=2),encoding='utf-8')
    (out/'storyboard.md').write_text('# Storyboard\n\nFor each beat: timestamp, technical state, actor, payload, arrival response, viewer takeaway.\n',encoding='utf-8')
    print(f'Created DRAFT {out}\nHost agent must complete content, design and scene before setting ready_for_render=true. This command does not generate a finished video.')
if __name__=='__main__':main()
