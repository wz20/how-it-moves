# HTML / MP4 / SVG output selection

The default is **no assumed format**. Capture the user's choice once. CLI values: `html`, `video` (alias `mp4`), `svg`; any nonempty subset is supported. Unknown or duplicate formats are rejected.

| Output | Deliverable | Specific behavior |
|---|---|---|
| HTML | `animation.html` | Inline artwork and SVG, deterministic play/pause/seeking; no external image/font/CDN dependencies |
| Video | `video.mp4` | The same SVG scene and timebase captured at 30/60fps; H.264/yuv420p; silent by default or explicit local audio; ffprobe and full decode checks |
| SVG image | `illustration.svg` | Static reviewed moment, separate image/text/path/group layers; full viewBox and accessible title/description |

The final folder also contains `delivery.json` and `asset-history-entry.json`, not unrequested media. Output is first built in an isolated temporary folder and published only after success; existing destination folders are refused. A failed MP4 does not silently deliver the other requested outputs as a completed multi-format job.

## Production modes and evidence

For v0.8, animated HTML/MP4 require a typed discrete mechanism plus executable operations. A static SVG-only request uses an explicit relation contract and no motion quota. An SVG snapshot requested alongside animation shares its reviewed event state. Parameter-driven teaching HTML is not implemented by adding playback controls; request a tested domain adapter rather than mislabelling a player.

All official exports require three separate quality verdicts and per-event/ablation evidence. Sparse review and dense export use the same software/full-raster browser configuration so tile-cache antialiasing does not invalidate approved pixels. Cross-browser/font/platform equality is not guaranteed; review anew in the target environment.

## Start

```bash
# From repository root; use absolute Skill path when installed elsewhere.
python3 technical-animation/scripts/create.py init \
  --topic "Explain the mechanism" --formats html svg --out work/my-topic
```

Fill typed events and run `create.py plan` / `create.py asset-plan` before generating artwork, as described in [the contract](production-contract.md). Then design topic-specific concepts and generate the required real assets:

```bash
python3 technical-animation/scripts/create.py prompts work/my-topic --out work/my-topic/generation-briefs.md
# This produces prompts, not images. The host must actually invoke image generation.
python3 technical-animation/scripts/create.py check work/my-topic
python3 technical-animation/scripts/create.py review work/my-topic --folder review-v1
# Inspect the actual images AND animation in review-v1; edit review.json with specific findings.
python3 technical-animation/scripts/create.py export work/my-topic \
  --formats html svg --review work/my-topic/review-v1/review.json --out build/my-topic-v1
```

Set `--formats video` for MP4 only, or `--formats html video svg` for all three. Formats must have been declared and reviewed. For another SVG moment, `--svg-frame 120` requires that exact frame in the review evidence; otherwise set `poster_frame`, recapture and review first. Defaults do not substitute a blank first frame for a good static composition.

## SVG honesty

AI-generated PNG/JPEG/WebP artwork remains raster. Each asset is embedded as an individual `<image>` in an SVG `<g>`; text and paths remain real editable vector elements. Resizing preserves image aspect ratio. The SVG metadata labels this **hybrid-svg / embedded-raster**, not pure-vector. No whole-frame screenshot is used as the sole SVG image. Image tools can edit vectors/text separately, but cannot magically edit a raster object's internal strokes.

For a pure-vector request, explain the conflict with raster image generation and agree on a different, manually vector-authored production path. Do not auto-trace without review or silently replace quality illustration with icons. A static illustration uses the same art standards but does not need an animation movement review.

## Dependencies and review

Python 3.10+ and Pillow for model validation and final HTML/SVG serialization. The supplied **review screenshot** command uses Playwright/Chromium for all formats; HTML/SVG serialization itself does not need FFmpeg. MP4 additionally requires FFmpeg/ffprobe. No font files are embedded or distributed; use licensed system fonts with the required glyphs.

```bash
python -m pip install -r technical-animation/requirements.txt
python -m playwright install chromium
# Install ffmpeg through the OS package manager for video only.
```

The scene size can be any even dimensions from 320 to 4096, with 30/60fps and 1–180 seconds. This is a transport limit, not a claim that every composition or length is good. Video is silent by default. v0.7 supports explicit local soundtrack tracks as described in performance-contract.md; real audio is verified and reviewed, not replaced with an empty stream. Audio probing needs ffprobe even for an HTML-only audiovisual project.

`review` produces `pending`. Final export checks actual asset files, source fingerprint and every required evidence image; changed content/art/exporter invalidates approval. MP4 compares sampled rendered pixels to those reviewed in the same environment. Switching browser/font environments requires fresh review, not bypassing the gate.

## v0.7 performance and sound

`performance` compiles ports, hinges, occlusion and discrete state changes into the same scene used by all formats. HTML embeds real local audio, and MP4 mixes explicit trim/start/gain tracks; SVG remains static and silent. Two-track audio is not automatic TTS/ASR/beat matching. See [performance contract](performance-contract.md).

Review fingerprints include the operation compiler and soundtrack sources. A rig, cue, state image or audio change requires fresh review. The semantic runtime is compatible with old manual-layer scenes; static-only scenes do not need a performance plan.

## Client handoff is separate

`export` produces a reviewed artifact. For academic work, verify the source ledger before export and obtain instructor/subject approval of those exact media before `handoff`. Approval cannot be inferred from ffprobe, screenshot hashes or an autonomous visual reviewer. Client uploads and public GitHub publication are separate, default-denied permissions.
