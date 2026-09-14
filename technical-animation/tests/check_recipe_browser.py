#!/usr/bin/env python3
"""Build and verify all recipes in Chromium: causal states, seek, and controls.

Requires Playwright and Chromium. No model API, network, or FFmpeg is used.
The self-contained HTML is loaded with set_content, just like the renderer.
This is not a cross-model benchmark or a file:// browser-policy test.
"""
from __future__ import annotations
import argparse
import asyncio
import base64
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
from recipe import build
from recipe_core import RECIPES, state_at_frame


async def check_all(out: Path, browser_path: str | None) -> dict:
    from playwright.async_api import async_playwright

    reports = []
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='explain-motion-browser-') as temporary:
        async with async_playwright() as playwright:
            options = {'headless': True, 'args': ['--disable-dev-shm-usage']}
            resolved_browser = browser_path or os.environ.get('CHROMIUM_PATH')
            if not resolved_browser:
                resolved_browser = (shutil.which('chromium') or shutil.which('chromium-browser')
                                    or shutil.which('google-chrome'))
            if resolved_browser:
                options['executable_path'] = resolved_browser
            if hasattr(os, 'geteuid') and os.geteuid() == 0:
                options['args'].append('--no-sandbox')
            browser = await playwright.chromium.launch(**options)
            try:
                for recipe_id in RECIPES:
                    folder = Path(temporary) / recipe_id
                    config = json.loads((SKILL/'recipes'/f'{recipe_id}.json').read_text(encoding='utf-8'))
                    contract = build(config, folder)
                    errors, external_requests = [], []
                    page = await browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
                    page.on('pageerror', lambda e, dest=errors: dest.append(str(e)))
                    page.on('request', lambda r, dest=external_requests: dest.append(r.url)
                            if r.url.startswith(('https://', 'http://')) else None)
                    try:
                        await page.set_content((folder/'preview.html').read_text(encoding='utf-8'), wait_until='load')
                        await page.wait_for_function('window.ready === true', timeout=15000)
                        last = round(contract['duration']*contract['fps']) - 1
                        frames = {0, last}
                        for event in contract['events']:
                            frames.update((event['start_frame'],
                                           (event['start_frame']+event['end_frame'])//2,
                                           event['end_frame']-1, min(last, event['end_frame'])))
                        for frame in sorted(frames):
                            actual = await page.evaluate('(f) => window.renderFrame(f)', frame)
                            expected = state_at_frame(contract, frame)
                            if actual != expected:
                                raise AssertionError(f'{recipe_id} frame {frame}: {actual!r} != {expected!r}')

                        async def canvas_png(frame):
                            encoded = await page.evaluate('''(f) => {
                                window.renderFrame(f);
                                return document.getElementById('stage').toDataURL('image/png').split(',')[1];
                            }''', frame)
                            return base64.b64decode(encoded)

                        chosen = [(e['start_frame']+e['end_frame'])//2 for e in contract['events']
                                  if e['kind'] in ('decision', 'execute', 'stop')]
                        screenshots = out / recipe_id
                        screenshots.mkdir(exist_ok=True)
                        for frame in chosen:
                            (screenshots/f'frame-{frame:04d}.png').write_bytes(await canvas_png(frame))
                        target = chosen[len(chosen)//2]
                        original = await canvas_png(target)
                        await canvas_png(last)
                        await canvas_png(0)
                        if original != await canvas_png(target):
                            raise AssertionError(f'{recipe_id}: out-of-order seek changed pixels')
                        await page.locator('#seek').evaluate('''el => {
                            el.value='0'; el.dispatchEvent(new Event('input'));
                        }''')
                        await page.locator('#toggle').click()
                        await page.wait_for_timeout(300)
                        if int(await page.locator('#seek').input_value()) <= 0:
                            raise AssertionError(f'{recipe_id}: playback did not advance')
                        await page.locator('#toggle').click()
                        frozen = await page.locator('#seek').input_value()
                        await page.wait_for_timeout(150)
                        if frozen != await page.locator('#seek').input_value():
                            raise AssertionError(f'{recipe_id}: pause did not freeze')
                        await page.locator('#seek').evaluate('''el => {
                            el.value='100'; el.dispatchEvent(new Event('input'));
                        }''')
                        if await page.evaluate('window.semanticState.frame') != 100:
                            raise AssertionError(f'{recipe_id}: slider did not seek')
                        if errors or external_requests:
                            raise AssertionError(f'{recipe_id}: JS errors={errors}, HTTP requests={external_requests}')
                        reports.append({'recipe': recipe_id, 'frames_checked': len(frames),
                                        'semantic_match': True, 'deterministic_seek': True,
                                        'play_pause_seek': True, 'browser_errors': errors,
                                        'external_requests': external_requests,
                                        'screenshots': [str((screenshots/f'frame-{f:04d}.png').relative_to(out)) for f in chosen]})
                    finally:
                        await page.close()
            finally:
                await browser.close()
    return {'ok': True, 'loading_mode': 'self-contained HTML via page.set_content',
            'scope': 'fixture rendering and state parity; NOT an LLM benchmark or audience study',
            'frames_checked': sum(r['frames_checked'] for r in reports), 'recipes': reports}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('build/recipe-browser-checks'))
    parser.add_argument('--browser', help='Chromium executable; otherwise discover CHROMIUM_PATH/PATH/Playwright')
    args = parser.parse_args()
    try:
        report = asyncio.run(check_all(args.out, args.browser))
    except Exception as error:
        report = {'ok': False, 'error': str(error),
                  'hint': 'Install Playwright + Chromium, or set --browser. Inspect the reported recipe/frame.'}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'browser.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
