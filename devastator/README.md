# Devastator / V1 Clay Study Checkpoint

Status: **WIP source checkpoint, not a successfully built or visually verified model.**

This task is independent of `metro/` and `optimus/`. It preserves the first
procedural Blender source and six user-supplied reference images. No existing
study, root deployment entry, dependency, or runtime asset is changed.

## Preserved Contents

- `scripts/build_devastator.py`: draft assembly generation, grayscale materials,
  GLB batching, studio lighting and four proposed render views.
- `scripts/geometry.py`: draft hard-surface geometry helpers.
- `references/`: the six original reference JPEGs, copied without modification.
- `checkpoint-manifest.json`: SHA-256 hashes of the source scripts and reference
  images for checkpoint integrity.
- `RECOVERY.md`: exact progress, failure boundary and next steps.
- `REFERENCE.md`: source attribution and visual interpretation.
- `QA.md`: checks actually performed and remaining gaps.

## Agreed Direction

Build a static combined-form clay study first: broad crawler shoulders, narrow
waist, asymmetric loader and mixer legs, exposed hydraulic connections, crane
backpack and a long four-bore cannon. Review proportions in front, rear,
three-quarter and close-up views before adding final green/purple paint.

The source is an original, unofficial fan interpretation guided by reference
images, not an exact reconstruction of the reference sculpt or a proven physical
transformation mechanism. Separate vehicles and transformation animation are
outside this first checkpoint.

## Not Yet Produced

No `.blend`, `.glb`, rendered PNG, MP4 or web viewer exists for this task.
Empty staging folders are not deliverables. Intended output paths after a
successful build are:

- `assets/devastator.glb`
- `assets/devastator.json`
- `deliverables/devastator-clay.blend`
- `deliverables/devastator-{hero,front,rear,detail}.png`

These are expected outputs only, not links to existing files.

## Resume

Read `RECOVERY.md` before running the draft. The attempted command, from the
repository root, is:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python devastator/scripts/build_devastator.py -- \
  --render --resolution 900 --samples 24 --views hero
```

The previous invocation crashed during Blender's Metal device detection, before
the Python script executed. Resolve that startup issue and the known draft
camera-animation issue before treating the generated scene as a deliverable.

This checkpoint intentionally has no Vite entry and does not change the shared
website. No remote publication is part of this save operation.
