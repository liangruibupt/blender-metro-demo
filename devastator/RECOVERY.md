# Devastator Recovery / 2026-09-14

## User Request

Continue the Blender + GPT-6 Astra creative workflow with Devastator, using the
six supplied Rex Hsu images. Keep the work in a separate `devastator/` directory
inside `blender-metro-demo`. The latest instruction is to check in and commit
the current work and preserve assets, not to finish the model in this checkpoint.

## Exact Checkpoint

- Repository: `/Users/ruiliang/Documents/workspaces/blender-metro-demo`.
- Starting commit: `9970646` (Optimus V3 and both weapons).
- Checkpoint branch: `codex/devastator-clay-checkpoint`.
- Original staging directory: `/private/tmp/devastator-v1/devastator`.
- Two draft Python scripts exist and pass Python AST syntax parsing.
- Six user-supplied JPEGs are preserved under `references/`.
- No Blender model, GLB, still render, movie, browser page or deployment
  integration has been generated or verified for Devastator.

The checkpoint preserves the two scripts as they stood after the interrupted
build. It does not retroactively claim implementation or visual QA success.
Use the repository copy for future work; do not depend on temporary files.

## Two Separate Failures

### Local Blender Startup

Blender 5.2.1 LTS, build `9e2066aef7ef`, exited with code 139. The crash backtrace
enters:

```text
supports_barycentric_whitelist
MTLBackend::metal_is_supported
GPU_backend_type_selection_detect
wm_homefile_read_ex
WM_init
```

The Python backtrace was empty. The failure occurred during startup, before
the model builder ran. A sandbox/Metal-device access issue is a hypothesis,
not a confirmed root cause. A retry with the appropriate execution approval
has not yet been performed.

### Model-Service Interruption

The active thread also encountered repeated model-response failures through
Bedrock's `us-east-2` Responses endpoint, including HTTP 500 responses and
stream failures after HTTP 200. Codex exhausted its five-retry sequence.
This is distinct from Blender's native crash. No credentials or full
conversation/application logs are included in this repository.

## Known Draft Issue

`build_devastator.py` creates camera turntable keyframes and then calls
`camera.animation_data_clear()` before saving. Thus the current source does
not preserve the claimed active camera turntable. Fix this deliberately during
the next implementation pass, for example with separate inspection and animated
cameras. It is documented, not silently changed in this source-preservation commit.

## Next Work

1. Verify Blender can start in the permitted runtime and access its graphics
   backend before diagnosing Python geometry.
2. Run the preserved builder, address any actual Blender API/runtime failures,
   and produce a low-resolution hero render.
3. Inspect the silhouette against `references/rex-hsu-b-0001.jpg`, then inspect
   side/back structure, shoulder clearance, feet, hands and cannon attachment.
4. Correct proportions and intersections. Fix the camera-action issue and
   verify camera framing rather than relying on the hard-coded presets.
5. Generate and visually inspect front, rear, hero and detail renders, the
   editable Blender file and browser GLB as one consistent asset set.
6. Only then add the independent inspection page and the necessary scoped
   build/deployment tests. Do not change Metro or Optimus geometry/assets.

Do not reapply old Optimus patches, regenerate its outputs, or present these
draft scripts as a verified six-vehicle transformation.
