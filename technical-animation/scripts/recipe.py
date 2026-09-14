#!/usr/bin/env python3
"""Model-friendly entrypoint: list | init | check | build | doctor.
Run `python scripts/recipe.py --help` from any directory; outputs never overwrite.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
from recipe_core import RECIPES, VERSION, validate_spec, compile_recipe, validate_compiled, normalized, digest
from bundle import bundle_html

ROOT=Path(__file__).resolve().parents[1]
HTML='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Explain Motion · Recipe Preview</title>
<style>*{box-sizing:border-box}html,body{margin:0;background:#24262c;font-family:system-ui;color:#fff}main{min-height:100vh;display:grid;align-content:center;gap:12px;padding:20px}canvas{width:100%;max-height:85vh;object-fit:contain;display:block}nav{display:flex;align-items:center;gap:16px;max-width:1100px;margin:auto;width:100%;font-size:14px}button{background:#ffcf50;border:0;border-radius:8px;padding:10px 20px;cursor:pointer;font-weight:bold}input{flex:1;min-width:30px}body.capture main{padding:0;display:block}body.capture nav,body.capture .sr-only{display:none}body.capture canvas{max-height:none;width:1920px;height:1080px}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}</style>
<main><canvas id="stage" width="1920" height="1080" role="img" aria-label="技术机制的动画示意；下方可播放、暂停和拖动时间轴。"></canvas><nav><button id="toggle" type="button">播放</button><input id="seek" type="range" min="0" max="719" value="0" aria-label="逐帧查看"><span id="clock">0.00 s</span></nav><p class="sr-only">本片使用虚构的教学数据演示机制，并非真实系统运行。方向、标签和颜色共同区分请求、结果与状态。</p></main>
<script type="module" src="./scene.mjs"></script></html>'''
SCENE="""// GENERATED. Edit recipe.json and rebuild; advanced authors should use a new project.
import {startRecipe} from './runtime/recipe-player.mjs';
const spec=window.__PROJECT__ ?? await (await fetch('./project.json')).json();
startRecipe(spec);
"""
class RecipeError(Exception):
 def __init__(self,code,field,message,hint):self.error=dict(code=code,field=field,message=message,hint=hint)
def load(path):
 if path.stat().st_size>256_000:raise RecipeError('E_SIZE',str(path),'配置超过 256KB','只填写该配方需要的少量内容。')
 def unique(pairs):
  d={}
  for k,v in pairs:
   if k in d:raise RecipeError('E_DUPLICATE',k,'JSON 键重复','删除重复字段，避免解析器静默覆盖。')
   d[k]=v
  return d
 return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique)
def dump(obj):print(json.dumps(obj,ensure_ascii=False,indent=2))
def ensure_new(out):
 if out.exists() or out.is_symlink():raise RecipeError('E_EXISTS',str(out),'输出已经存在，未覆盖','换一个新版本目录，例如 build/rag-v2；保留已确认版本。')
def write_json(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def generated_hashes(out):
 import hashlib
 return {p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file() and p.name!='build-files.json'}
def build(spec,out):
 p=compile_recipe(spec);out=out.absolute();ensure_new(out);out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.recipe-',dir=out.parent) as tmp:
  stage=Path(tmp)/'project';stage.mkdir()
  write_json(stage/'recipe.json',normalized(spec));write_json(stage/'project.json',p)
  shutil.copytree(ROOT/'runtime',stage/'runtime',ignore=shutil.ignore_patterns('__pycache__'))
  (stage/'index.html').write_text(HTML,encoding='utf-8');(stage/'scene.mjs').write_text(SCENE,encoding='utf-8')
  (stage/'preview.html').write_text(bundle_html(stage,stage),encoding='utf-8')
  lines=['# '+p['title'],'','生成版本：'+VERSION,'','输入：recipe.json；不要直接编辑自动生成的 project.json 或 scene.mjs。','',p['truth'],'','## 自动分镜','| 时间 | 动作 | 触发关系 |','|---|---|---|']
  lines += [f"| {e['start']:.2f}–{e['end']:.2f}s | {e['caption']} | {e.get('caused_by','开始')} → {e['id']} |" for e in p['events']]
  lines += ['','## 尚须人工核验','文字的技术真实性、回答是否被证据支持、审美和观众理解效果未由编译器自动证明。','已检查：字段类型、内容长度预算、时序模板、证据引用集合、输出文件完整性。']
  (stage/'storyboard.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
  write_json(stage/'build-files.json',generated_hashes(stage))
  ensure_new(out);stage.rename(out)
 return p

def check_project(path):
 errors=validate_compiled(load(path/'project.json'))
 try:
  spec=load(path/'recipe.json');p=load(path/'project.json')
  if normalized(spec)!=p.get('input_spec'):errors.append(dict(code='E_INPUT_CHANGED',field='recipe.json',message='输入已改但尚未重建',hint='build 到新目录。'))
  import hashlib
  manifest=load(path/'build-files.json')
  if not isinstance(manifest,dict) or not manifest:raise ValueError('Missing build manifest mapping')
  if not all(isinstance(k,str) and isinstance(v,str) for k,v in manifest.items()):raise ValueError('Invalid build hashes')
  for rel,expected in manifest.items():
   item=path/rel
   if item.is_symlink() or not item.resolve().is_relative_to(path.resolve()) or not item.is_file() or hashlib.sha256(item.read_bytes()).hexdigest()!=expected:
    errors.append(dict(code='E_FILE_CHANGED',field=rel,message='生成文件缺失或改变',hint='从配方重新 build；不要直接改底层代码绕过检查。'))
 except (ValueError,KeyError,TypeError,OSError):errors.append(dict(code='E_BUILD',field=str(path),message='生成目录不完整',hint='从 recipe.json 重新 build 到新目录。'))
 return errors

def main():
 ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
 sub.add_parser('list',help='List supported mechanism recipes')
 sub.add_parser('doctor',help='Inspect local tools; never installs or charges')
 ip=sub.add_parser('init',help='Copy a complete content example');ip.add_argument('--recipe',required=True,choices=RECIPES);ip.add_argument('--out',required=True,type=Path)
 cp=sub.add_parser('check',help='Validate a JSON spec or generated project');cp.add_argument('path',type=Path)
 bp=sub.add_parser('build',help='Compile JSON into offline HTML and optional MP4');bp.add_argument('path',type=Path);bp.add_argument('--out',type=Path,required=True);bp.add_argument('--render',action='store_true');bp.add_argument('--jobs',type=int,default=2);bp.add_argument('--browser')
 a=ap.parse_args()
 try:
  if a.command=='list':dump(dict(ok=True,recipes=RECIPES,mode='recipe (default)',schema=str(ROOT/'schemas/recipe.schema.json')));return 0
  if a.command=='doctor':
   browser=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome') or os.environ.get('CHROMIUM_PATH')
   dump(dict(ok=True,python=sys.version.split()[0],offline_build='stdlib only',playwright=importlib.util.find_spec('playwright') is not None,browser=browser or 'Playwright managed browser must be installed separately',ffmpeg=shutil.which('ffmpeg'),ffprobe=shutil.which('ffprobe'),fonts='System CJK fonts required; not bundled',note='No tools installed, no external API calls made.'));return 0
  if a.command=='init':
   ensure_new(a.out);a.out.parent.mkdir(parents=True,exist_ok=True)
   with a.out.open('x',encoding='utf-8') as f:f.write((ROOT/'recipes'/f'{a.recipe}.json').read_text(encoding='utf-8'))
   dump(dict(ok=True,spec=str(a.out),next='Edit content fields; then recipe.py check SPEC'));return 0
  errors=check_project(a.path) if a.path.is_dir() else validate_spec(load(a.path))
  if errors:print(json.dumps(dict(ok=False,errors=errors),ensure_ascii=False,indent=2),file=sys.stderr);return 2
  if a.command=='check':dump(dict(ok=True,scope='structure/contract, NOT technical truth or aesthetic quality'));return 0
  if not 1<=a.jobs<=8:raise RecipeError('E_JOBS','jobs','jobs 必须为 1–8','建议 2。')
  p=build(load(a.path),a.out)
  if a.render:
   cmd=[sys.executable,str(ROOT/'scripts/render.py'),str(a.out),'--out',str(a.out/'video.mp4'),'--jobs',str(a.jobs)]
   if a.browser:cmd+=['--browser',a.browser]
   subprocess.run(cmd,check=True)
  dump(dict(ok=True,project=str(a.out),preview=str(a.out/'preview.html'),frames=round(p['fps']*p['duration']),video=str(a.out/'video.mp4') if a.render else None,review='Open preview; inspect event boundaries and wording.'));return 0
 except RecipeError as exc:errors=[exc.error]
 except subprocess.CalledProcessError:errors=[dict(code='E_RENDER',field='video.mp4',message='HTML 已完成，MP4 渲染失败',hint='保留项目，按 render.py 报错修复环境后单独重试渲染。')]
 except (OSError,ValueError,TypeError) as exc:errors=[dict(code='E_INPUT',field=str(getattr(a,'path','input')),message=str(exc),hint='提供合法 UTF-8 JSON；从 init 的完整示例开始。')]
 print(json.dumps(dict(ok=False,errors=errors),ensure_ascii=False,indent=2),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
