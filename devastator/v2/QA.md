# V2 Verification / 2026-09-15

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
