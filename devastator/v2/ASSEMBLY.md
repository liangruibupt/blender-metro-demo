# Devastator V2 / 18-Second Assembly

## Scope

This animation adds a one-way cinematic assembly to the existing V2, within the
same directory. It does not replace the accepted sculpture or the 360-degree
turntable. It is not a simulation of six roadworthy vehicles transforming.

The same evaluated geometry is regrouped into 81 meshes, driven by 11 main
module controls and three secondary controls: both elbows and the folded crane.
All 610,432 triangles and original material assignments are retained. No mesh
decimation, visibility pop-ins, scaling tricks, explosions or light effects
hide the assembly. Final controller transforms return to their exact bind pose.

## Choreography

| Time | Action |
| --- | --- |
| 0-1 s | Separated modules hover in a readable exploded arrangement |
| 1-4.8 s | Loader and mixer legs align and settle onto the existing base |
| 3.3-7 s | Pelvis and chest descend and lock together |
| 6.3-10.8 s | Shoulder modules attach; arms align and elbows fold |
| 9-12.8 s | Rear powertrain and crane dock; the crane folds into its final pose |
| 11-12.5 s | Head lowers into the chest/shoulder frame |
| 12.5-14.8 s | Cannon aligns with the existing gripping hand |
| 14.8-18 s | Completed model remains assembled while the camera finishes its arc |

Module motion has a smooth approach, a short alignment pause and a final small
locking movement. The camera makes a restrained arc and gradual dolly-in;
there are no cuts. Floating starting modules are a presentation convention,
not a claim of physically unsupported vehicle flight.

## Delivery

- `deliverables/devastator-v2-assembly.blend`: native animated scene, evaluated
  editable meshes, controls, camera, lights and timeline markers.
- `deliverables/devastator-v2-assembly.mp4`: completed 18-second video.
- `assets/devastator-v2-assembly.json`: settings, source hashes, bind matrices,
  control mapping and output hashes.
- `qa/assembly-scene-audit.json`: reopened scene and all-frame checks.
- `qa/assembly-render.json`: resumable render provenance and frame hashes.
- `qa/assembly-video-audit.json`: encoded-video checks.
- `qa/assembly-contact-sheet.jpg`: 18 decoded video samples, one per second.

Verified video: 18 seconds, 1920 x 1080, 24 fps, 432 frames, H.264, no audio.
Rendering retains the turntable's Eevee 64 samples, ray tracing, fast GI,
studio, lights, material parameters and color management.
The cyclorama radius is expanded for the opening wide shot; the floor height,
surface material and lights are unchanged.

The original `devastator-v2.blend` remains the detailed construction source.
The animation scene uses evaluated geometry with baked bevels, just as the
existing turntable does; original procedural objects remain in that source.

## Reproduce

Run from the repository root using the installed Mac Blender:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python devastator/v2/scripts/build_assembly.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python devastator/v2/scripts/audit_assembly.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python devastator/v2/scripts/audit_assembly_motion.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python devastator/v2/scripts/render_assembly.py -- --all
python3 devastator/v2/scripts/encode_assembly.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python devastator/v2/scripts/audit_assembly.py
```

Preview selected frames by omitting `--all`; optional `--width 960 --samples 24`
is for preview only. Final quality is checked against the manifest at encoding.
Temporary frames live in `work/assembly-<signature>/`, outside delivered assets.
Progress is checkpointed every 12 frames. Identical inputs can resume; changes
to the scene, scripts or rendering settings create a new signature.

## Verification Limits

The validator checks source/output hashes, unchanged triangle count, original
materials, all-frame control transforms, unit scale, floor clearance and
framing, sampled background rays, exact final vertex positions, and the four
selected final-pose surface pairs used for V2.

It does not certify swept-volume collision freedom, internal joints, load
bearing, mechanical latches, finger regripping or viable vehicle forms.
The gripping hand retains its existing modeled shape. Visual inspection of
keyframes and decoded-video samples supplements, but does not expand, those
technical guarantees.

`audit_assembly_motion.py` independently checks the four established non-joint
surface pairs at all 432 discrete frames. Disjoint bounding boxes are rejected
first; overlapping boxes receive a triangle-level BVH surface check. Its report
is `qa/assembly-motion-clearance.json`, bound to the scene and validator hashes.
This does not examine unlisted pairs or motion between frame samples.

## Completed Checkpoint

The production render completed all 432 frames. Encoding and full decoding
passed; minimum frame grayscale deviation is 38.786 and maximum adjacent
frame difference is 1.030 at the validator's 160 x 90 resolution.
There are ten near-identical transitions around the deliberately eased opening
and ending, but no run reaches the half-second freeze threshold.

The reopened scene audit and independent motion-clearance audit both pass.
All 18 one-second decoded samples were visually inspected, along with
full-resolution opening, late-assembly and completed-pose frames.
This is sampled visual QA, not manual inspection of every frame.
Original sculpture and 360-degree files are unchanged.
