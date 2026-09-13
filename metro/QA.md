# Verification

Verified on 2026-09-13 using Blender 5.2.1 LTS, Node.js 22, Vite 7 and Chromium
driven by Playwright on macOS. Mobile checks emulate viewport dimensions; they
are not physical iOS or Android device tests.

## Assets and Build

- `npm install`: dependency audit reports zero vulnerabilities.
- `npm run build`: passes. Three.js produces a bundle-size advisory, not an error.
- `npm test`: 25 tests pass, covering navigation, boarding, furniture and track
  boundaries, upper/lower camera presets, responsive framing, layer visibility
  and the 80-second film timeline.
- `metro/scripts/check_assets.py`: passes from the repository root under
  `/Users/ruiliang/Documents/workspaces/venv/bin/python`.
- GLB: 1,127 nodes, 1,115 meshes, 12 door leaves, 166 roof-related objects.
- GLB size: 9,012,696 bytes.
- Blender original: compressed, approximately 0.6 MB.
- Station GLB: 2,629 nodes; 898 removable cover objects; 9,369,128 bytes.
- Combined editable station and train file: approximately 1.5 MB.
- Platform: 36 m long, 6.22 m wide, five central columns and two tracks.
- Car geometry bounds, excluding rails and studio: 19.35 x 3.10 x 3.90 m.
  These are model bounds, not engineering measurements of a real vehicle.
- Exterior, passenger saloon and driver cab Cycles renders inspected visually.
- New station platform and open-roof overview Cycles renders inspected visually.
- Passenger signage and console legends corrected to face the observer.

## Browser Checks

Desktop viewport: 1440 x 1000. Mobile viewport: 390 x 844.

- Model loads with no browser console errors.
- Station overview, platform, passenger and driver presets render distinct views.
- WebGL pixel sampling confirms rendered geometry, not an empty background.
- Mobile red-channel pixel variances: overview 831, platform 2304, interior 1415,
  cab 5062 (all above the nonblank threshold of 50).
- Exterior auto-orbit moves the camera; dragging changes the interior view.
- All 12 door leaves remain present; only the six platform-facing leaves open.
- The station cover is hidden in the overview and restored in first-person views.
- Train roof removal works; entering the saloon restores the ceiling.
- Browser keyboard walkthrough crosses the central doorway into the saloon and
  returns to the platform without jumping between camera presets.
- Attempting to close doors while standing at the threshold is refused.
- With doors closed, outward movement stops at Z = 1.197 instead of crossing
  the door. Reopening permits alighting and updates the active view to platform.
- Keyboard W moves along the saloon aisle after using the view tabs.
- On-screen forward control moves in the cab and stops at X = 8.21 m.
- Cab visitor movement stays clear of the driver's chair.
- Instrument hotspot opens its detail panel and moves the camera.
- PNG capture downloads `M01-cab.png`; GLB download returns `metro.glb`.
- No mobile horizontal overflow; controls and detail panel visually inspected.

Screenshots are in the repository-root `output/playwright/` locally and excluded from Git.

## Underside Inspection

- Desktop: 1440 x 1000. Mobile: 390 x 844, inspected visually.
- Separate station and train inspection scopes work in the 360-degree view.
- Both bottom presets move below Y = 0, with polar angle greater than PI/2.
- Manual orbit dragging crosses the horizon; ground/track visibility updates
  from actual camera height rather than only from a preset-button state.
- Train underside hides station, presentation floor and display track.
- Station underside is an X-ray view. Opaque platform structure, grout, floor
  tiles and ballast are grouped separately and hidden along with the original
  train display trackbed. Rails, sleepers and train geometry remain visible.
- The platform reference is a depth-tested outline plus a plane at 4.5% opacity;
  it does not write depth and cannot act as an opaque blocker.
- Actual asset grouping verified: 6 station deck batches, 1 train trackbed
  batch, and 2 platform reference objects.
- X-ray pixel variances: desktop 1114, mobile 489; automatic orbit moves the
  camera and the deck/trackbeds restore when leaving underside inspection.
- Bottom auto-orbit changes camera position while keeping it below the subject.
- The earlier non-X-ray station screenshot is superseded by
  `output/playwright/station-xray-desktop.png` and `station-xray-mobile.png`.
- Bottom PNG capture downloads `station-bottom.png`.
- Returning to the passenger saloon restores ground, foundation and station roof.
- No browser console errors in the inspection test session.
- Existing Blender/GLB assets are unchanged by this viewing-controls update.

## Intentional Limits

- Instrument displays are static artwork, including the door-status legend.
- First-person navigation uses a constrained visitor path rather than full
  rigid-body collision. It does not let visitors walk onto the track.
- Roof removal is an exterior inspection preference; the ceiling is restored
  while viewing the interior.
- A 240-frame camera orbit is included in the standalone train Blender file.
  A separate 80-second MP4 is rendered from the film-only Three.js scene.
- No external model downloads, paid assets or authentication are needed.
- Arrival boards and instrument readouts are static concept artwork.
- The exit stair is visual scenery; the upper concourse is not explorable.
- The Sketchfab listing is visual inspiration only; no assets from it are bundled.
- The GitHub repository is private; no public web deployment is configured.

## Video Recovery and Verification

Verified on 2026-09-13 after the previous task stopped with `Input is too long`.
Its unfinished film sources were recovered from `/private/tmp/blender-metro-demo`;
the original project previously had no film source or MP4 deliverable.

- Earlier development logs reported `504 (Outdated Optimize Dep)` for
  `mediabunny` and a missing `mp4-muxer` entry during dependency optimization.
  A top-level encoder import prevented scene startup, leaving the static
  loading label on screen. Export now lazy-loads its encoder.
- A dependency-free bootstrap catches scene/module startup failures, shows
  retry, and warns after 45 seconds. Controls remain disabled until ready.
- `watch.html` uses a native video element and does not require WebGL,
  JavaScript or WebCodecs to play the generated MP4.
- Chrome playback and seeking verified at 1440 x 1000 and 390 x 844;
  no horizontal overflow. Live storyboard playback advances, pauses and seeks.
- Nine live keyframes inspected across arrival, station orbit, train orbit,
  rear entry, saloon, cab, cab exit, alighting and departure. Pixel variance
  exceeded 2800 for every sampled keyframe.
- A sampled six-axis ray check at 0.125-second intervals from 42 to 67 seconds
  found no opaque train mesh within 0.055 m of the camera. This is a sampled
  visual-clearance check, not a general collision or passenger safety proof.
- Simulated encoder-module failure: preview still starts, export shows an
  error, and playback controls are re-enabled.
- Simulated scene-module failure: startup error and retry are shown.
- Export: H.264, yuv420p, 1920 x 1080, exactly 24 fps / 1920 frames /
  80.000 seconds, 56,218,572 bytes, no audio stream (verified with ffprobe).
- Entire MP4 decoded by ffmpeg with no errors; contact sheet inspected.
- The original `.blend` and `.glb` files are unchanged. Rear-door animation
  and updated cab door-status graphics are confined to the film scene.
- Browser QA uses local Chrome. ChatGPT's embedded browser and physical
  mobile devices were not tested.
