# Optimus Prime / V2 Cinematic Metal Study

Original, unofficial G1-inspired fan study. The robot and cab-over truck share
one articulated mesh set. No third-party model, texture, logo or audio asset is
bundled. This is a stylized mechanical visualization, not an official product,
an exact reproduction of a commercial toy, or a manufacturing-ready mechanism.

## Version 2

V2 keeps the large G1-inspired panels and 29 main articulated assemblies rather
than introducing fragmented movie armor. It changes the finish to brushed steel,
deep crimson/cobalt metal, restrained edge wear, packed roughness/metalness maps
and micro-normal detail. The maps are embedded in GLB and packed into the Blender
file. They do not require extra browser texture requests.

Seven guided telescoping supports connect the head, shoulders, waist and front
axle carriers to the chassis. Each support uses fixed-length, nested tube meshes;
stages translate and rotate but do not scale or get exchanged for another model.
The chassis height follows a 257-sample contact curve derived from evaluated mesh
vertices, so transformation stays close to the stage instead of lifting the
whole figure along the former presentation curve.

The neck has a real roof notch; the fists fit inside the forearm sleeves; the
shoulders fold, descend and then slide inward through open cab-side channels.
Feet fold outward only after the legs rise, and front wheels move into position
after the arms clear their path. Rear wheel spacing and the shoulder crossmember
clearances have also been corrected.

## Deliverables

Paths in this list are relative to the `optimus/` task directory.

- `index.html`: interactive Three.js presentation.
- `watch.html`: ordinary MP4 playback without WebGL or JavaScript.
- `deliverables/optimus-showcase.mp4`: the complete directed sequence,
  80 seconds, 1920 x 1080, 24 fps, silent H.264.
- `deliverables/optimus-prime.blend`: editable Blender model, materials, joint
  hierarchy and an 80-second keyed animation with a camera orbit.
- `assets/optimus.glb`: one model with 29 stable articulated joints.
- `assets/optimus-rig.json`: the robot/truck poses, explosion offsets,
  assembly ordering and transformation intervals used by the web viewer.
- `deliverables/optimus-robot.png`, `optimus-truck.png`: Blender Cycles renders.
- `scripts/build_optimus.py`: reproducible model and asset generation.
- `scripts/metal_surfaces.py`: deterministic PBR map generation.
- `scripts/rig_motion.py`: shared Blender pose evaluator.
- `scripts/audit_motion.py`: selected moving-surface BVH checks.
- `qa/motion-audit.json`: current collision report, bound to model and rig hashes.
- `assets/surfaces/`: editable source PNG maps, also embedded in the model.

The Blender source has 550 mesh objects, including fasteners, tire tread blocks,
armor and glazing. For browser rendering, static meshes are batched inside each
joint; there are 127 browser meshes including the unbatched guide stages.
Moving parents, object identity and joint hierarchy remain
intact. The original metro assets and film are not replaced.

## Presentation

The five modes are robot/truck 360-degree inspection, assembly-level exploded
view, ordered assembly, transformation and the full directed camera sequence.
Playback supports pause, restart, scrubbing and 0.5x/1x/1.5x/2x speeds.
The desktop inspector includes component highlighting, wireframe, and front,
side, rear and top camera presets. Both desktop and mobile have robot/truck
configuration switches and orbit dragging. Selecting a camera preset or dragging
switches to manual camera control; the director preset restores the camera path.

Explosion separates 29 articulated assemblies, not each of the 550 decorative
meshes. No parts are faded out or exchanged for another complete model during
assembly or transformation. Guides stay with their chassis-side mount during
the exploded presentation; they track the mating joints during transformation.

## Motion

The head retracts while the roof panels slide apart. Fists retract into their
forearm sleeves; shoulders temporarily spread while elbows fold. Hip joints
rotate the thighs and lower legs into the rear frame, feet rotate into the deck,
and the front axle carriers move into the truck position. The contact-height
curve keeps the lowest body surface above the stage. Reversing the timeline reverses the same
joint operations.

Some stages use telescoping translations and simplified hinge geometry.
The current triangle BVH audit checks 21 selected moving-part pairs at 161
transformation states and reports no surface intersections in those checks.
It is not a rigid-body solver, a swept-volume proof, or a manufacturing tolerance
analysis. Unlisted contacts and intentionally nested guide tubes are outside its
scope. The animation emphasizes readable component correspondence and continuous
motion.

| Time | Camera sequence |
| --- | --- |
| 00:00-00:12 | Robot 360-degree orbit |
| 00:12-00:20 | Assemblies separate |
| 00:20-00:28 | Exploded 360-degree orbit |
| 00:28-00:40 | Ordered assembly |
| 00:40-00:44 | Robot inspection |
| 00:44-00:58 | Robot to truck |
| 00:58-01:06 | Truck 360-degree orbit |
| 01:06-01:20 | Truck to robot |

Web camera framing tracks the actual model bounds, including during intermediate
transformation. Every box corner is fitted with margin for both horizontal and
vertical field of view. This avoids cropping tall intermediate poses when the
camera changes from robot framing to truck framing.

The MP4 export button renders this complete 80-second sequence deterministically
at 1920 x 1080 / 24 fps through Three.js and WebCodecs H.264, independent of the
current inspector mode, playback speed and display size. Export can be canceled.
Chrome with WebCodecs support is required for encoding; scene playback does not
load the encoder until it is needed. This is not a Cycles-rendered movie.

## Reproduce

Run commands from the repository root.

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python optimus/scripts/build_optimus.py -- --render
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python optimus/scripts/audit_motion.py
npm test
npm run build
npm run verify:deploy
npm run preview -- --port 5193
```

Open `http://127.0.0.1:5193/optimus/`. For development, use
`npm run dev -- --port 5193`. Pick another port if it is occupied. The 3D page
requires HTTP and WebGL; do not open it with `file://`.

Blender writes GLB and rig data before adding studio lights, floor and camera.
Omit `-- --render` to skip the two Cycles still renders. Blender and web poses use
the same staged joint calculations; Blender's keyed camera is a reference orbit,
while the browser uses the bounds-aware director camera.

The optional Google Fonts request supplies Barlow and Barlow Condensed. Local
system fonts are the fallback; no remote visual asset is required.

See `QA.md` for verification results and the limits of the checks. Re-run the
motion audit after generating assets: tests reject a stale audit whose hashes
do not match the current GLB and rig JSON.

If rebuilding the model, export the movie again to keep it synchronized.
The generated movie is included by the production build; generating GLB alone
does not regenerate the existing MP4.
