# v0.3 directing-path verification

## What was tested

- 70 Python Skill tests passed: existing 50 plus 20 directing tests. New tests cover content-only builds, wrong mechanisms, IDs, finite scores, text budgets, format/audio refusal, duplicate JSON keys, escaping, causality, atomic output reservation and manifest integrity.
- 12 new JavaScript checks passed, including path distance, half-open shots, bounded cameras, arrival gating, ranking after all returns, repeatable seeking and card-overlap checks across 121 reflow samples. Existing motion tests also passed.
- Browser audit: 1,440 default frames + 1,440 maximum-text/first-group frames + 600 last-group/30fps frames = **3,480 frame-state inspections**. No reported text overflow, causal violations or JS exceptions. Play, pause, slider and out-of-order rendering consistency passed for all three configurations.
- A 24.000-second, 1,440-frame, 1920×1080 H.264/yuv420p silent MP4 was actually rendered and fully decoded. It is high-quality lossy CRF 16, not lossless. Export hash and bytes are in verification.json. The MP4 was delivered as a conversation artifact; this commit publishes the reproducible source and served HTML, not the MP4 binary.
- Keyframes and transition frames were visually inspected. An overlap defect in direct wide-card reflow was found and corrected by shrink → relocate → expand. The query is now pinned so the focus camera cannot crop it.

## Reproduce

```bash
python3 -m unittest discover -s technical-animation/tests -v
node technical-animation/tests/test_motion.mjs
node technical-animation/tests/test_editorial.mjs
python3 technical-animation/tests/check_editorial_browser.py --out build/editorial-browser.json --browser /path/to/chromium
python3 technical-animation/scripts/direct.py build technical-animation/directing/partition-search.json --out build/directed-v1
python3 technical-animation/scripts/render.py build/directed-v1 --out build/directed-v1/video.mp4
```

## Evidence boundaries

The current remote shared runtime and exporter files were matched by Git blob hash against the local testing base. Current README and SKILL were fetched and matched exactly before patching, preserving the DeepSeek showcase and browser fallback policy. Reference movie/frame/audio bytes are excluded from the change set. Existing examples and browser rules are not rewritten.

The local environment allowed offline browser frame rendering but blocked an HTTP preview navigation with `ERR_BLOCKED_BY_ADMINISTRATOR`. That connection was stopped; no policy bypass was attempted. **Hosted GitHub Pages playback/deployment was not verified locally.** Relative demo imports and offline generation are checked, which is separate evidence.

No weaker-model A/B benchmark, audio synchronization review, cross-platform pixel-identical guarantee, copyright-license audit of the reference, or audience comprehension study was performed. No claim of outperforming the reference creator is made. Deterministic tests protect animation production, not factual truth or teaching effectiveness.
