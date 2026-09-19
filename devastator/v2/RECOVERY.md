# Devastator V2 Recovery / 2026-09-15

## Official MCP Setup

The user requested the official Blender Lab MCP for subsequent development
and installed its 1.0.3 add-on manually. The matching server was then built
from official commit `2cea8d566dde07fbac28a61d698909d69724e853` and installed
in the explicitly requested `/Users/ruiliang/Documents/workspaces/venv`.
Do not create a replacement environment or use the third-party PyPI project.

Codex global server `blender-official` is enabled, using stdio and loopback
`127.0.0.1:9876`. `MCP_SETUP.md` records the setup and security limitations.
The real MCP test passed: 26 tools, 610,432 triangles, 432 frames, correct
scene-state restoration and unchanged source hashes. It also generated
`qa/official-mcp-preview.png` using the official rendering tool.

The validation copy remains open in a separate Blender instance. Native
Codex tools may require a new conversation/app restart to be discovered.
The protocol test itself already completed using the official MCP SDK.
No automatic commit or push is authorized for this setup.

## Active Assembly Iteration

The user now requests an assembly animation shorter than 20 seconds, at the
existing turntable's detail level, without creating another version folder.
Current target: 18 seconds, 432 frames, 1080p24, Eevee 64 samples.
This request supersedes the older static-only scope for this added animation.
The accepted static source and old 360 video remain unchanged.

Work is in `/private/tmp/devastator-v2`, to be synchronized into the existing
repository `devastator/v2/` after verification. `ASSEMBLY.md` describes scope,
timeline and commands. New scripts are `assembly_motion.py`, `build_assembly.py`,
`audit_assembly.py`, `render_assembly.py` and `encode_assembly.py`.

Build succeeded with 81 evaluated meshes, all 610,432 original triangles and
14 motion controls. The 432-frame audit and visual keyframe gate passed.
The initial wide camera was outside the old cyclorama; the animation-only
cyclorama was expanded by 25 units, and dolly-in was delayed to seconds 9-16
to keep the elevated head in frame. Original scene geometry is unchanged.
Full 1080p/64-sample rendering completed all 432 frames in about 27 minutes.
Current production frames: `work/assembly-a646980aad4b/`.
An additional independent `audit_assembly_motion.py` passes 1,728 pair/frame
checks across the same four selected non-joint pairs. Its report is
`qa/assembly-motion-clearance.json`. It does not alter the rendering inputs.
`assembly-render.json` has `complete: true`; `assembly-video-audit.json`
passes for the 18-second 1080p24 H.264 MP4. All 432 frames decode, and the
18-sample decoded contact sheet was visually inspected. Reopened-scene and
motion-clearance checks also pass. Final native scene and video are
`deliverables/devastator-v2-assembly.blend` and
`deliverables/devastator-v2-assembly.mp4`.

The user added a reference MP4 under `devastator/references/`; preserve it.
The prior V2 delivery was committed as `24f4fdd`; the user subsequently committed
the reference video as `a690bea`. This iteration has not been authorized for
an automatic commit or push.

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
