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
    data=json.loads(p.read_text(encoding='utf-8'));m.require(isinstance(data,dict),'E_SCHEMA','story.json must be an object')
    return data,root

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('init');s.add_argument('--topic',required=True);s.add_argument('--formats',nargs='+',required=True);s.add_argument('--out',type=Path,required=True);s.add_argument('--profile',choices=['general','academic'],default='general')
    q=sub.add_parser('cue-import');q.add_argument('--srt',type=Path,required=True);q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('operations')
    for name in ('plan','asset-plan','prompts','check','review','export','timeline','diagnose','handoff-init','handoff'):
        s=sub.add_parser(name);s.add_argument('project',type=Path)
        if name in ('plan','asset-plan','prompts','timeline','diagnose'):s.add_argument('--out',type=Path)
        if name in ('handoff-init','handoff'):
            s.add_argument('--delivery',type=Path,required=True);s.add_argument('--out',type=Path,required=True)
            if name=='handoff':s.add_argument('--teacher-review',type=Path,required=True)
        if name=='diagnose':s.add_argument('--review',type=Path)
        if name=='review':s.add_argument('--folder',default='review-v1')
        if name=='export':
            s.add_argument('--out',type=Path,required=True);s.add_argument('--formats',nargs='+');s.add_argument('--review',type=Path,required=True)
            s.add_argument('--svg-frame',type=int)
    args=p.parse_args(argv)
    try:
        if args.command=='operations':
            from perform_core import ACTIONS,DEFAULTS
            print(json.dumps({k:{'minimum_seconds':ACTIONS[k],'default_seconds':DEFAULTS[k]} for k in ACTIONS},indent=2));return 0
        if args.command=='cue-import':
            from soundtrack import parse_srt
            m.require(not args.out.exists(),'E_EXISTS','use a new cue file')
            cues=parse_srt(args.srt.read_text(encoding='utf-8-sig'))
            args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(cues,ensure_ascii=False,indent=2)+'\n')
            print('IMPORTED supplied timestamps only; not transcription/alignment: '+str(args.out));return 0
        if args.command=='init':
            data=m.blank(args.topic,args.formats)
            data['profile']=args.profile
            data['presentation']='animated' if any(f in data['formats'] for f in ('html','video')) else 'static'
            data['mechanism']={'version':1,'kind':'discrete','variables':{},'events':[],'invariants':[]} if data['presentation']=='animated' else {'version':1,'kind':'static','relations':[]}
            if args.profile=='academic':
                from academic_delivery import blank_course
                data['course']=blank_course()
            if any(f in data['formats'] for f in ('html','video')):data['performance']={'version':1,'rigs':[],'actions':[],'cues':[]}
            m.require(not args.out.exists(),'E_EXISTS','use a new project directory')
            args.out.mkdir(parents=True);(args.out/'assets').mkdir()
            (args.out/'story.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(f'DRAFT: {args.out}/story.json. Plan typed events and effects BEFORE designing split assets. Fill course evidence for academic work. No assets were generated.');return 0
        data,root=read(args.project)
        if args.command in ('plan','asset-plan'):
            import mechanism_core as mc
            import action_requirements as ar
            import academic_delivery as ad
            ad.validate_course(data)
            report=mc.plan(data) if args.command=='plan' else ar.derive(data)
            text=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
            if args.out:
                m.require(not args.out.exists(),'E_EXISTS','use a new plan file');args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text,encoding='utf-8')
            else:print(text,end='')
            return 0
        if args.command in ('handoff-init','handoff'):
            import academic_delivery as ad
            if args.command=='handoff-init':print('PENDING instructor review: '+str(ad.prepare_handoff(data,root,args.delivery,args.out)))
            else:print(json.dumps(ad.handoff(data,root,args.delivery,args.teacher_review,args.out),ensure_ascii=False,indent=2))
            return 0
        if args.command in ('timeline','diagnose'):
            if args.command=='timeline':
                scene=m.resolved(data);report={'status':'compiled-not-reviewed','shots':scene['shots'],'actions':scene.get('compiled_actions',[]),'events':scene.get('mechanism_trace',[]),'skipped':scene.get('mechanism_skipped',[])}
            else:
                from repair_plan import diagnose
                report=diagnose(data,root,args.review)
            text=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
            if args.out:
                m.require(not args.out.exists(),'E_EXISTS','use a new diagnostic file');args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text)
            else:print(text,end='')
            return 2 if report.get('status')=='blocked' else 0
        if args.command=='prompts':
            text=m.prompts(data)
            if args.out:
                m.require(not args.out.exists(),'E_EXISTS','refuse overwriting briefs')
                args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text,encoding='utf-8')
            else:print(text,end='')
        elif args.command=='check':
            import mechanism_core as mc
            mc.production_gate(data);m.validate(data,root);print('PASS: asset and event checks; actual visual/subject review is still required.')
        elif args.command=='review':print('PENDING: inspect images AND transitions, then fill '+str(out.prepare_review(data,root,root/args.folder)))
        elif args.command=='export':
            report=out.export(data,root,args.out,args.formats,args.review,args.svg_frame)
            print('EXPORTED reviewed artifact (customer handoff is a separate approval): '+', '.join(report['files'])+'\n'+str(args.out))
        return 0
    except (m.Problem, OSError, ValueError, RuntimeError) as exc:
        print(str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
