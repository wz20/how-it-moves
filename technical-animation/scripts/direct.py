#!/usr/bin/env python3
"""Content-only editorial directing. Owns shot timing, never executes content as code."""
from __future__ import annotations
import argparse
import copy
import hashlib
import html
import json
import math
import re
import shutil
import sys
from pathlib import Path
from bundle import bundle_html
from validate import validate_project

ROOT = Path(__file__).resolve().parents[1]
PATTERN = 'partition-search'
RUNTIME = ('motion.mjs', 'drawing.mjs', 'editorial.mjs', 'partition-search.mjs')

class ContractError(ValueError):
    def __init__(self, code, field, message, hint):
        super().__init__(message)
        self.code, self.field, self.hint = code, field, hint
    def record(self):
        return dict(code=self.code, field=self.field, message=str(self), hint=self.hint)

def fail(code, field, message, hint='只修改指出的输入字段；不要修改运行库或验证器。'):
    raise ContractError(code, field, message, hint)

def load_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: fail('E_DUPLICATE', key, 'JSON 字段重复，不能静默覆盖。')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs)

def keys(obj, allowed, required, field):
    if not isinstance(obj, dict): fail('E_FIELD', field, '必须是对象。')
    unknown, missing = set(obj) - set(allowed), set(required) - set(obj)
    if unknown: fail('E_FIELD', field + '.' + sorted(unknown)[0], '不支持该字段。')
    if missing: fail('E_FIELD', field + '.' + sorted(missing)[0], '缺少必填字段。')

def text(value, field, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
        fail('E_TEXT', field, f'需要 1—{limit} 个字符，不含换行或控制字符。', '缩短文案，不缩小字号、不塞入脚本。')
    return value.strip()

def identifier(value, field, seen):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,7}', value) or value in seen:
        fail('E_ID', field, 'ID 必须全局唯一，以英文字母开头，最长 8 字符。')
    seen.add(value)

def normalize(source):
    required = ('schema_version', 'pattern', 'title', 'query', 'groups', 'selected_group', 'segments', 'top_k', 'takeaway')
    keys(source, required + ('duration', 'fps', 'aspect', 'style', 'audio'), required, '$')
    s = copy.deepcopy(source)
    if type(s['schema_version']) is not int or s['schema_version'] != 1:
        fail('E_FORMAT', 'schema_version', '目前只支持版本 1。')
    if s['pattern'] != PATTERN:
        fail('E_PATTERN', 'pattern', '目前导演模式仅实现 partition-search。', '不匹配时使用其他已支持配方或高级模式；不要改标签硬套。')
    for name, limit in (('title', 24), ('query', 8), ('takeaway', 24)):
        s[name] = text(s[name], name, limit)
    defaults = {'duration': 24, 'fps': 60, 'aspect': '16:9', 'style': 'paper-explainer', 'audio': 'none'}
    for k, v in defaults.items(): s.setdefault(k, v)
    if type(s['fps']) is not int or s['fps'] not in (30, 60): fail('E_FORMAT', 'fps', '仅支持 30 或 60fps。')
    d = s['duration']
    if type(d) not in (int, float) or not math.isfinite(d) or not 20 <= d <= 40 or abs(d * s['fps'] - round(d * s['fps'])) > 1e-6:
        fail('E_FORMAT', 'duration', '需要 20—40 秒且总帧数为整数。', '缩减内容或增加时长，不压缩掉因果动作与阅读停留。')
    for k in ('aspect', 'style', 'audio'):
        if s[k] != defaults[k]: fail('E_FORMAT', k, f'本模式只支持 {defaults[k]}。', '不支持的画幅/配音/画风转高级模式，不静默替换。')
    seen = {'Q1'}
    if not isinstance(s['groups'], list) or len(s['groups']) != 3:
        fail('E_FIELD', 'groups', '本构图需要 3 个分组。')
    for i, g in enumerate(s['groups']):
        field = f'groups[{i}]'; keys(g, ('id', 'label'), ('id', 'label'), field)
        identifier(g['id'], field + '.id', seen); g['label'] = text(g['label'], field + '.label', 6)
    if s['selected_group'] not in [g['id'] for g in s['groups']]:
        fail('E_REFERENCE', 'selected_group', '必须引用一个 groups.id。')
    if not isinstance(s['segments'], list) or len(s['segments']) != 3:
        fail('E_FIELD', 'segments', '本构图需要目标分组内的 3 个段。')
    for i, seg in enumerate(s['segments']):
        field = f'segments[{i}]'; keys(seg, ('id', 'label', 'candidates'), ('id', 'label', 'candidates'), field)
        identifier(seg['id'], field + '.id', seen); seg['label'] = text(seg['label'], field + '.label', 4)
        if not isinstance(seg['candidates'], list) or len(seg['candidates']) != 2:
            fail('E_FIELD', field + '.candidates', '每个段提供 2 个教学候选。')
        for j, row in enumerate(seg['candidates']):
            loc = field + f'.candidates[{j}]'; keys(row, ('id', 'score'), ('id', 'score'), loc)
            identifier(row['id'], loc + '.id', seen)
            v = row['score']
            if type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1:
                fail('E_SCORE', loc + '.score', '相似度示意值必须是 0—1 的有限数值。')
    if type(s['top_k']) is not int or not 1 <= s['top_k'] <= 3: fail('E_FIELD', 'top_k', '本画面支持 Top 1—3。')
    return s

def compile_project(s):
    s = normalize(s); fps = s['fps']; scale = s['duration'] / 24
    frame = lambda sec: round(sec * scale * fps)
    bounds = (0, 3.5, 7, 10, 16, 20.5, 24)
    names = ('overview', 'select', 'expand', 'parallel', 'rank', 'recap')
    shots = [dict(id=name, start_frame=frame(bounds[i]), end_frame=frame(bounds[i+1])) for i, name in enumerate(names)]
    events = []
    def event(eid, kind, a, b, actor, label, after=(), target=None):
        start, end = frame(a), frame(b)
        item = dict(id=eid, kind=kind, start=start/fps, end=end/fps, start_frame=start, end_frame=end,
                    actor=actor, label=label, after=list(after))
        if after: item['caused_by'] = after[-1]
        if target: item['target'] = target
        events.append(item)
    event('choose', 'select', 3.5, 4.7, 'Q1', '指定分区', target=s['selected_group'])
    event('expand', 'expand', 7, 8.3, s['selected_group'], '展开内部结构', ('choose',))
    for i, seg in enumerate(s['segments']):
        event('call_' + seg['id'], 'call', 10.1, 11.3, 'Q1', 'Q1', ('expand',), seg['id'])
        event('work_' + seg['id'], 'process', 11.3, 12.9 + i*.3, seg['id'], '局部检索', ('call_'+seg['id'],))
        event('return_' + seg['id'], 'result', 13 + i*.3, 14.5 + i*.3, seg['id'], '候选返回', ('work_'+seg['id'],), 'reducer')
    returns = ['return_' + seg['id'] for seg in s['segments']]
    event('rank', 'aggregate', 16.8, 18.2, 'reducer', '汇总排序', returns)
    event('deliver', 'result', 18.9, 20.1, 'reducer', 'TopK', ('rank',), 'Q1')
    lookup = {e['id']: e for e in events}
    for e in events:
        for dep in e['after']:
            if lookup[dep]['end_frame'] > e['start_frame']: fail('E_CAUSAL', e['id'], '内部排期违反依赖。')
    rows = [dict(row, segment=seg['id']) for seg in s['segments'] for row in seg['candidates']]
    ranked = sorted(rows, key=lambda row: (-row['score'], row['id']))
    project = dict(title=s['title'], width=1920, height=1080, fps=fps, duration=s['duration'], takeaway=s['takeaway'],
                   entry='index.html', ready_for_render=True, requires_feedback=False, audio='none',
                   events=events, assets=[dict(path='runtime/partition-search.mjs', origin='original-procedural-vector', used=True, status='approved')],
                   sources=[dict(title='Milvus partition-search scope; not a full architecture specification', url='https://milvus.io/docs/v2.4.x/single-vector-search.md')],
                   direction=dict(version=1, pattern=PATTERN, query_id='Q1', config=s, shots=shots, ranked=ranked,
                     limitations=['Synthetic scores; higher means more similar, not probability.', 'Three segments inside one explicitly selected partition; not a physical node mapping.', 'Ranks only the supplied candidates; no claim of exact global ANN recall or production latency.']))
    errors = validate_project(project)
    if errors: fail('E_CAUSAL', 'project', '; '.join(errors))
    return project

def player_html(title):
    return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>''' + html.escape(title) + ''' · How It Moves</title>
<style>*{box-sizing:border-box}body{margin:0;background:#182b40;color:white;font:16px system-ui}main{max-width:1440px;margin:auto;padding:16px}canvas{display:block;width:100%;height:auto;background:#f7f8fa}nav{display:flex;gap:16px;align-items:center;margin-top:14px}button{padding:10px 20px;border:0;border-radius:8px;background:#a6d8eb;font-weight:bold}input{flex:1;min-width:60px}body.capture main{padding:0;max-width:none}body.capture nav,body.capture .note{display:none}body.capture canvas{width:1920px;height:1080px}.note{font-size:13px;color:#c5d5e6}</style>
<main><canvas id="stage" width="1920" height="1080" role="img" aria-label="按分区缩小范围，展开三个段，等待候选返回后排序。"></canvas>
<nav><button id="toggle">播放</button><input id="seek" type="range" min="0" value="0" aria-label="逐帧拖动"><span id="clock"></span></nav>
<p class="note">原创机制示意 · 非实时执行 · 分数为虚构相似度，不是概率或性能实测 · 来源与限制见工程 project.json</p></main>
<script type="module" src="scene.mjs"></script></html>'''

def build(source, out):
    p = compile_project(source); out = Path(out).resolve()
    if out.exists(): fail('E_EXISTS', str(out), '输出目录已存在。', '使用 v2/v3 新目录，保留确认稿。')
    out.parent.mkdir(parents=True, exist_ok=True)
    try: out.mkdir()
    except FileExistsError: fail('E_EXISTS', str(out), '输出目录被其他进程创建。')
    try:
        (out / 'runtime').mkdir()
        for name in RUNTIME: shutil.copy2(ROOT / 'runtime' / name, out / 'runtime' / name)
        for name, data in [('source.json', p['direction']['config']), ('project.json', p)]:
            (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        (out / 'index.html').write_text(player_html(p['title']), encoding='utf-8')
        (out / 'scene.mjs').write_text("import {start} from './runtime/partition-search.mjs';\nstart(window.__PROJECT__);\n", encoding='utf-8')
        (out / 'preview.html').write_text(bundle_html(out, out), encoding='utf-8')
        rows = ['# Generated shot plan', '', 'Single event contract; do not edit generated scene code.', '']
        rows += [f"- {x['id']}: frames {x['start_frame']}—{x['end_frame']-1}" for x in p['direction']['shots']]
        (out / 'storyboard.md').write_text('\n'.join(rows)+'\n', encoding='utf-8')
        files = {f.relative_to(out).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.rglob('*')) if f.is_file()}
        (out / 'build-files.json').write_text(json.dumps(files, indent=2)+'\n', encoding='utf-8')
    except Exception:
        shutil.rmtree(out); raise
    return out

def check_build(path):
    path = Path(path).resolve()
    try:
        manifest = load_json(path / 'build-files.json')
        if not isinstance(manifest, dict) or not manifest: raise ValueError('invalid manifest')
        required = {'source.json', 'project.json', 'index.html', 'scene.mjs', 'preview.html', 'storyboard.md'} | {'runtime/' + name for name in RUNTIME}
        if set(manifest) != required: fail('E_INTEGRITY', 'build-files.json', '校验清单不完整或含未知文件。')
        for name, digest in manifest.items():
            file = (path / name).resolve()
            if not file.is_relative_to(path) or not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
                fail('E_INTEGRITY', name, '生成文件被修改或缺失。', '修改 source.json 的内容，并重新生成到新目录。')
        expected = compile_project(load_json(path / 'source.json'))
        if expected != load_json(path / 'project.json'):
            fail('E_INTEGRITY', 'project.json', '事件合同与原始配置不一致。')
    except (OSError, ValueError, TypeError) as e:
        if isinstance(e, ContractError): raise
        fail('E_INTEGRITY', str(path), str(e), '重新生成到新目录；校验和不是安全签名。')
    return expected

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('list')
    init = sub.add_parser('init'); init.add_argument('--out', type=Path, required=True)
    check = sub.add_parser('check'); check.add_argument('source', type=Path)
    make = sub.add_parser('build'); make.add_argument('source', type=Path); make.add_argument('--out', type=Path, required=True)
    a = parser.parse_args()
    try:
        if a.cmd == 'list':
            result = {'pattern': PATTERN, 'scope': 'explicit partition -> three segment searches -> merge candidate scores', 'duration': '20—40 seconds', 'style': 'paper-explainer'}
        elif a.cmd == 'init':
            a.out.parent.mkdir(parents=True, exist_ok=True)
            with a.out.open('x', encoding='utf-8') as f: f.write((ROOT / 'directing/partition-search.json').read_text(encoding='utf-8'))
            result = {'source': str(a.out)}
        else:
            if a.source.is_dir():
                p = check_build(a.source); data = p['direction']['config']
            else: data = normalize(load_json(a.source))
            result = {'pattern': data['pattern']}
            if a.cmd == 'build': result['output'] = str(build(data, a.out))
        print(json.dumps({'ok': True, **result}, ensure_ascii=False)); return 0
    except (OSError, ValueError, TypeError) as e:
        error = e if isinstance(e, ContractError) else ContractError('E_EXISTS' if isinstance(e, FileExistsError) else 'E_INPUT', str(getattr(a, 'source', getattr(a, 'out', '$'))), str(e), '检查输入路径/JSON；已有输出请换新目录。')
        print(json.dumps({'ok': False, 'errors': [error.record()]}, ensure_ascii=False)); return 2
if __name__ == '__main__': raise SystemExit(main())
