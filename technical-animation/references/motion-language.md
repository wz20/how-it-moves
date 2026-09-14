# Motion language / 动作就是解释

## Principle
Every primary motion needs a sentence: **Because X happened, Y moves carrying Z; after arrival, W changes.** If the sentence cannot be written, the motion is decoration. Keep it secondary or delete it.

## Six reusable motion recipes
| Recipe | Technical purpose | Timing / construction | Fail condition |
|---|---|---|---|
| Routed packet | call, response, event, network transfer | reveal edge, packet along fixed Bézier, short trail, arrival response | destination changes before arrival; arrow points backward |
| Context ingestion | observation changes future decision | return token docks, stack gains receipt, face/next action changes | suggests model weights train during inference |
| Branch / reroute | result chooses a different next action | show result; mute rejected route; articulate/select next tool | predetermined success shown before evidence |
| Compare / replace | patch, cache update, state transition | old value visible; explicit delta; replacement; validate | decorative morph without preserving meaning |
| Inspect / reveal | zoom into mechanism internals | hold external object, push into active region, reveal layers, return via same anchor | camera moves without a question or loses object identity |
| Stop / settle | task satisfied, budget reached, error requires human | check condition, stop packet emissions, settle actors, hold ≥1.5s | loop visually continues after declaring completion |

## Motion timing defaults (guidelines, not physics claims)
Anticipation 0.08–0.16s. Main transfer 0.35–0.80s. Arrival response starts at arrival or 1–3 frames after. Short overshoot on props/characters 0.20–0.45s. Informational hold 0.7–1.5s, final takeaway ≥1.5s. 10s demo uses 600 explicit frames at 60fps.

Character: separate head tilt, hand target, eyes, mouth, posture. Hands prepare before launching a command. Eyes track the active entity. Failure is an observation, not necessarily panic; success only follows received evidence. Squash/stretch should be subtle and return to the same anchor.

Packet: normalized time maps monotonically along the path. Never use an overshooting spring for data travel. Label and path stay tied to the same semantic event ID. Trails die quickly; they are not additional messages.

Camera: stage transforms should support attention, not hide unreadable labels. Keep top title and bottom explanatory line stable; allow the mechanism layer to push/pan modestly. Use larger close-ups only with planned safe regions. No random shake. Short impact reaction can emphasize arrival, but not imply causality itself.

## Deterministic authoring contract
`window.videoMeta` contains width/height/fps/duration. `window.renderFrame(n)` draws frame n from a clean state. `window.ready` is true only after assets/fonts are ready. Capture frame n at n/fps; do not record a real-time animation and assume it ran at target FPS. `window.semanticState` supports temporal tests.

Frame functions must have no dependence on prior frames, wall-clock time, Date.now, unseeded randomness, asynchronous generation or unbounded physics integration. Browser playback may use requestAnimationFrame purely to choose which deterministic frame to display. Seed decorative texture once.

Canvas is the included reference backend for fully controlled vector rigs and exact state changes. The same rules apply in SVG/Remotion/GSAP; the Skill's meaning and motion decisions are not tied to Canvas.
