#!/usr/bin/env python3
"""Publish this reviewed release as a NEW public GitHub repo and configure Pages.

Uses your locally authenticated GitHub CLI. Never asks for or prints tokens.
No force-push, no overwrite, no private-to-public conversion, no automatic install.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PublishError(RuntimeError):
    pass

def validate_target(owner: str, repo: str) -> str:
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', owner):
        raise PublishError('Invalid personal GitHub login.')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', repo) or repo in ('.', '..'):
        raise PublishError('Invalid repository name; do not include paths or spaces.')
    return f'{owner}/{repo}'

def require_public(consent: bool) -> None:
    if not consent:
        raise PublishError('Explicit --public is required. No repository was created.')

def check_identity(profile: dict, owner: str) -> str:
    if profile.get('login', '').lower() != owner.lower():
        raise PublishError(f"Logged in as {profile.get('login')!r}, not {owner!r}. Use gh auth switch first.")
    uid = profile.get('id')
    if not isinstance(uid, int) or uid < 1:
        raise PublishError('GitHub returned an invalid account ID.')
    return f'{uid}+{profile["login"]}@users.noreply.github.com'

def check_missing_repo(result: subprocess.CompletedProcess) -> None:
    if result.returncode == 0:
        raise PublishError('Repository already exists. It was NOT overwritten or made public. '
                           'Use normal git push after review, or --pages-only to configure the demo.')
    message = (result.stderr or '') + (result.stdout or '')
    if not re.search(r'HTTP\s+404\b', message, re.I):
        raise PublishError('Cannot verify repository availability: ' + message.strip()[:500])

def scan_public_files(root: Path) -> None:
    ignored = {'.git', '.venv', '__pycache__', '.pytest_cache', 'node_modules', 'build', 'work'}
    secrets = re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    for p in root.rglob('*'):
        if set(p.relative_to(root).parts) & ignored:
            continue
        if p.is_symlink():
            raise PublishError(f'Symlinks are not allowed in this release: {p.relative_to(root)}')
        if not p.is_file():
            continue
        if p.name == '.env' or p.name.startswith('.env.') or p.suffix.lower() in {'.pem','.key','.ttf','.otf','.ttc','.woff','.woff2'}:
            raise PublishError(f'Private or font file must not be published: {p.relative_to(root)}')
        if p.stat().st_size > 50 * 1024 * 1024:
            raise PublishError(f'File exceeds the release size limit: {p.relative_to(root)}')
        if p.suffix in {'.py','.json','.md','.txt','.yml','.yaml','.html','.mjs','.sh'}:
            if secrets.search(p.read_text(encoding='utf-8')):
                raise PublishError(f'Possible credential detected in {p.relative_to(root)}')

def run(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env['GH_HOST'] = 'github.com'
    result = subprocess.run(list(args), cwd=ROOT, text=True, capture_output=True, env=env)
    if check and result.returncode:
        raise PublishError(f'{args[0]} failed: {(result.stderr or result.stdout).strip()[:1000]}')
    return result

def verify_manifest() -> list[str]:
    manifest_path = ROOT / 'release-files.json'
    if not manifest_path.exists():
        raise PublishError('Missing release-files.json; use the complete release folder.')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    files = manifest['files']
    for rel, expected in files.items():
        p=(ROOT/rel).resolve()
        if not p.is_relative_to(ROOT) or not p.is_file():
            raise PublishError(f'Missing or invalid release file: {rel}')
        if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise PublishError(f'Release file changed: {rel}. Review edits and regenerate the manifest before publishing.')
    return sorted(files) + ['release-files.json']

def configure_pages(full: str) -> dict:
    existing = run('gh','api','--hostname','github.com',f'repos/{full}/pages',check=False)
    args = ['gh','api','--hostname','github.com','--method']
    if existing.returncode == 0:
        args += ['PUT', f'repos/{full}/pages']
    elif re.search(r'HTTP\s+404\b', (existing.stderr or '')+(existing.stdout or ''),re.I):
        args += ['POST', f'repos/{full}/pages']
    else:
        raise PublishError('Cannot read Pages settings. Repository may be published, but Pages was NOT verified: '+existing.stderr[:500])
    run(*args,'-f','build_type=legacy','-f','source[branch]=main','-f','source[path]=/docs')
    pages = json.loads(run('gh','api','--hostname','github.com',f'repos/{full}/pages').stdout)
    if pages.get('source', {}).get('branch') != 'main' or pages.get('source', {}).get('path') != '/docs':
        raise PublishError('Pages source read-back did not match main:/docs.')
    return pages

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner',default='wz20',help='Must match your authenticated personal account')
    parser.add_argument('--repo',default='how-it-moves')
    parser.add_argument('--public',action='store_true',help='Explicitly authorize public publication')
    parser.add_argument('--dry-run',action='store_true',help='Local integrity check only; NO network or git writes')
    parser.add_argument('--pages-only',action='store_true',help='Configure Pages on an already public target; no commit/push')
    args=parser.parse_args()
    try:
        require_public(args.public)
        full=validate_target(args.owner,args.repo)
        scan_public_files(ROOT)
        paths=verify_manifest()
        if args.dry_run:
            print(f'DRY RUN ONLY. No repository has been created.\nTarget: {full} (PUBLIC)\n'
                  f'Reviewed files: {len(paths)}\nPages source: main:/docs\n'
                  'Actions: verify identity -> refuse existing repo -> commit allowlisted files -> create and push -> configure Pages')
            return 0
        for executable in ('git','gh'):
            if not shutil.which(executable):
                raise PublishError(f'Missing {executable}. Install GitHub CLI from https://cli.github.com/ '
                                   '(macOS/Homebrew: brew install gh), then run gh auth login --hostname github.com --web.')
        run('gh','auth','status','--hostname','github.com')
        profile=json.loads(run('gh','api','--hostname','github.com','user').stdout)
        email=check_identity(profile,args.owner)
        if args.pages_only:
            info=json.loads(run('gh','api','--hostname','github.com',f'repos/{full}').stdout)
            if info.get('private', True):
                raise PublishError('Target is private. Refusing to expose a private repository as a public demo.')
        else:
            check_missing_repo(run('gh','api','--hostname','github.com',f'repos/{full}',check=False))
            if (ROOT/'.git').exists():
                raise PublishError('This folder already has git history. No changes made. Use a clean extracted release for first publication.')
            # Nothing is staged outside the reviewed manifest. Existing user history is never touched.
            run('git','init','-b','main')
            run('git','config','user.name',profile['login'])
            run('git','config','user.email',email)
            run('git','add','--',*paths)
            run('git','commit','-m','feat: publish How It Moves skill and complete animation showcase')
            local_sha=run('git','rev-parse','HEAD').stdout.strip()
            run('gh','repo','create',full,'--public','--source','.', '--remote','origin','--push',
                '--description','Technical animation Skill: strict content recipes, causal motion, offline HTML, silent video, and advanced authoring.',
                '--homepage',f'https://{args.owner}.github.io/{args.repo}/')
            info=json.loads(run('gh','api','--hostname','github.com',f'repos/{full}').stdout)
            remote_sha=json.loads(run('gh','api','--hostname','github.com',f'repos/{full}/commits/main').stdout)['sha']
            if info.get('private',True) or local_sha != remote_sha:
                raise PublishError('Post-push visibility or commit verification failed. Inspect the repository before retrying.')
            print('Repository created and commit verified: '+info['html_url'])
        pages=configure_pages(full)
        print('Pages source configured: main:/docs')
        print('Demo URL: '+pages.get('html_url',f'https://{args.owner}.github.io/{args.repo}/'))
        print('Deployment may still be queued. Check Settings > Pages / Actions for the completed build; '
              'this message does NOT claim the site is already serving.')
        return 0
    except (PublishError, OSError, ValueError, KeyError) as exc:
        print(f'PUBLICATION STOPPED: {exc}',file=sys.stderr)
        print('No force-push or repository deletion was performed. If the repository was already created, '
              'retain this directory; retry Pages with --pages-only or inspect git status.',file=sys.stderr)
        return 1

if __name__=='__main__': raise SystemExit(main())
