#!/usr/bin/env python3
"""Local release integrity checks. No network access. --write-manifest is explicit."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote
from publish_github import scan_public_files, verify_manifest, PublishError

ROOT=Path(__file__).resolve().parents[1]
IGNORED={'.git','.venv','__pycache__','.pytest_cache','node_modules','build','work'}

def candidates():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and
                  not (set(p.relative_to(ROOT).parts)&IGNORED) and p.name!='release-files.json')

def check_links():
    errors=[]
    for name in ('README.md','README.en.md','CONTRIBUTING.md','SECURITY.md','docs/PUBLISHING.md'):
        p=ROOT/name
        text=p.read_text(encoding='utf-8')
        # This deliberately checks local Markdown file/image links, not remote URLs or heading anchors.
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if re.match(r'(?:https?://|mailto:|#)',link): continue
            target=(p.parent/unquote(link.split('#')[0])).resolve()
            if not target.exists():errors.append(f'{name}: missing {link}')
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-manifest',action='store_true',help='After reviewing changes, regenerate the allowlisted release hashes')
    args=parser.parse_args()
    try:
        scan_public_files(ROOT)
        assert (ROOT/'docs/index.html').read_bytes()==(ROOT/'technical-animation/examples/agent-loop/preview.html').read_bytes(), 'Published HTML differs from source preview'
        assert (ROOT/'docs/media/agent-loop-10s.mp4').read_bytes()==(ROOT/'technical-animation/examples/agent-loop/agent-loop-10s.mp4').read_bytes(), 'Published MP4 differs from reference'
        errors=check_links()
        if errors:raise PublishError('\n'.join(errors))
        if args.write_manifest:
            data={'schema':1,'note':'Review file contents before regenerating. SHA256 is integrity evidence, not a signature.',
                  'files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in candidates()}}
            (ROOT/'release-files.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        files=verify_manifest()
        print(f'PASS: {len(files)} allowlisted release files; HTML/MP4 copies identical; local README links resolve; no prohibited files detected.')
        print('Remote GitHub publication and GitHub Pages deployment were NOT checked by this offline command.')
        return 0
    except (PublishError,AssertionError,OSError,ValueError) as exc:
        print(f'RELEASE CHECK FAILED: {exc}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
