# Optimus Showcase Verification

Local verification on 2026-09-13 using Blender 5.2.1 LTS, Node.js 22,
Three.js 0.180, Vite 7 and Chrome driven by Playwright.

## Automated Checks

- 36 Node tests pass: the original 25 metro tests plus 11 Optimus tests.
- The actual GLB has exactly the 29 joint IDs recorded in the rig manifest.
- The joint definition is a parent-ordered tree with six wheel assemblies.
- Robot and truck endpoint poses match the manifest.
- Assembly begins at the exploded pose and ends at the exact robot pose.
- Objects are reused at all intermediate states; no scaling or mesh swapping.
- Head retraction happens only with the two roof hatches open.
- The chassis lift protects the foot-folding phase.
- Every articulated joint and the nominal camera path are checked for
  continuous position/rotation across all 1,920 film frames.
- A regression test checks intermediate transformation framing at desktop,
  mobile and video aspect ratios.

## Asset and Browser Checks

- Blender generated the editable `.blend`, GLB, rig manifest and two Cycles
  renders successfully. An initial sandboxed Blender launch crashed during
  Metal device initialization; the approved native launch succeeded.
- Blender: 503 meshes. Browser: 89 material/joint batches, 29 articulated
  groups. Typical draw count: 90-92; approximately 102,000 triangles.
- Robot, truck, exploded and intermediate assembly/transformation screenshots
  inspected. Initial desktop pixel variances ranged from 1,357 to 3,172.
- Desktop 1440 x 1000 and mobile 390 x 844 layouts inspected; no horizontal
  page overflow. Mobile has all five presentation modes and both configurations.
- Playback advances and pauses; timeline seeking changes joint poses.
- Robot/truck selection, assembly highlighting and wireframe controls tested.
- Intermediate camera clipping was found and fixed with bounds-aware framing.
- At 0.125-second intervals throughout the complete 80-second sequence, the
  updated model's minimum Y was 0.0125 m and its largest projected bounding-box
  coordinate was 0.892858. No sampled pose went below the floor or outside the
  camera frame. Earlier pre-fix screenshots are superseded by the fixed capture.
- Export cancellation tested: the source mode, time and enabled playback
  controls restore without leaving the scene locked.
- Simulated scene-module failure shows an error and retry action. Simulated
  encoder-module failure leaves the scene usable and re-enables playback.
- Final MP4: H.264 / yuv420p, 1920 x 1080, 24 fps, exactly 1,920 frames /
  80.000 seconds, 51,026,023 bytes, no audio stream (ffprobe).
- The whole movie decoded with ffmpeg without errors; its contact sheet was
  inspected. A separate 90-pixel caption band does not cover model geometry.
- The formal repository build passed. Native MP4 playback and seeking worked
  in Chrome, including at 390 x 844. Navigation to the existing metro viewer
  and back passed with no page runtime errors; the metro loaded without an
  error state or horizontal overflow.

These are sampled visual and bounding-box checks, not proof of solid-to-solid
self-collision freedom or manufacturing feasibility. Physical mobile devices
and the ChatGPT embedded browser were not tested. The original `.blend` assets,
GLBs and metro movie remain unchanged.

Screenshots are stored in the ignored `output/playwright/` directory.
