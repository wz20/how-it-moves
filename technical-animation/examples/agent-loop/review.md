# Release review — v0.1.0

## Passed, with execution evidence
- 9 Python regression tests: valid contract, causality, missing cause, overrun, feedback relation, fractional frames, rejected asset, path traversal, draft block.
- JavaScript motion checks: path endpoints, normalization, interpolation, deterministic seeded randomness and spring settlement.
- 11 actual-browser event-boundary checks: tool idle before call arrival, execution after arrival, failure return before context update, patch only after command arrival, retest result and final stop.
- Offline player play/pause advances frames; scrubber can seek to frame 480.
- Arbitrary-frame PNG repetition matches after seeking to a different frame.
- Full export: 1920×1080, 60/1 fps, 600 decoded frames, 10.000 seconds, one H.264 video stream, zero audio streams.
- Complete FFmpeg decode succeeded. Actual file hash and byte count: agent-loop-10s.qa.json.
- Final keyframe inspection: clear actor identity, explicit TEST/FAIL/PATCH/PASS, matching code change, result direction, stop without new messages. Small metadata is not required to understand the loop.

## Issues fixed during review
1. Final loop label duplicated the title and crossed the outgoing edge → removed.
2. Return-path caption sat on its stroke → moved below the path.
3. A camera push clipped the goal ticket → moved the task inward and shortened the task connector.
4. Return-path caption approached the bottom explanation bar during the push → moved it upward into a safe gap.
5. Initial generated image was an unsuitable flattened storyboard → rejected and not shipped; original vector rigs used instead.
6. Local HTTP navigation was blocked in the environment → removed HTTP serving from the renderer, using offline bundled HTML instead.

## Not established
- No blinded viewer comprehension study or creator-vs-creator comparative test.
- Normal-speed viewing by an independent human reviewer has not been performed. Frame/timing checks and player behavior were exercised; these are not a substitute for audience feedback.
- RAG, TCP, cache and other topics have planning guidance but are not rendered/evaluated examples in this release.
- Cross-model automatic skill invocation and cross-OS pixel parity were not tested. The actual environment is recorded separately.
