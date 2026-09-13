# Verification

Verified on 2026-09-13 using Blender 5.2.1 LTS, Node.js 22, Vite 7 and Chromium
driven by Playwright on macOS. Mobile checks emulate viewport dimensions; they
are not physical iOS or Android device tests.

## Assets and Build

- `npm install`: dependency audit reports zero vulnerabilities.
- `npm run build`: passes. Three.js produces a bundle-size advisory, not an error.
- `scripts/check_assets.py`: passes under
  `/Users/ruiliang/Documents/workspaces/venv/bin/python`.
- GLB: 1,127 nodes, 1,115 meshes, 12 door leaves, 166 roof-related objects.
- GLB size: 9,012,696 bytes.
- Blender original: compressed, approximately 0.6 MB.
- Car geometry bounds, excluding rails and studio: 19.35 x 3.10 x 3.90 m.
  The website rounds length to 19.4 m. These are model bounds, not engineering
  measurements of a real vehicle.
- Exterior, passenger saloon and driver cab Cycles renders inspected visually.
- Passenger signage and console legends corrected to face the observer.

## Browser Checks

Desktop viewport: 1440 x 1000. Mobile viewport: 390 x 844.

- Model loads with no browser console errors.
- Exterior, passenger and driver camera presets render nonblank, distinct views.
- WebGL pixel sampling confirms rendered geometry, not an empty background.
- Exterior auto-orbit moves the camera; dragging changes the interior view.
- All 12 door leaves animate to the open state.
- Roof removal works; entering the saloon restores the ceiling.
- Keyboard W moves along the saloon aisle after using the view tabs.
- On-screen forward control moves in the cab and stops at X = 8.21 m.
- Cab visitor movement stays clear of the driver's chair.
- Instrument hotspot opens its detail panel and moves the camera.
- PNG capture downloads `M01-cab.png`; GLB download returns `metro.glb`.
- No mobile horizontal overflow; controls and detail panel visually inspected.

Screenshots are in `output/playwright/` locally and excluded from Git.

## Intentional Limits

- Instrument displays are static artwork, including the door-status legend.
- First-person navigation uses a constrained visitor path rather than full
  rigid-body collision. It does not let visitors walk onto the track.
- Roof removal is an exterior inspection preference; the ceiling is restored
  while viewing the interior.
- A 240-frame camera orbit is included in Blender. No MP4 is pre-rendered.
- No external model downloads, paid assets or authentication are needed.
- GitHub publication and repository visibility are not configured automatically.
