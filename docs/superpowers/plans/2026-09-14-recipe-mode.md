# Recipe Mode Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans; complete and verify each task.

**Goal:** Make the approved visual method usable without asking the model to implement animation code.
**Architecture:** strict JSON recipe input → deterministic compiler → one event contract → mechanism-specific Canvas scenes → existing offline bundler/render pipeline.
**Tech Stack:** Python 3.10+ standard library, ES modules, Canvas2D, existing Playwright and FFmpeg.
**Spec:** ../specs/2026-09-14-recipe-mode.md

## Global Constraints
Silent 1920×1080 at 30/60fps. Preserve original demo bytes. No remote mutations without supported authenticated tools. No secret/font distribution. No claim of weaker-model benchmark results.

### Task 1: input and temporal compiler
Files: recipes/*.json, scripts/recipe_core.py, tests/test_recipes.py, schemas/recipe.schema.json.
Interface: validate_spec(dict)->list[dict]; compile_recipe(dict)->dict; event effects apply only at end_frame; state_at_frame(project,frame)->dict.
- [x] Write fixture-based validation and timing tests; run them without the compiler to verify a clear missing-feature assertion.
- [x] Implement strict fields, recipe-specific semantic constraints, deterministic frame allocation, reading holds, and explicit error codes/hints.
- [x] Run unit tests on valid/invalid config, booleans, unknown fields, evidence citations, layout bounds, temporal invariants, 30/60fps and edge durations.

### Task 2: controlled player and portable CLI
Files: runtime/recipe-player.mjs, runtime/recipe-state.mjs, scripts/recipe.py, references/recipe-mode.md.
Interfaces: init copies a complete spec; check returns actionable errors; build emits self-contained project and offline preview without editing scene code; --render invokes existing renderer.
- [x] Write integration tests for overwrite protection, invalid-spec refusal, portable bundle and compiler tamper detection.
- [x] Implement original mechanism-specific scenes using existing vector rigs and event-derived state.
- [x] Verify each example at event boundaries, deterministic out-of-order seek, error-free playback and readable static frames.

### Task 3: skill and examples
Files: SKILL.md, README.md, README.en.md, recipes guide, evals, docs/recipes/, original demos unchanged.
- [x] Make default path short: list → choose → init → edit allowed fields → check → build → review.
- [x] Keep advanced path; document unsupported content/ratio/style and retries; supply schema and finished content examples.
- [x] Render three actual silent MP4 examples and offline HTML previews; record real checks separately from human/model evaluations.

### Task 4: release and publication
Files: CHANGELOG.md, release-checks/v0.2.*, manifests, launch helper.
- [x] Full unit/browser/decode/link/security checks; preserve original HTML/MP4 SHA256.
- [x] Package clean source and demos; no cache/env/fonts/credentials.
- [x] Inspect connector and local GitHub capabilities. Create and verify public repository only if real write capability exists; otherwise mark blocked, never fabricate remote success.

## Publication outcome
Local source and examples are complete. Remote creation/push remains BLOCKED: the active connector exposes read-only actions and no authenticated local gh session exists. No remote-success claim is made.
