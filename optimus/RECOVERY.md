# Recovery And Active Work

Updated 2026-09-13. Read this short file first after an input-length failure.
Do not reload entire previous conversations or all reference screenshots.

## Recovered State

- Main checkout: `/Users/ruiliang/Documents/workspaces/blender-metro-demo`.
- Branch: `codex/optimus-prime-showcase`; committed V2: `fd53385`.
- V3 staging: `/private/tmp/optimus-reference-v3`.
- V3 body, maps, GLB, Blender file, stills and 80-second MP4 were complete in
  staging but had NOT been synchronized to the checkout when the turn failed.
- Prior V3 checks: 46 tests, 45 collision pairs at 321 states, build, video
  decode and static deployment checks passed. These checks do not validate
  the weapon changes below.

## Current Request

During the robot's pre-transformation 360-degree presentation, show both a
gun and an axe, following the user's existing reference screenshots.
The gun is a dark long-barrel ion rifle. The axe is a short wrist-style
orange/gold energon axe with curved hooked blades, not a long polearm.

## Completed Checkpoint

`scripts/weapons.py` creates two persistent accessories attached through
sliding carriers and visible telescoping guides to the forearms. They start
in the hands, slide outward before folding, and remain present in truck form.
No hiding, mesh replacement or geometry scaling is used.

- The reference-guided V3 body and both weapons are implemented.
- GLB, rig JSON, Blender animation, two Cycles stills and the 80-second MP4
  are regenerated. No geometry is hidden or swapped during transformation.
- 48 tests pass. The collision audit passes 67 pairs at 321 states, with
  grounding checks and matching Blender/browser poses at 17 states.
- The half-turn direction is explicitly specified; do not replace it with
  endpoint-only quaternion interpolation, which selects opposite arcs in
  Blender and JavaScript at exactly pi.
- Desktop/mobile full-film framing and persistent weapon visibility pass.
- MP4 full decode, static build and deployment-asset integrity checks pass.
- See `QA.md` for limitations. These are selected surface checks, not a
  physical transformation proof. Storage mechanisms are original simplifications.
- Synced to the main checkout. Main-checkout tests (48/48), build, HTTP asset
  integrity, video range requests and browser smoke checks all pass.
- Preview: `http://127.0.0.1:5193/optimus/`.

For future syncs, change only `optimus/` and relevant version labels.
Do not touch Metro or apply the archived V2 WIP patch. Rerun tests, build and
local HTTP validation after changing the assets.
The Git baseline before this checkpoint is `fd53385`. This checkpoint is for
local version control only; no remote push is performed.

## Prior Conversation

Task `01a09ae2-89b0-7570-9d7c-c95da992e160` failed with the model-service error
`Input is too long` immediately after the weapon request. The web app did not
produce that error. Nothing indicates loss of the already written V3 files.
The service's effective input limit is not established by the available logs.
This checkpoint does not change Codex configuration or the model service.
