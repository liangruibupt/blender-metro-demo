# Devastator / V1 Clay Study

First reference-guided combined-form study, built and rendered with the Mac's
installed Blender 5.2.1 LTS. This is a proportion and mechanical-detail review
version, not final paint, an exact replica, or a validated transformation.

The task is independent of `metro/` and `optimus/`. All source, references,
generated assets and documentation stay in `devastator/`.

## Deliverables

- `deliverables/devastator-clay.blend`: editable panels, fasteners, tracks,
  hydraulic lines, grouped assemblies, studio lights and two cameras.
- `deliverables/devastator-hero.png`: three-quarter combined-form view.
- `deliverables/devastator-front.png`: frontal proportion view.
- `deliverables/devastator-rear.png`: crane, rear chassis and crawler details.
- `deliverables/devastator-detail.png`: upper-body close-up.
- `assets/devastator.glb`: static browser-ready mesh, batched by assembly and
  material. No reference images are embedded as textures.
- `assets/devastator.json`: model statistics, render settings and SHA-256 hashes
  binding the model, renders and generation scripts.
- `qa/scene-audit.json`: saved-scene, contact, camera framing and reimport checks.

All four stills are 1400 x 1400, Cycles, 48 samples with denoising. The first
900-pixel render was a development preview and has been replaced.

## Model Direction

The study uses broad crawler shoulders, a narrow mechanical waist, asymmetric
loader and mixer legs, an exposed crane backpack and a four-bore cannon.
Materials remain grayscale, with separate armor, steel, rubber, glass and
recesses. The body retains a simplified stylized form and substantially less
detail than the supplied sculpt. Proportion approval comes before final paint
or six-vehicle transformation work.

The Blender file retains individual editable parts. The GLB reduces draw calls
by batching evaluated geometry without including studio lights or the ground
plane. Its 12 named assembly labels include the display plinth; they are not
12 independently transformable vehicles.

## Blender Cameras

The file opens on `Inspection camera`, a static hero view. A separate
`Animated turntable camera`, parented to `Turntable orbit`, preserves one full
camera revolution from frame 1 through 241 at 24 fps. Select it as the scene
camera to inspect the orbit. The robot itself is static.

No MP4, web inspector or deployment integration is included in this Blender
modeling pass. The existing repository website remains unchanged.

## Reproduce

From the repository root, use the installed Mac application:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python devastator/scripts/build_devastator.py -- \
  --render --resolution 1400 --samples 48

/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python devastator/scripts/audit_scene.py
```

When invoked through Codex on this Mac, these commands need approved execution
outside the Codex sandbox so Blender can access the native graphics backend.
This does not install a different Blender or use a container.

The audit checks all four rendered files, so run the full render command before
the audit. Omitting `--render` generates the model but does not validate any old
stills. Rendering selected views is a development operation, not a complete
deliverable refresh.

`checkpoint-manifest.json` records historical hashes at commit `31abf51`;
use `assets/devastator.json` for the current generated version.

See `REFERENCE.md` for source attribution, `QA.md` for the scope of validation,
and `RECOVERY.md` before resuming work.
