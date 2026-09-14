# Historical v0.1 publication checks

The current v0.2 upgrade results are in [v0.2/README.md](v0.2/README.md). The observations below apply only to the earlier preparation pass.

# Publication preparation checks

This folder records **local checks**, not evidence of a published GitHub repository.

## Executed in this preparation pass

- 9 original Python validation regression tests passed.
- 11 new Python publication-guard tests passed: explicit public consent, safe target names, account identity, noreply email, existing-repository refusal, 404-only availability handling, sensitive/font file and symlink rejection, and demo-copy identity.
- Original JavaScript motion checks passed.
- Existing example contract validation passed.
- Offline HTML rebuilt from source is byte-identical to the approved standalone HTML and `docs/index.html`.
- Scene, motion runtime, Skill and visual/workflow references were compared with the delivered source archive and were not modified.
- 11 actual-browser semantic-boundary checks passed.
- Play advances frames, pause holds the current frame, range-input seeking selects frame 480, and returning to that frame after another seek produces identical Canvas pixels.
- Browser execution reported no JavaScript errors and made no HTTP requests.
- Included MP4 was fully decoded: 600 frames, 10.000 seconds, 1920×1080, 60fps, zero audio streams.

See `verification.json` for observations and command output. Initial publication tests failed because the helper was absent; the helper was then implemented and the 11 tests rerun successfully.

## Limitations

The managed browser blocked file-URL navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`). Verification used the identical HTML file bytes with `page.set_content`, without changing browser policies. It therefore verifies the code and controls, **not a successful file-URL navigation or a hosted Pages visit** in this environment.

The GitHub connection exposed read operations but no repository-creation or push operation; no authenticated local `gh`/git write session was present. The publication helper's protective logic and dry-run are tested locally. Its authenticated create/push/Pages path has **not** been run against the user's account here. A repository URL or Pages URL in the README is the intended publication address, not a claim that it is live.

The original scene was not rerendered into a new full MP4 in this preparation pass. The approved MP4 is preserved byte-for-byte and its full decode was rechecked. The README GIF is a derived low-frame-rate preview of that same MP4.

## Scope of changes

Added repository-facing Chinese/English READMEs, a Pages directory containing the exact approved HTML, a GIF preview, contributor/security/publication documents, and publication/integrity helpers. Redacted one temporary absolute filename from the original ffprobe QA metadata; video data and its SHA-256 did not change. Regenerated the local integrity manifest for that metadata-only edit.
