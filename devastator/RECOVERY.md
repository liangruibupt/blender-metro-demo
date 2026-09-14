# Devastator Recovery / 2026-09-14

## Active Work

- Repository: `/Users/ruiliang/Documents/workspaces/blender-metro-demo`.
- Task directory: `devastator/`.
- Branch: `codex/devastator-clay-checkpoint`.
- Original source/reference checkpoint: `31abf51`.
- The user authorized resuming Blender work and explicitly wants the installed
  Mac application, not another Blender installation or a container.
- Current phase: first combined-form clay model and multi-angle review.

## Current Assets

The builder now executes successfully with the installed Blender 5.2.1 LTS
binary (`9e2066aef7ef`) outside the Codex sandbox. It produces the editable
`.blend`, static GLB and hero/front/rear/detail Cycles stills.

Current paths and usage are in `README.md`. `assets/devastator.json` binds
generated files to their source hashes; `qa/scene-audit.json` records the checks.
Always recheck those hashes before relying on an earlier audit.

`checkpoint-manifest.json` belongs to the original commit, not the current
scripts. The six original reference JPEGs are preserved unchanged.

## Changes Since the Source Checkpoint

- Confirmed the native Mac Blender starts and builds correctly when executed
  outside the Codex sandbox. The earlier code-139 crash was during its native
  Metal device detection, before Python execution. This environment change
  resolves the observed startup failure; it is not a Blender source-level fix.
- Rendered the first draft, then refined the stance, waist connection, chest
  layers, thigh/forearm detail, material separation and sharper armor edges.
- Added rear engine covers, radiator slots, chassis lines and rear sprocket
  detail after inspecting the back view.
- Corrected both feet independently to contact the display-plinth surface.
- Replaced the detached camera action with an independent animated orbit rig.
  Static still rendering no longer removes turntable motion.
- Added saved-scene, asset hash, image dimension, sampled camera-framing and
  GLB reimport checks.

The model-service disconnections discussed earlier were separate Bedrock
response failures. They are not a reason to alter Blender geometry or to
change model/provider configuration while resuming this task.

## Interpretation Limits

This remains a stylized, first-pass gray model, not a detail-for-detail copy of
the Rex Hsu sculpt. Its design uses reference motifs, not measured dimensions.
No vehicle-form models, six-way transformation, collision-free mechanism,
final green/purple paint, MP4 or web inspection page is implemented.

The camera orbit animates only a camera parent. Source assembly empties are
organizational transforms, not a solved articulation or vehicle transformation.

## Next Work

1. Review the actual hero/front/rear/detail images with the user.
2. Refine silhouette, head, armor mass and mechanical density based on feedback.
3. Only after proportion approval, add final paint and/or the independent
   inspection page; do not present transformation as already implemented.
4. Rebuild all model and render outputs together, rerun the audit and inspect
   the images after every geometry change.

Use the repository as the authoritative source. Temporary working files under
`/private/tmp/devastator-v1` are not a separate accepted version. Do not overwrite
newer repository assets with stale staging copies.

Do not alter Metro, Optimus, their scripts or generated assets. No automatic
commit, push or remote deployment is part of this modeling pass.
