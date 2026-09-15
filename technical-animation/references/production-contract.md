# Topic scene contract v1 · v0.8 production rules

Use `create.py init`; fill a single `story.json`. No arbitrary JavaScript, SVG markup or external URLs are executable input. The same contract drives SVG, HTML and MP4. There is no fixed Agent/RAG/cache layout or topic-to-asset lookup.

Official animation export now also requires the [typed mechanism contract](mechanism-contract.md). The keyframe fields below are rendering primitives, not evidence of an explained mechanism. A low-level geometry check passing never certifies production.

## Fields

| Field | Meaning |
|---|---|
| `presentation` | `animated` or `static`; general parameter-driven `interactive` is rejected until a tested domain adapter exists |
| `mechanism` | typed discrete events for animation; entity relations for static SVG |
| `profile`, `course` | `general` or `academic`; academic requires a course evidence ledger |
| `schema_version` | integer `1` |
| `project_id` | generated project identity; do not recycle it to disguise old assets |
| `topic`, `style` | teaching topic and concrete art direction; no unfinished placeholders |
| `formats` | nonempty subset of `html`, `video`, `svg` |
| `width`, `height` | even integers 320–4096; recompose when aspect changes |
| `fps`, `duration` | 30/60; 1–180 seconds with integer frame count |
| `poster_frame` | reviewed frame for the standalone static SVG |
| `concept` | `goal`, three `candidates` (`world/reason/risk`), `selected` index, `entities`, `avoid` |
| `history` | records from prior workspace deliveries; `project_id/world/asset_hashes` |
| `assets` | real generated foreground/background files plus provenance |
| `shots` | continuous ordered frame ranges, operations and visible consequences |
| `layers` | separate image/text/path objects with persistent IDs and optional keyframes |
| `reuse_consent` | optional, specific user authorization for cross-project asset IDs or world reuse |

Each entity: `id/meaning/subject/operation/consequence/invariant`. One entity ID binds one image file; use additional mapped IDs for independently generated state layers. Coherent states still depict the same object. Every asset has `id`, local `path`, `sha256`, `role` (`subject/prop/background`), and `generation` containing actual `project_id/tool/model/run_reference/prompt`. Paths must stay inside the project. PNG/JPEG/WebP >=256px per side, <=40M pixels and <=30MB per file are supported. Empty/sparse/solid placeholders and hash mismatches are rejected. Resolution floors are not a guarantee of sharp close-ups.

Each shot: `id`, inclusive `start`, exclusive `end`, short `caption` (<=42 chars), `action`, `change`, `asset_ids`, optional `critical_frames`. Full timeline coverage is required. Operation verbs are `extract/store/retrieve/inspect/select/assemble/route/split/merge/compare/update/invalidate/evict/verify/repair/dispatch/return/acknowledge/transform/resolve`. The field labels do not prove technical correctness; inspect the actual effect.

## Layers and motion

An image layer uses `asset` and `slot`, optional visibility `start/end`, `scale`, `rotate`, `opacity`, `keys`. Layer IDs must be unique and cannot use player control IDs. Named slots: `left/center/right/hero/top/bottom/top-left/top-right/bottom-left/bottom-right/off-left/off-right`. They are anchors, **not subject choices**.

```json
{
  "id": "memory-token-art",
  "asset": "memory-token",
  "slot": "left",
  "start": 0,
  "end": 600,
  "keys": [
    {"frame": 0, "slot": "left"},
    {"frame": 180, "slot": "center", "scale": 0.9},
    {"frame": 420, "slot": "right", "scale": 1.0}
  ]
}
```

This is a syntax illustration, **not a completed memory mechanism or generation receipt**. Choose timings and visible states from the storyboard. Coordinates, bounds and smoothstep interpolation are supplied by the renderer; keys must be ordered integer frames. Translate/rotate/scale artwork only when the operation calls for it. Image aspect ratio is preserved. Use generated parts/state variants for contact, opening, insertion and consequence, not only whole-image movement. A final `resolve` hold of at most two seconds is allowed; SVG-only scenes need no movement tracks.

Text layer: `type:"text"`, `text` <=42 chars, `slot` (including `title/subtitle/caption`), `size` 18–84, optional hex `color`. Text remains editable. Path layer: `type:"path"`, 2–24 normalized `[x,y]` points, optional hex `color` and `stroke_width` 1–12. Paths support scheduled visibility and opacity, not silently ignored geometric tracks. No raw path strings or arbitrary markup are accepted.

## Quality and evidence

The validator checks actual image alpha bounds and transformed screen footprint at shot start/quarter/middle/three-quarter/end, explicit critical frames and poster frame. Foreground union must cover >=18%; approximate text footprint <=20%. Repeated identical keyframes or pure fades do not count as a subject operation. These are **heuristics**, not an aesthetic oracle: occlusion, paragraphs embedded inside an image, unrelated large artwork and meaningless movement require visual rejection.

`review-v1/review.json` includes source/exporter/asset fingerprint, captured PNG hashes, requested formats and per-shot findings. The supplied command sets all verdicts to `pending`. A human or vision-capable agent must inspect images and animated transitions, then identify reviewer/method and record concrete findings for `asset_quality/not_slides/readability/mechanism` and (HTML/video) `causal_motion`. There is deliberately no automatic approve command.

A generated-asset receipt is an auditable claim, not a provider signature; matching a project ID cannot prevent forgery. A hostile host can write another renderer. Do not assert that code alone guarantees beauty, truthful provenance, cross-model success or audience comprehension. When checks fail, repair the art/scene, recapture and re-review; never rename drafts or bypass the export route.

Final HTML omits generation prompts, private run references and workspace history from its player payload. SVG keeps only minimal project/format metadata. Keep detailed origins in the private editable project unless the user explicitly wants them published.

## v0.7 optional performance extensions

Top-level `performance` and `soundtrack` are now accepted; other unknown top-level fields still fail. `performance` has version/rigs/actions/cues. It is compiled, not executable JSON. Do not manually provide compiled_actions, compiled_rigs or performance_initial. See [the full contract](performance-contract.md).

Assets may add `entity` to link several distinct registered state images to one concept entity. Image layers accept an optional normalized `box`, normalized `pivot`, verified `image_size`, and discrete `asset_keys`; numeric keyframes may use x/y and `ease: linear|smooth`. New ordinary producers should let the operation compiler emit these details rather than write them.

Bound performance layers reject conflicting hand-authored keys and visibility ranges; state images must have equal artboard dimensions. Transform limits, freshness, image-area and text/readability checks remain enforced. Source validation does not prove that drawings are registered semantically—visual inspection remains necessary.

## v0.8 production evidence

Layers may declare `purpose`: subject, mechanism, label, narration, decoration or camera. Explain-only text can be hidden without hiding necessary labels; mechanism-only review also hides decoration and nonessential camera layers. Do not mislabel decoration as mechanism to pass the review.

`create.py review` generates actual full/reduced/ablation captures, event observations and pending reviews. Official `export` requires approved technical/event/visual records, unchanged evidence, real visible state witnesses and the same source fingerprint. It exports reviewed media, not an inferred instructor endorsement. Academic customer handoff additionally uses [separate subject sign-off](academic-delivery.md).
