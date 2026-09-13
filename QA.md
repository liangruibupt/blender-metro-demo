# Verification

Verified on 2026-09-13 using Blender 5.2.1 LTS, Node.js 22, Vite 7 and Chromium
driven by Playwright on macOS. Mobile checks emulate viewport dimensions; they
are not physical iOS or Android device tests.

## Assets and Build

- `npm install`: dependency audit reports zero vulnerabilities.
- `npm run build`: passes. Three.js produces a bundle-size advisory, not an error.
- `npm test`: 15 tests pass, covering navigation, boarding, furniture and track
  boundaries, upper/lower camera presets, responsive framing and layer visibility.
- `scripts/check_assets.py`: passes under
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

Screenshots are in `output/playwright/` locally and excluded from Git.

## Underside Inspection

- Desktop: 1440 x 1000. Mobile: 390 x 844, inspected visually.
- Separate station and train inspection scopes work in the 360-degree view.
- Both bottom presets move below Y = 0, with polar angle greater than PI/2.
- Manual orbit dragging crosses the horizon; ground/track visibility updates
  from actual camera height rather than only from a preset-button state.
- Train underside hides station, presentation floor and display track.
- Station underside hides the presentation foundation and ground, retaining
  platform and rail geometry.
- Bottom auto-orbit changes camera position while keeping it below the subject.
- Mobile pixel variances: train 742, station 273; no horizontal overflow.
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
  No MP4 is pre-rendered.
- No external model downloads, paid assets or authentication are needed.
- Arrival boards and instrument readouts are static concept artwork.
- The exit stair is visual scenery; the upper concourse is not explorable.
- The Sketchfab listing is visual inspiration only; no assets from it are bundled.
- The GitHub repository is private; no public web deployment is configured.
