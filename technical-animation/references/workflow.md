# Workflow: meaning → material → motion → evidence

## Modes
`auto`: Explicit “直接做/自动生成” authorizes design within requested scope. Record assumptions, proceed, stop only on missing essential facts, asset rights, unavailable required tools, or spend/overwrite boundaries. `guided`: pause for script, style, and animatic approval. Never treat this mode as authorization to publish or make purchases.

## Per-project artifacts
| Phase | Input | Output / gate |
|---|---|---|
| Intake | task, refs, source media | brief.md; content constraints; voice/music separately specified |
| Research | precise mechanism | semantic-map.json; primary sources and simplifications |
| Story | mechanism + duration | storyboard.md, project.json causal event intervals |
| Visual | supplied refs | DESIGN.md; asset ledger with origins, license/status, pose IDs |
| Static | hero frames | full-size + phone-size layout review |
| Motion | approved/static composition | 2–4s action test; timing changes logged |
| Render | finite, deterministic timeline | exact frame count, frame hashes, MP4 |
| Review | frames + video | issue list with timecode, severity, resolution, remaining uncertainty |
| Release | checked outputs | clean source + video + offline preview + QA, no fonts/keys |

## Content model
For any subject, identify: entities; initial state; input; observable operation; changed state; output; optional branch/loop; stopping criterion. Also document what is deliberately absent. 10 seconds is a mechanism excerpt, not a complete course.

Example mappings, not universal templates:
- Agent: model decision → tool call → external observation → context update → new decision or stop. The scene's feedback loop is essential; retries need not always succeed.
- RAG: query → candidate documents → retrieved evidence → model answer with evidence. Retrieval is not model training; embeddings are not guaranteed semantic truth.
- TCP: sender → sequence-numbered segment → receiver → ACK; show loss and timeout before retransmit. Do not imply the network acknowledges application processing.
- Cache: lookup → hit or miss; miss must cause backend read; insertion happens after the backend returns. Hit/miss cannot both be active for the same single lookup unless explicitly modelling races.

## Budget
Default one hero style, one mechanism, no paid calls without configured permission, no more than two asset attempts per scene before reporting a problem. Prefer original procedural vector symbols for precise labels, code, wires and rigged faces. Use image generation for art that benefits from it, never for exact technical text. If user requires all-image-generation or a named provider, obey that constraint or report the blockage instead of switching silently.

## Incremental changes
Change only the touched content/asset/motion stage. A technical claim change invalidates affected storyboard and render reviews. A palette change invalidates visual review, not source verification. Duration changes invalidate all timing and QA. Save each approved version; never overwrite user source media.

## Automation boundary
This package is not a hosted service. It has no bundled model credentials, voice cloning, music catalogue, social posting integration, or paid asset subscription. The included renderer handles silent Canvas projects; other renderers can honor the same event contract. No background job promises: execute tools and return real files.
