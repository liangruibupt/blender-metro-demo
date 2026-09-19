# V2 Verification / 2026-09-15

## Added Assembly Animation

The 18-second assembly scene preserves 610,432 triangles in 81 evaluated
meshes, driven by 14 controls. The original sculpture, stills and turntable
remain unchanged.

The reopened animation passes all 432 frames for camera framing, unit scale,
finite control transforms, floor clearance and 3,888 studio coverage rays.
The camera is also checked to remain inside the expanded cyclorama.
The largest final vertex displacement from the original bind geometry is
0.0000016093 model units, below the 0.0001 tolerance.

An independent motion audit checks four named pairs across all 432 frames:
1,728 pair/frame checks, comprising 1,592 disjoint bounding-box rejections and
136 triangle-level BVH tests. No surface crossing is found in those pairs.
This excludes other pairs, containment and motion between sampled frames.

Nine low-resolution keyframes were rendered for visual QA, including the
opening layout, leg/torso docking, arm folding and completed pose. The initial
preview exposed a camera outside the studio and an early dolly-in cropping the
head; both were corrected before the final render. The corrected keyframes and
the first full-resolution frame were opened and inspected.

Evidence: `assembly-scene-audit.json`, `assembly-motion-clearance.json`.
Final video validation is recorded in `assembly-video-audit.json`: PASS.
The encoded H.264 stream is exactly 18 seconds, 1920 x 1080, 24 fps and 432
frames, with no audio. All 432 frames decode; minimum grayscale deviation is
38.786 and maximum adjacent-frame difference is 1.030 at 160 x 90.
Ten transitions near the slowly eased opening/ending are nearly identical;
none form a half-second freeze. This one-way assembly is intentionally not a loop.

All 18 once-per-second decoded samples in `assembly-contact-sheet.jpg` were
opened for visual inspection. The production render used Eevee 64 samples,
ray tracing and fast GI, matching the existing turntable quality settings.
The complete saved-scene audit was repeated after MP4 encoding.

## Verified Delivery

The video-guided refinement and presentation checkpoint passes the native
Blender 5.2.1 LTS saved-scene audit and the encoded-video audit.

- 3,791 editable source meshes; 68 evaluated GLB meshes; 610,432 triangles.
- Both soles meet their world-space targets: loader Z=0, mixer Z=0.2,
  within the 0.002-unit tolerance. The raised support contains the checked
  mixer sole corners.
- Three full-body perspective cameras retain and center the whole sculpture.
  The fourth still is an intentionally cropped upper-body detail.
- All 289 orbit positions, including the loop endpoint, pass framing checks
  at the actual 1920 x 1080 video aspect ratio.
- 2,637 sampled studio rays hit the continuous backdrop. Its only open mesh
  boundary is the top rim.
- Four selected BVH surface pairs have no surface intersections:
  helmet/raised arm, helmet/cannon, cannon/loader leg, cannon/mixer leg.
- The scene reopens without linked libraries or unpacked image dependencies.
  Mesh count, finite transforms, assigned materials, grayscale GLB materials,
  independent GLB reimport extents and triangle count all pass.
- Source, native scene, GLB, four PNGs and MP4 match the build manifest hashes.
  The complete scene audit was rerun after video encoding.

## Images and Video

All four 1600 x 1200 Cycles stills were opened and visually inspected in this
resumed session. Hero/front/rear retain the sculpture and base; the close-up
intentionally crops outer shoulders and the lower body. Head, hand, cab and
back-crane additions are visible. No obvious background opening was observed.

The 12-second H.264 video is 1920 x 1080, 24 fps, 288 frames and has no audio.
The renderer uses Eevee, 64 samples, ray tracing and fast GI, with the evaluated
GLB and the native scene's camera and studio. Sculpture and base remain rigid.
Frame 289 is the matching orbit endpoint, not an extra encoded duplicate.

Every encoded frame was decoded. All 287 adjacent transitions pass the
non-frozen-frame threshold; the minimum grayscale standard deviation is
43.199. The loop difference is 1.609, compared with a maximum adjacent
difference of 1.630, within the validator's continuity threshold.

`video-contact-sheet.jpg` samples the decoded video once per second. These
12 views were visually inspected for front, side and rear coverage, framing,
missing parts and gross rendering artifacts. This is sampled visual QA,
not a claim that every pixel in every frame was manually inspected.

Machine-readable evidence:

- `scene-audit.json`: reopened scene, framing, selected clearances and hashes.
- `turntable-render.json`: input signatures, settings and 288 frame hashes.
- `video-audit.json`: codec, resolution, duration, decode and transition checks.

All evidence files and the contact sheet are in `qa/`. The render report's
`outputDirectory` records the temporary render location; intermediate PNGs
are intentionally not part of the delivered bundle. Rerendering from a new
location creates a new local frame sequence before encoding.

## Limits

Technical checks are not a likeness score. Compared with the reference,
V2 has a more upright pose, simpler head/hand contours and vehicle shells,
a more vertical rear crane and a more regular base. The reference uses a
brighter clay treatment on a flat cool-gray background; V2 uses a darker
studio and visible floor. `PROMPTS.md` distinguishes those two effects.

Selected BVH checks exclude intentional joints, nested containment and all
unlisted pairs. They do not certify a collision-free mechanism or a physically
possible transformation. There is no vehicle mode, transformation rig, final
paint pass or web inspector.

Only current V2 production assets are delivered. Original reference inputs and
git history are retained. Metro and Optimus are outside this verification scope.
