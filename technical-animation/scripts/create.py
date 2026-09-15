#!/usr/bin/env python3
"""Topic-first authoring: select HTML/video/SVG without selecting a fixed asset kit."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import topic_model as m
import topic_output as out

def read(project):
    root=Path(project).resolve()
    p=root/'story.json'
    if not p.is_file():m.fail('E_SOURCE',f'Missing {p}; run init first')
    return json.loads(p.read_text(encoding='utf-8')),root

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('init');s.add_argument('--topic',required=True);s.add_argument('--formats',nargs='+',required=True);s.add_argument('--out',type=Path,required=True)
    for name in ('prompts','check','review','export'):
        s=sub.add_parser(name);s.add_argument('project',type=Path)
        if name=='prompts':s.add_argument('--out',type=Path)
        if name=='review':s.add_argument('--folder',default='review-v1')
        if name=='export':
            s.add_argument('--out',type=Path,required=True);s.add_argument('--formats',nargs='+');s.add_argument('--review',type=Path,required=True)
            s.add_argument('--svg-frame',type=int)
    args=p.parse_args(argv)
    try:
        if args.command=='init':
            data=m.blank(args.topic,args.formats)
            m.require(not args.out.exists(),'E_EXISTS','use a new project directory')
            args.out.mkdir(parents=True);(args.out/'assets').mkdir()
            (args.out/'story.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(f'DRAFT: {args.out}/story.json. Choose three visual concepts, fill entity mappings, generate real assets. No assets were generated.');return 0
        data,root=read(args.project)
        if args.command=='prompts':
            text=m.prompts(data)
            if args.out:
                m.require(not args.out.exists(),'E_EXISTS','refuse overwriting briefs')
                args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text,encoding='utf-8')
            else:print(text,end='')
        elif args.command=='check':m.validate(data,root);print('PASS: structural checks only; not visual approval or generation-provider authentication.')
        elif args.command=='review':print('PENDING: inspect images AND transitions, then fill '+str(out.prepare_review(data,root,root/args.folder)))
        elif args.command=='export':
            report=out.export(data,root,args.out,args.formats,args.review,args.svg_frame)
            print('EXPORTED: '+', '.join(report['files'])+'\n'+str(args.out))
        return 0
    except (m.Problem, OSError, ValueError, RuntimeError) as exc:
        print(str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
