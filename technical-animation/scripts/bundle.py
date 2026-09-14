#!/usr/bin/env python3
"""Produce an offline single HTML preview from the local, static ES-module graph.
No npm install, external network, API keys, or font embedding. Dynamic imports,
remote modules and arbitrary asset fetches are deliberately not implemented.
"""
from __future__ import annotations
import base64,json,re,argparse
from pathlib import Path
IMPORT=re.compile(r'''(\bfrom\s*|\bimport\s*)(["'])(\.{1,2}/[^"']+)\2''')
SCRIPT=re.compile(r'''<script\s+type=["']module["']\s+src=["']([^"']+)["']\s*>\s*</script>''')

def bundle_html(project:Path,root:Path)->str:
    project=project.resolve();root=root.resolve()
    data=json.loads((project/'project.json').read_text(encoding='utf-8'))
    entry=(project/data['entry']).resolve()
    if not entry.is_relative_to(root):raise ValueError('entry escapes project/skill root')
    cache={};visiting=set()
    def inline(path:Path)->str:
        path=path.resolve()
        if not path.is_relative_to(root):raise ValueError(f'Module escapes allowed root: {path}')
        if path in cache:return cache[path]
        if path in visiting:raise ValueError('Cyclic imports unsupported by the offline adapter')
        visiting.add(path);code=path.read_text(encoding='utf-8')
        code=IMPORT.sub(lambda m:m[1]+m[2]+inline(path.parent/m[3])+m[2],code)
        visiting.remove(path)
        uri='data:text/javascript;base64,'+base64.b64encode(code.encode()).decode();cache[path]=uri;return uri
    html=entry.read_text(encoding='utf-8')
    if not SCRIPT.search(html):raise ValueError('Expected <script type="module" src="...">')
    injected='<script>window.__PROJECT__='+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+';</script>'
    html=SCRIPT.sub(lambda m:injected+'<script type="module" src="'+inline(entry.parent/m[1])+'"></script>',html)
    return html

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 root=Path(__file__).resolve().parents[1];project=a.project.resolve()
 if not project.is_relative_to(root):root=project
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(bundle_html(project,root),encoding='utf-8');print(a.out)
if __name__=='__main__':main()
