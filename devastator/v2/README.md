# Devastator V2 / Video-Guided Refinement

## Official MCP

The official Blender Lab MCP is configured as `blender-official` in Codex.
Use it for live scene edits, structured inspection and verification. A real
MCP protocol test against a disposable V2 copy passed all 432 frame checks and
produced a full-resolution render without changing the accepted assets.
See `MCP_SETUP.md` for installation details, limitations and reproduction.

## Assembly Animation

V2 now also has an 18-second modular assembly sequence in this same directory.
It retains all 610,432 triangles and the turntable's 1080p24 Eevee 64-sample
quality, adding module docking, elbow folding and rear-crane folding.
The original sculpture and 12-second 360-degree turntable are unchanged.

- `deliverables/devastator-v2-assembly.blend`: animated native scene.
- `deliverables/devastator-v2-assembly.mp4`: 18-second H.264 presentation.
- `assets/devastator-v2-assembly.json`: independent animation provenance.
- `ASSEMBLY.md`: choreography, build commands and verification scope.

This is a staged assembly of the existing robot modules, not six independently
modeled vehicles or a mechanically solved vehicle-to-robot transformation.

## Sculpture

V2 is the current retained model inside `devastator/v2/`. Obsolete V1 generated
assets, build scripts and checkpoint documents are removed from the working
tree at the user's request; git history is unchanged. Reference originals,
Metro and Optimus assets are retained.

## Changes in Form

- The video-guided pass rebuilds the swept helmet, separated facial components,
  dorsal hand armor and knuckle mechanisms.
- New chest return walls, shoulder service decks and forearm side mechanisms
  improve side-view structure rather than only front-facing detail.
- Vehicle legs gain lateral shells, brake reservoirs and steering cylinders.
  The cab has separate doors, side glass, handles, access steps and front wheels.
- The crane gains telescopic sleeves, guide rails, wound winch cable, an open
  hook, a lifting cylinder and rear radiator banks.
- Additional fractured concrete and bent reinforcement refine the base.

- Sloped crawler/counterweight assemblies wrap the shoulder joints. Small
  complete construction vehicles are no longer placed on top of the shoulders.
- The chest is rebuilt as a deep, folded bridge with separate outer plates,
  internal rails, diagonal struts and a recessed abdominal transmission.
- The upper body rotates independently from the pelvis. The raised forearm is
  heavier, with a changing cross-section, overlapping wrist armor and exposed
  accumulators rather than a single rectangular casing.
- Hip, knee and ankle endpoints define a wider asymmetric stance. The mixer
  foot steps forward onto a separate raised slab.
- The mixer vessel, loader chassis, truck cab and bucket are rebuilt around
  those leg/foot structures.
- A longer faceted cannon replaces the short rotary-barrel silhouette.
- Four perspective cameras replace the V1 orthographic inspection presentation.
  A separate turntable camera and a continuous studio cyclorama are included.
- The hero camera now uses a 40.7-degree azimuth from the global front axis.
  Full-body views use lens shift to center the asymmetric silhouette without
  flattening its perspective. The cyclorama uses a floor-tangent circular arc.

The reference remains Rex Hsu's work at
<https://www.artstation.com/artwork/w6KbAZ>, with the six user-supplied JPEGs in
`../references/`. No reference image is used as a surface texture or embedded
in the exported model. This is an unofficial original fan interpretation.
The supplied 12.01-second turntable video was inspected locally. See
`REFERENCE_NOTES.md` for its fingerprint, observed features and interpretation limits.

## Deliverables

- `deliverables/devastator-v2.blend`: editable native Blender scene.
- `deliverables/devastator-v2-hero.png`: perspective three-quarter view.
- `deliverables/devastator-v2-front.png`: frontal proportion view.
- `deliverables/devastator-v2-rear.png`: rear mechanical structure.
- `deliverables/devastator-v2-detail.png`: upper-body close-up.
- `assets/devastator-v2.glb`: evaluated static combined form.
- `assets/devastator-v2.json`: source/asset hashes, geometry statistics,
  cameras, render settings and foot-contact targets.
- `qa/scene-audit.json`: saved-scene and export verification.
- `deliverables/devastator-v2-360.mp4`: 1920 x 1080, 24 fps, 12-second H.264 turntable.
- `qa/turntable-render.json`: render settings, source and per-frame hashes.
- `qa/video-audit.json`: encoded-video and all-frame decoding checks.
- `qa/video-contact-sheet.jpg`: 12 decoded video views for visual inspection.
- `PROMPTS.md`: Chinese prompts for images, editable 3D and video, with a compact
  version and instruction-writing guidance.

The four full-size stills use Cycles at 1600 x 1200, 64 samples, with denoising.
The file opens on `V2 View hero`. The other views are named Blender cameras;
`V2 View turntable` rotates through 360 degrees over frames 1-289 at 24 fps.
Only frames 1-288 are encoded, avoiding a duplicate loop endpoint. The sculpture
and base remain static. Video uses Eevee with 64 samples, ray tracing and fast
GI, importing the exact evaluated GLB and reusing the native studio and cameras.

The recovered render is complete and the MP4 has been encoded and validated.
The final scene audit passes with 3,791 source meshes, 68 GLB meshes, 610,432
triangles and all 289 orbit positions checked. All four stills and 12 decoded
video samples were visually inspected. Full details and limits are in `QA.md`.

## Reproduce

Run from the repository root, using the Mac's installed Blender:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python devastator/v2/scripts/build_devastator.py -- \
  --render --resolution 1600 --samples 64

/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python devastator/v2/scripts/audit_scene.py

/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python devastator/v2/scripts/render_turntable.py -- --all

python3 devastator/v2/scripts/encode_turntable.py

/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python devastator/v2/scripts/audit_scene.py
```

Codex requires approved execution outside its sandbox for this Mac's native
graphics backend. There is no separate Blender installation or container.
Always render all four views before running the complete audit.
Stills use the Metal GPU by default; use `--device CPU` when unavailable.
FFmpeg and ffprobe are required to encode and validate the video. Intermediate
frames live under `work/turntable-<signature>/`, are resumable for identical
inputs/settings, and are excluded from the delivered asset bundle.

## Remaining Work

This revision changes the silhouette and structure; it does not reach the
reference sculpt's surface density, exact armor contours, mechanical complexity
or finish. Treat the images as a visual review checkpoint, not an accepted final
reproduction. Fine design work remains on the head, vehicle shell segmentation,
hands and mechanical transitions.

There is no final paint, independent vehicle mode, physical transformation
or web inspector. Selected surface-clearance checks are not an exhaustive
collision or engineering certification. See `QA.md`.
