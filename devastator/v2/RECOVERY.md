# Devastator V2 Recovery / 2026-09-15

## User Direction

Continue refining V2 from the supplied 12.01-second video, produce a complete
360-degree presentation, retain only optimized V2 production assets, and
provide reference-free image prompts with instruction-writing guidance.

Repository: `/Users/ruiliang/Documents/workspaces/blender-metro-demo`.
Current model: `devastator/v2/`.
Staging work: `/private/tmp/devastator-v2`.
Reference clip:
`/Users/ruiliang/Downloads/mac_sync/2-00x-3840x2160-alq-8-1.mp4`.
Reference inspection frames: `/private/tmp/devastator-reference-video/`.

No automatic commit, push, paint pass or website deployment is requested.
Do not alter Metro, Optimus, original references or git history.

## Resumed Checkpoint

The previous session's geometry refinement, four stills and all 288 turntable
PNGs survived its input-length failure. Rendering finished at approximately
10:18 local time. Do not restart that render merely because the session failed.

This continuation encoded `deliverables/devastator-v2-360.mp4`, decoded and
checked all 288 frames, opened all four stills and the decoded video's
12-view contact sheet, and reran the complete native scene audit.
Both machine-readable audits pass. See `QA.md` for exact scope and limitations.

Current geometry: 3,791 source meshes, 68 evaluated GLB meshes and 610,432
triangles. Older 3,020/486,732 statistics describe an earlier checkpoint.

`PROMPTS.md` now defaults to the reference video's bright clay/cool-gray
presentation, with a separate dark-studio replacement for current V2. It
includes full/compact image prompts, local corrections, editable-3D and
video instructions, and a table explaining useful descriptive language.
Numerical camera choices are recommendations, not recovered reference data.

## Source Map

- `scripts/build_devastator.py`: entry point, materials and base.
- `scripts/upper_body.py`: chest, head, shoulders, arms, cannon and crane.
- `scripts/lower_body.py`: pelvis, endpoint-defined legs and integrated feet.
- `scripts/refinement.py`: video-guided helmet, hand armor, cab side details,
  drivetrain, shell segmentation, telescopic crane and rubble additions.
- `scripts/parts.py`, `scripts/geometry.py`: mesh construction helpers.
- `scripts/scene_io.py`: evaluated GLB, actual bounds, cameras, studio,
  still rendering, resource manifest and hashes.
- `scripts/render_turntable.py`: signature-bound resumable frame rendering.
- `scripts/encode_turntable.py`: encoding and every-frame decoding checks.
- `scripts/audit_scene.py`: saved-scene, GLB, contact and all-orbit checks.

## Reproduction Constraints

Use the already installed Mac Blender 5.2.1 LTS at
`/Applications/Blender.app/Contents/MacOS/Blender`, outside the Codex sandbox
with approval. Do not install another Blender or change model/provider
configuration to address an unrelated session error.

Keep world-space sole targets Z=0 and Z=0.2. The sculpture is rigid; only the
independent camera orbit moves. Hero azimuth is approximately 40.7 degrees.
The studio uses a floor-tangent quarter-circle sweep.

Video: 1920 x 1080, 24 fps, 12 seconds, Eevee 64 samples. Encode frames 1-288;
frame 289 closes the orbit without being duplicated in the video. Stills:
1600 x 1200, Cycles 64 samples with denoising. See `README.md` for commands.

The four selected surface checks are not an exhaustive collision test.
The BVH studio-ray tolerance is 0.00001 units to avoid misses on shared
triangle edges; studio topology is checked independently.

Render intermediates, old previews, `.blend1` and Python caches are excluded
from delivery. Reopen and verify the repository copy before relying on any
staging copy in a later session.

## Visual Limits

Do not treat passing audit checks or increased object counts as visual
acceptance. Current V2 still simplifies the reference's pose, head and hands,
vehicle panels, mechanical transitions, crane placement and rubble contour.
Further artistic refinement should be driven by user review of the actual
stills and video. No physical transformation or independent vehicle mode is
implemented.
