# Topic-first art direction / 每个主题有自己的视觉世界

## Event planning comes before art

First run `create.py plan` on typed events and `create.py asset-plan` on the operations, even with no images or rigs. Use those generated requirements to choose a world and split only the parts that really perform an event. Do not create a full illustration first and try to salvage motion later. See [mechanism contract](mechanism-contract.md). Asset-plan entries describe current adapter capabilities, not compulsory cabinets or characters.

## Reuse the visual language, not the same nouns

A style bible can preserve contour weight, palette, camera, material and light. Motion primitives can preserve timing and collision handling. Neither authorizes silently copying the last robot, terminal, binder or drawer. There is deliberately **no keyword-to-prop catalog** in the new initializer.

The host creates three distinct concepts from the actual mechanism. `create.py prompts` packages that reasoning into generation briefs; it does not invent ideas, call an image provider or claim images exist.

For each candidate record:
- `world`: a distinct visual setting or organizing metaphor, not a color variant.
- `reason`: which operation this world makes visible and why this is better than literal boxes.
- `risk`: how the metaphor could distort the real mechanism; keep that boundary visible.

Select only after mapping technical nouns, operations and consequences. A visual reviewer rejects superficial candidate variation even if string uniqueness passes.

## Association ladder

Start with the topic's verbs: collecting, comparing, updating, routing, waiting, verifying, preserving, discarding. Ask what physical or spatial action makes the verb observable, then choose a coherent world. Examples of design questions, **not ready-made assets or a fixed selection list**:

- Memory: how can a persistent preference and a one-time exception remain distinguishable? A travel journal, layered keepsake or another newly devised object may help; a generic filing cabinet is not mandatory.
- Message delivery: how can ownership, acknowledgement and retries remain visible? Design a relay or transfer system without implying literal instantaneous duplication.
- Resource reclamation: how can reachability, retention and reclamation appear as distinct operations, without implying objects are deleted merely because they are old?
- Retrieval: how can a query pick evidence while preserving originals? Choose an original setting instead of always drawing the previous archive machine.

A familiar robot can still be appropriate for a robotics topic or an explicitly requested brand character. The prohibition is **unexamined default reuse**, not a blacklist of nouns.

## Per-entity brief

`concept.entities` maps an ID to `meaning`, `subject`, `operation`, `consequence`, `invariant`. For one entity, generate an independent image/layer with a complete silhouette, enough resolution for its actual shot size, consistent perspective and a usable contact surface/pivot. Generate additional states only when needed. Assemble all pieces into the selected world, rather than an unrelated sticker collage.

Generation prompt includes the current topic, selected world, shared art direction, entity role, physical action, visible result and metaphor boundary. No paragraphs, watermarks, full-page slide layouts, arrows or labels inside the generated artwork. Draw exact text/code/numbers separately.

**Actual generation is an explicit host action.** Use the installed native image tool or authorized provider. If the actual model is undisclosed, record that honestly; do not make up a model name, run ID or API response. Never use a provider logo or API-shaped JSON as proof of generation.

## Freshness and provenance

A new `project_id` is allocated on initialization. Every asset has file SHA256 and a real generation record tied to its producing project. Fresh is the default. The validator rejects assets from another project or an already-used file hash, even when the file is renamed. Only a scoped `reuse_consent` with specific IDs and actual user request reference permits reuse.

The host reads prior `asset-history-entry.json` records from the relevant workspace and includes them in `history`. The exporter writes the next record but does not scan unrelated private directories. It rejects a repeated selected `world` unless the user explicitly requests it. The history check cannot discover files it was not given or authenticate a self-written receipt.

**In-project reuse is required for identity:** the same subject should persist across shots and state variants. The fix is not generating random new art every second.

## Weak-agent workflow

Do not ask a weaker agent to invent coordinates, easing and a complete renderer. Ask it to fill semantic fields, call the image tool, inspect the returned files, assign named slots, and specify a small sequence of operation keyframes. The renderer interpolates and shares those states across formats. Use short captions and few simultaneous subjects; decline production rather than inventing generated assets.

A text-only agent cannot sign off visual quality. Use a vision-capable review step or the user. Three long prompts and a passing schema are not an art review.

## v0.7: design art that can perform

Before final generation, identify the necessary contact surface, hinge, opening, foreground edge and visible states for each selected operation. Supply body/state/gate/front layers on a shared artboard, including transparent margins; these are parts of the newly devised subject, not a preselected machine kit. Inspect them against [the rig contract](performance-contract.md).

The compiler replaces repeated coordinate/choreography work. It does not generate or segment images, infer a new visual metaphor, identify a hinge from pixels, or prove an analogy accurate. A vision-capable agent or user must locate a small set of real anchors. Reuse operation recipes, not previously generated topic art.
