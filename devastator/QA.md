# Devastator V1 QA

Runtime: installed Mac Blender 5.2.1 LTS, build `9e2066aef7ef`.
Render target: Cycles, 1400 x 1400, 48 samples, denoised.

## Latest Result

PASS on 2026-09-14: 3,030 source meshes, 68 exported mesh batches, 479,620
reimported triangles, four full-size stills and 25 camera-orbit samples.
Both foot-contact checks passed. Python syntax checks and `git diff --check`
also passed. The output file was opened in a new native Mac Blender instance.

The initial export-extent check exposed an overestimate from rotated object
bounding boxes. The builder now computes the manifest bounds from evaluated
mesh vertices; the GLB reimport matches these actual geometry extents.
The ground plane was enlarged after a visible edge appeared in the front view.

## Automated Scope

`scripts/audit_scene.py` checks:

- SHA-256 equality for the generated Blender file, GLB, stills and three scripts.
- Reopening the saved Blender file, material assignments, finite transforms and
  source mesh count.
- Two foot soles touching the plinth top at Z = -0.315, within 0.002 units.
- A static inspection camera and a separate preserved animated orbit action.
- Full-scene framing with a minimum 2.5% margin at 25 camera-orbit samples.
- Actual camera motion and return to the initial position after a revolution.
- GLB header, declared size, mesh count, assembly labels and grayscale colors.
- Absence of reference-image textures and transformation animation in GLB.
- PNG format and dimensions for all four stills.
- GLB reimport into a separate Blender scene, matching triangle count and model
  extents within 0.025 units.

Results and the source/asset hashes checked are stored in `qa/scene-audit.json`.
The audit fails on missing/stale files; it does not treat a partial render run
as a complete verified deliverable.

## Visual Review

The development hero render was inspected before refinement. Full-size hero,
front, rear and detail views are reviewed for framing, readable construction
elements and obvious disconnected parts. This review does not establish
detail-for-detail similarity to the source artwork.

## Remaining Limits

- No exhaustive mesh-intersection, watertightness or physical-mechanism test.
- No exact-source dimensional reconstruction.
- The camera orbit is sampled rather than continuously proven.
- No independently modeled vehicle configurations or transformation.
- No final color/texture work.
- No browser/mobile or website deployment tests in this Blender-only pass.

Metro and Optimus are unchanged. Their existing tests are not evidence of
Devastator geometry correctness.
