# Optimus V3 Dual-Weapon Verification

Verified locally on 2026-09-13 with Blender 5.2.1 LTS, Node.js 22,
Three.js 0.180, Vite 7 and Chrome/Playwright.
The V2 checkpoint remains available at Git commit `fd53385`.

## Appearance And Assets

- 35 articulated groups, eleven guided telescoping supports.
- 730 source mesh objects, reduced to 178 browser meshes by static batching.
  Of the browser meshes, 157 carry both base-color and normal maps.
- Seven metal finish families have embedded base-color and metal/roughness maps,
  with a shared brushed-normal map. Editable PNGs are in `assets/surfaces/`.
- Higher shoulders, a narrow abdomen, longer tapered legs, level feet in a
  wider stance, a faceted helmet/mask and blue segmented hands follow the
  supplied reference direction. Rear wheels sit behind the calves.
- Window frames are single annular meshes, with no coplanar strip overlaps.
- Blender robot and truck renders inspected. Browser robot, exploded view,
  intermediate states and truck inspected at 1440 x 1000 and 390 x 844.
  No horizontal mobile page overflow. No browser console errors recorded.
- Canvas pixel checks at three transformation states found 1,417, 851 and 1,683
  distinct sampled colors and three different pixel hashes. Playback advanced
  while running, confirming both a nonblank canvas and live animation.

This is a simplified, reference-guided fan model, not an exact reproduction.
The screenshots do not establish the reference's hidden rear/truck mechanism.
The robot holds both a dark ion rifle and an orange/gold short energon axe,
following the supplied accessory references. Their meshes remain present in
all modes, including the truck. Opening chest doors and raised-arm action
poses remain outside this iteration.

## Motion

- 48 Node tests pass, including unchanged Metro and layout tests.
- All 1,920 film-frame continuity checks pass. Robot and truck use the same
  objects; moving joints and guide tubes do not scale or swap geometry.
- Eleven guides use overlapping, fixed-length nested stages. Endpoint tracking
  is tested at 161 transformation states.
- Rear wheel carriages extend sideways before crossing calf depth and then
  close to truck width. Regression tests check this clearance order.
- Blender triangle BVH: 67 selected part pairs at 321 transformation states
  (21,507 pair/state checks), PASS with no detected surface intersections.
- The expanded audit covers head/chest, shoulder/cab/abdomen, fist sleeves,
  front wheels, rear carriages/wheels/calves/feet, foot/hip and opposite shins.
- Each weapon is also tested against its forearm, shoulder, front wheel,
  thigh, shin, foot, rear wheels, cab, abdomen and head. Hand/grip contact and
  the small carrier fittings are not included in these pairwise checks.
- Weapon carriers move outward before folding, take an additional outward
  detour during front-axle motion, and close after the wheels clear.
  The axe has a wider parked offset to clear the exhaust shield.
- Half-turn direction is explicit in both runtimes. This avoids the opposite
  quaternion interpolation arcs caused by float32/float64 rounding at pi.
- Development checks caught ankle/shin, shoulder/window, exhaust/window,
  front-wheel/shoulder and shoulder/waist-strut intersections. Geometry and
  clearances were corrected rather than removing those pairs from the audit.
- The report binds GLB, rig JSON, Blender file, builder, weapon generator and Blender pose
  evaluator SHA-256 hashes. Tests reject stale combinations.
- Browser joint poses match independently evaluated Blender poses at 17 states.
- The ground-contact curve has 257 samples. Browser checks every 0.5 seconds
  over the 80-second film found minimum surface Y = 0.039764 m and maximum
  absolute projected X/Y bound = 0.892858. No sampled surface crossed the
  floor or camera frame.
- The audit also measures the unarmed body separately, preventing weapons
  from lifting the truck off its tires. Body minimum height across samples
  is 0.039669-0.050787 m. All six final tire minima are about 0.042500 m.
  The elbow slides into upper-arm rails when folding so arm armor no longer
  determines the truck's ground-contact plane.

These are selected triangle-surface tests, not exhaustive solid containment,
swept-volume collision detection, rigid-body simulation or manufacturing
certification. Nested guide tubes, same-assembly seams, other component pairs
and unsampled instants are not certified. Mobile checks emulate viewports,
not physical devices.

## Video And Build

- Re-exported the complete armed V3 sequence through Three.js/WebCodecs.
- FFprobe: H.264, 1920 x 1080, 24 fps, 80 seconds, 1,920 frames, no audio.
- Final MP4 size: 57,878,015 bytes.
- FFmpeg full-file decode passes.
- `npm run build` passes. Large Three.js/encoder chunk warnings remain.
- `npm run verify:deploy` checks ten pages, 34 referenced files and eight
  byte-identical runtime assets, including the updated movie.
- Synced to the main checkout and repeated all 48 tests and the static build.
- Local HTTP validation at `http://127.0.0.1:5193` passes: 34 hosted files,
  eight runtime asset hashes and two video range requests.
- Main-checkout browser smoke check confirms both weapons, rifle selection
  and live playback, with no recorded page errors. No remote deployment.

Metro source and assets are unchanged. Browser evidence is in the ignored
repository-root `output/playwright/` directory.
