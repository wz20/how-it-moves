# Visual system / 原创漫画技术实验室

## Default preset: comic-lab
Paper `#F5F0E5`, ink `#22252B`, orange `#FF7549` for requests/actions, teal `#3CC7B2` for tool feedback/success, yellow `#FFCF50` for attention/decisions, red `#F06A67` for failure. Keep neutral texture subtle. Alternate themes must declare the same semantic roles; never rely on color alone.

At 1920×1080: main title 60–76 px, concept/actor label 28–44 px, incidental code 24–32 px, outer safe region about 72 px. Avoid shrinking information to fit. Render at the actual target ratio and inspect a 480-px-wide preview. Smaller than 24 px is only appropriate for nonessential metadata.

Original mascot shape: ivory monitor-like head, orange work chassis, teal side parts, simple jointed arms. Face, body, left/right arm, eyelids, hands, props and shadows are separately controlled. No copied creator avatar, no default cat, no creator watermark, no fictional endorsements. Existing user mascots are opt-in, not global assumptions.

Every visual object needs a technical role: terminal executes, packet carries a particular command, receipt is a particular observation, context stack stores observations, tick satisfies an explicit goal. Do not add a brain, server, person and cloud just to fill space.

## Image-generation asset prompts
Use these templates in the actual configured tool. They are not a substitute for tool execution.

### One riggable subject
Create ONE original [subject], isolated transparent background, [view]. [Define silhouette, palette, line weight, materials and expression]. Full visible silhouette with clear limb separation; no labels, no background, no poster layout, no collage, no multiple poses, no extra character. Match the supplied approved character reference without copying any unrelated mascot.

### Matching pose
Using the approved [asset ID/path], preserve identity, camera, scale, outlines and colors. Change only [pose/action]. Keep consistent foot/contact anchor and leave room for [hand prop]. One transparent asset, not a sheet or a storyboard. Do not change clothing, eye shape, proportions or role.

### Technical props
Generate one isolated [tool prop], clear front-facing active region where text will be drawn later. Consistent comic linework and cel shading. No generated text or fake interface claims; reserve a clean display. No unnecessary photorealistic setting.

## Asset ledger
Record `path`, `origin`, `license`, `status`, `used`, `reference`, `anchor`, `parts`, `source_prompt` where applicable. Origin choices include original vector, image generation, supplied reference, licensed third-party. Never list generated assets as original vector or report a rejected attempt as a used asset.

## Covers, when requested
Write a separate composition for each requested ratio. Use the actual video's concept, not a related generic topic. A requested independently generated cover must be independently generated, not cropped from another generated collage. If a downstream text correction is allowed, record that it was typeset/edited. The demo in this package is a video excerpt, not a cover task.
