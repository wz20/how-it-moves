#!/usr/bin/env python3
"""Regenerate the three public illustrated demos, never overwrite legacy demos.
Requires local Playwright/Chromium, FFmpeg and system CJK fonts. No model/API key.
This script never pushes; the dedicated repository workflow publishes its outputs.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'technical-animation'
sys.path.insert(0,str(SKILL/'scripts'));sys.path.insert(0,str(SKILL/'tests'))
import illustrate
from check_illustrated import check_all

def run(*args):subprocess.run([str(x) for x in args],check=True)
def update_readme(name):
 path=ROOT/name;text=path.read_text(encoding='utf-8');en=name.endswith('.en.md')
 start='<!-- ILLUSTRATED-STUDIO:BEGIN -->';end='<!-- ILLUSTRATED-STUDIO:END -->'
 text=re.sub(re.escape(start)+r'.*?'+re.escape(end)+r'\n*','',text,flags=re.S)
 titles=['Feedback and retry','Retrieval and evidence','Cache miss and hit'] if en else ['反馈与重试','检索与证据','缓存：未命中与命中']
 captions=['Original jointed robot and physical terminal. Feedback changes the next action.','Archive originals stay put. Evidence copies enter a ring binder; the press prints a cited answer.','A physical drawer opens empty, stores a key/value copy, and serves the next hit.'] if en else ['保留初版关节机器人与实体终端；先看反馈，再修改与验证。','档案柜保留原件，证据副本进入活页本，生成机输出带引用的回答。','快取柜先打开空抽屉，再保存键值副本；同一个键第二次命中，不再回源。']
 sections=[]
 for i,r in enumerate(illustrate.DURATIONS):
  dur=illustrate.DURATIONS[r];title=titles[i];page=f'https://wz20.github.io/how-it-moves/illustrated/{r}.html'
  sec=f'### {title} · {dur}s · Illustrated Studio\n\n[![{title}](docs/illustrated/media/{r}.gif)]({page})\n\n{captions[i]}\n\n[▶ HTML]({page}) · [1080p60 MP4](docs/illustrated/media/{r}.mp4)\n\n'
  pattern=r'### '+re.escape(title)+r'[^\n]*\n.*?(?=\n### |\n<details>|\n## |\Z)'
  text,n=re.subn(pattern,lambda m:sec.rstrip()+'\n',text,count=1,flags=re.S)
  if not n:sections.append(sec)
 heading='## v0.4 · Physical comic assets, content-only authoring' if en else '## v0.4 · 精致漫画素材，不再退化成技术图'
 intro='Original artwork is preserved and the three mechanism demonstrations are rebuilt using a shared, content-driven illustrated presentation. The renderer owns the props, poses and camera; the model edits validated content only. No weaker-model or audience benchmark is claimed.' if en else '保留初版的精致角色与实体道具，重制 Agent、RAG、缓存三个案例。模型只填写内容，素材、表演和构图由运行库提供；不需要普通模型重新写动画代码。自动检查不等于审美、弱模型成功率或学习效果评测。'
 block=f'''{start}
{heading}

{intro}

```bash
python3 technical-animation/scripts/illustrate.py init --recipe feedback-retry --out work/agent.json
python3 technical-animation/scripts/illustrate.py check work/agent.json
python3 technical-animation/scripts/illustrate.py build work/agent.json --out build/agent-v1 --render
```

[Guide / 使用指南](technical-animation/references/illustrated-mode.md) · [All three demos](docs/illustrated/index.html)

18–40s · 1920×1080 · 30/60fps · silent / 无声。Old demos are preserved / 原版保留。
{''.join(sections)}{end}

'''
 anchor='## Animation showcase' if en else '## 动画效果展示'
 if anchor in text:text=text.replace(anchor,block+anchor,1)
 else:text=block+text
 text=text.replace('## 三套真正能运行的配方','## 兼容保留的旧版配方').replace('## 60 秒开始：不用写动画代码','## 旧版配方入口（兼容保留）')
 text=text.replace('## Three working recipes','## Legacy recipes (preserved)').replace('## Quick start — no animation code','## Legacy recipe entry point')
 path.write_text(text,encoding='utf-8')

def update_skill():
 path=SKILL/'SKILL.md';text=path.read_text(encoding='utf-8')
 text=text.replace('version: "0.3.0"','version: "0.4.0"')
 section='## 默认选择：精致漫画，而不是动态技术图\n\nAgent 反馈、RAG、缓存三个机制默认使用 [Illustrated Studio](references/illustrated-mode.md)。它保持初版大机器人、实体终端、档案柜、活页本、快取抽屉等完整素材，让普通模型只填内容。不要用小图标、代码面板和通用圆角框替代已经确认的美术。\n\n```bash\npython SKILL_DIR/scripts/illustrate.py init --recipe feedback-retry --out PROJECT_DIR/source.json\npython SKILL_DIR/scripts/illustrate.py check PROJECT_DIR/source.json\npython SKILL_DIR/scripts/illustrate.py build PROJECT_DIR/source.json --out PROJECT_DIR/v1 --render\n```\n\n另外两个 recipe：`retrieval-evidence`、`cache-aside`。默认20/20/22秒；18—40秒、16:9、30/60fps、无声。没有渲染依赖时去掉 `--render`，明确只完成 HTML。\n\n先匹配机制，再选呈现：上述三个机制优先 `illustrate.py`；明确要旧版才用 `recipe.py`；分区检索或明确要架构图再用 `direct.py`。不匹配的新机制使用高级模式，不乱换标签。\n\n**美术和机制独立验收。** 暂停画面应有完整角色/实体道具及层次；动作应保持对象身份。`E_ART_TEXT` 时缩短文字，不缩成小字或退回技术图。素材缺失应报告失败；不得绕过验证器。片头/片尾至少查看实际关键帧，动作中段查看路径、接触和反馈，不能把测试通过说成审美已获用户认可。现有浏览器回退规则适用于此模式。\n\n'
 if '## 默认选择：精致漫画' not in text:
  if '## v0.3 导演路径' not in text:raise ValueError('Skill routing anchor changed; reconcile before publishing')
  text=text.replace('## v0.3 导演路径',section+'## v0.3 导演路径',1)
 path.write_text(text,encoding='utf-8')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--no-manifest',action='store_true',help='Local partial-source review only; CI must not use this flag');a=ap.parse_args()
 out=ROOT/'docs/illustrated';media=out/'media';media.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='illustrated-build-') as d:
  for r in illustrate.DURATIONS:
   project=Path(d)/r;p=illustrate.build(illustrate.example(r),project)
   run(sys.executable,SKILL/'scripts/render.py',project,'--out',media/f'{r}.mp4','--jobs','2')
   (out/f'{r}.html').write_text((project/'preview.html').read_text(encoding='utf-8'),encoding='utf-8')
   run('ffmpeg','-y','-hide_banner','-loglevel','error','-i',media/f'{r}.mp4','-filter_complex_threads','1','-filter_complex','fps=10,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer','-loop','0',media/f'{r}.gif')
   run('ffmpeg','-y','-hide_banner','-loglevel','error','-ss',str(p['duration']-1),'-i',media/f'{r}.mp4','-frames:v','1',media/f'{r}.png')
 checks=out/'checks';result=check_all(checks)
 (out/'index.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Illustrated Studio</title><style>body{max-width:1000px;margin:40px auto;padding:20px;background:#f5f0e5;font:18px system-ui}video{width:100%}section{margin:40px 0}a{color:#126a63}</style><h1>How It Moves · Illustrated Studio</h1>'+''.join(f'<section><h2>{illustrate.TITLES[r]}</h2><video controls playsinline preload="metadata" poster="media/{r}.png" src="media/{r}.mp4"></video><p><a href="{r}.html">可拖动 HTML</a> · <a href="media/{r}.mp4">MP4</a></p></section>' for r in illustrate.DURATIONS)+'</html>',encoding='utf-8')
 for name in ['README.md','README.en.md']:update_readme(name)
 update_skill()
 if not a.no_manifest:
  ignored={'.git','.venv','__pycache__','.pytest_cache','node_modules','build','work'}
  manifest={p.relative_to(SKILL).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SKILL.rglob('*')) if p.is_file() and p.name!='manifest.sha256.json' and not(set(p.relative_to(SKILL).parts)&ignored)}
  (SKILL/'manifest.sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  run(sys.executable,ROOT/'scripts/check_release.py','--write-manifest')
 print('DONE: three decoded MP4s, GIFs, offline HTML, frame checks and README. No GitHub push was attempted.')
if __name__=='__main__':main()
