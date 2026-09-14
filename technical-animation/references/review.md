# Review / 发片前证据

## Blocking checks
Technical falsehood; result before cause; missing return path for a loop explainer; unreadable key text; lost entity identity; wrong user mascot; missing essential source; undeclared synthetic demonstration; unexpected audio; unavailable required asset; broken decode; wrong duration; wrong frame count. Do not average these away with visual polish.

## Review rubric (human judgment, not a fake automated score)
- Mechanism clarity 0–5: can the viewer identify input, operation, feedback, next action and stop?
- Motion semantics 0–5: motion carries the technical explanation rather than decorating captions.
- Continuity 0–5: object identity, spatial direction and contact anchors persist.
- Visual craft 0–5: hierarchy, consistent shapes, negative space, expression, readable technical labels.
- Timing 0–5: enough holds; one focus at a time; arrival responses synchronized.

Do not claim to beat a particular creator without an actual comparative viewing protocol. A 10s excerpt proves only that this excerpt renders and follows its contract, not that the skill has been evaluated across all topics and host models.

## Automated
1. `python scripts/validate.py <project>` checks event ranges/causality and asset status.
2. `python -m unittest discover -s tests` and `node tests/test_motion.mjs` check core regressions.
3. Snapshot first, last, event boundaries and representative states, including arrival−1 and arrival+1 frames.
4. Re-seek a sampled frame; its PNG hash must match regardless of previous frame.
5. Export and use ffprobe for dimensions, FPS, frames, duration and stream layout; full FFmpeg decode.
6. Keep QA JSON, environment versions and sample hashes. Test archives; never bundle fonts, secrets, caches or node_modules.

## Visual
View full-size and mobile-size keyframes; inspect both sides of every transition. When a video player is available, watch at normal speed, silent. If only sampled images/automated checks were inspected, explicitly record normal-speed human playback as unverified. A contact sheet does not prove animation quality.

## Feedback entry
`time / object / severity / observed issue / change / evidence / resolved-or-open`.
Avoid feedback like “more premium” without tying it to a visible fault. Re-render affected scenes and recheck transitions. Preserve the source and previously approved versions.
