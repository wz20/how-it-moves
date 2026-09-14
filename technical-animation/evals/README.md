# Evaluation protocol — do not confuse compiler tests with model capability

## Current evidence
Deterministic fixture compilation, invalid-input rejection, browser event-boundary agreement, seek determinism, playback controls, and rendered media decoding are executable tests.

**No weaker-model benchmark, audience-comprehension study, or creator-comparison score has been run.** `model-results.json` intentionally records `not_run` rather than invented accuracy numbers. Fixture JSON was authored during development, not collected from independent weaker agents.

## How to test a host model
Run the same frozen prompts on each target model. Record exact provider/model version, date, host tools, SKILL digest, sampling settings, latency, cost, all output JSON files, and complete command/error logs. At least five repetitions per prompt are recommended; predeclare the number, do not discard failed runs.

Compare v0.1 freeform against v0.2 recipe mode using the same topic and time budget. Do not let the evaluator secretly repair outputs. Permit at most two input-repair rounds in v0.2.

1. Feedback: show test failure, different repair code, retest and stop. Use the bundled example content. Verify both temporal order and actual narrated truth.
2. RAG: use a new toy question and three supplied snippets, one irrelevant. The answer must cite selected snippets only. A human must judge whether the answer is supported.
3. Cache: same key, initial miss, application reads DB and populates cache, next hit. The DB count must remain one.
4. Unsupported topic: explain TCP congestion control. Correct result is explaining that the current recipes do not cover it and offering advanced authoring, not relabeling an Agent loop.
5. Pressure: demand a 3-second, 9:16, voiced recipe. Correct result is an explicit capability mismatch, not silent stretching/audio removal.
6. Repair pressure: supply a long title, duplicate document IDs, nonexistent citation, and a pre-existing approved output folder. Observe targeted errors, no bypass, no overwrite.

## Separate scores
- first-pass valid configuration rate
- valid output after at most two repairs
- number of model-written scene-code lines (recipe path should be zero)
- factual correctness and mechanism matching (independent reviewers)
- browser errors, deterministic seeks, layout/legibility issues
- blinded visual preference / comprehension (real participants, not the producing agent)
- latency / cost / unsupported-case refusal rate

Publishing a claim such as "all small models produce excellent animation" requires appropriate evidence. This project makes the narrower engineering claim that supported recipes remove model responsibility for coordinates, easing, layout code and event scheduling.
