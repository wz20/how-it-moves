#!/usr/bin/env python3
"""Content-only illustrated studio: retain physical comic assets and causal events."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path
from recipe_core import compile_recipe, normalized, validate_spec, visual_units
from recipe import HTML, load
from bundle import bundle_html
ROOT=Path(__file__).resolve().parents[1]
DURATIONS={'feedback-retry':20,'retrieval-evidence':20,'cache-aside':22}
ASSETS={
 'feedback-retry':['original-jointed-robot','original-physical-terminal','task-clipboard','context-notebook'],
 'retrieval-evidence':['archive-cabinet','indexed-evidence-pages','context-ring-binder','generation-press'],
 'cache-aside':['application-kiosk','sliding-cache-drawer','database-vault','key-value-letter'],
}
TITLES={'feedback-retry':'Agent 的关键，是反馈闭环','retrieval-evidence':'RAG：先找证据，再回答','cache-aside':'缓存：这次不用再查库了'}
RUNTIME=['motion.mjs','drawing.mjs','rigs.mjs','recipe-state.mjs','studio-art.mjs','illustrated-player.mjs']
def example(name):
 s=json.loads((ROOT/'recipes'/f'{name}.json').read_text(encoding='utf-8'))
 s['duration']=DURATIONS[name];s['title']=TITLES[name]
 return s
def compile_illustrated(spec):
 errors=validate_spec(spec)
 if not errors and spec.get('duration',12)<18:
  errors.append({'code':'E_READING_TIME','field':'duration','message':'实体道具和特写需要至少18秒','hint':'使用20秒；不要用小字或删除反馈来硬塞10秒。'})
 if not errors:
  c=spec['content'];r=spec['recipe'];budgets=[]
  if r=='retrieval-evidence':
   budgets=[('content.answer',c['answer'],13),('content.question',c['question'],14)]
   budgets += [(f'content.documents[{i}].text',d['text'],10) for i,d in enumerate(c['documents'])]
   budgets += [(f'content.documents[{i}].id',d['id'],2) for i,d in enumerate(c['documents'])]
  if r=='cache-aside':budgets=[('content.key',c['key'],7.5)]
  for field,text,budget in budgets:
   if visual_units(text)>budget:errors.append({'code':'E_ART_TEXT','field':field,'message':f'实体道具文字上限 {budget} 汉字宽度单位','hint':'缩短内容，不缩小字体或替换成文本框。'})
 if errors:raise ValueError(json.dumps(errors,ensure_ascii=False))
 p=compile_recipe(spec)
 p['presentation']='illustrated-studio'
 p['art']={'version':'0.4.0','assets':ASSETS[p['recipe']], 'fallback':'fail-not-diagram','source':'Original MIT vector assets; original robot/terminal retained.'}
 return p
def hashes(path):
 return {p.relative_to(path).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(path.rglob('*')) if p.is_file() and p.name!='build-files.json'}
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def build(spec,out):
 p=compile_illustrated(spec);out=Path(out).absolute()
 if out.exists() or out.is_symlink():raise FileExistsError(f'E_EXISTS: {out}; use a new version directory')
 out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.illustrated-',dir=out.parent) as t:
  stage=Path(t)/'project';stage.mkdir();(stage/'runtime').mkdir()
  write(stage/'recipe.json',normalized(spec));write(stage/'project.json',p)
  for name in RUNTIME:shutil.copy2(ROOT/'runtime'/name,stage/'runtime'/name)
  (stage/'index.html').write_text(HTML.replace('Explain Motion · Recipe Preview','How It Moves · Illustrated Studio'),encoding='utf-8')
  (stage/'scene.mjs').write_text("import {start} from './runtime/illustrated-player.mjs';\nconst spec=window.__PROJECT__ ?? await (await fetch('./project.json')).json();\nstart(spec);\n",encoding='utf-8')
  (stage/'preview.html').write_text(bundle_html(stage,stage),encoding='utf-8')
  rows=['# '+p['title'],'','Presentation: illustrated-studio. Same semantic events as recipe mode.','','| Seconds | Action |','|---|---|']
  rows += [f"|{e['start']:.2f}–{e['end']:.2f}|{e['caption']}|" for e in p['events']]
  rows+=['','Art lock: '+', '.join(p['art']['assets']), '','Human review is required for beauty, framing and technical truth.']
  (stage/'storyboard.md').write_text('\n'.join(rows)+'\n',encoding='utf-8');write(stage/'build-files.json',hashes(stage))
  if out.exists():raise FileExistsError(out)
  stage.rename(out)
 return p
def check(path):
 path=Path(path)
 if not path.is_dir():
  try:compile_illustrated(load(path));return []
  except (ValueError,OSError) as e:return [str(e)]
 try:
  p=load(path/'project.json');s=load(path/'recipe.json');errors=[]
  if p!=compile_illustrated(s):errors.append('E_CONTRACT: source and compiled project differ')
  manifest=load(path/'build-files.json')
  if not isinstance(manifest,dict) or not manifest:raise ValueError('invalid build manifest')
  for rel,h in manifest.items():
   f=path/rel
   if f.is_symlink() or not f.resolve().is_relative_to(path.resolve()) or not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=h:errors.append('E_FILE_CHANGED: '+rel)
  return errors
 except (OSError,ValueError,TypeError,KeyError) as e:return ['E_BUILD: '+str(e)]
def main():
 ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
 ip=sub.add_parser('init');ip.add_argument('--recipe',choices=DURATIONS,required=True);ip.add_argument('--out',type=Path,required=True)
 cp=sub.add_parser('check');cp.add_argument('path',type=Path)
 bp=sub.add_parser('build');bp.add_argument('path',type=Path);bp.add_argument('--out',type=Path,required=True);bp.add_argument('--render',action='store_true')
 a=ap.parse_args()
 try:
  if a.command=='init':
   if a.out.exists() or a.out.is_symlink():raise FileExistsError('E_EXISTS: '+str(a.out))
   a.out.parent.mkdir(parents=True,exist_ok=True)
   with a.out.open('x',encoding='utf-8') as f:f.write(json.dumps(example(a.recipe),ensure_ascii=False,indent=2)+'\n')
   print(a.out);return
  e=check(a.path)
  if e:raise ValueError('\n'.join(e))
  if a.command=='check':print('OK: structure and integrity; visual/technical review separate');return
  p=build(load(a.path),a.out)
  if a.render:subprocess.run([sys.executable,str(ROOT/'scripts/render.py'),str(a.out),'--out',str(a.out/'video.mp4')],check=True)
  print(json.dumps({'ok':True,'preview':str(a.out/'preview.html'),'frames':round(p['fps']*p['duration']),'video':str(a.out/'video.mp4') if a.render else None},ensure_ascii=False))
 except (OSError,ValueError,subprocess.CalledProcessError) as e:print(str(e),file=sys.stderr);raise SystemExit(2)
if __name__=='__main__':main()
