# Optimus Checkpoint / 2026-09-13

> Historical V2 checkpoint, committed as `fd53385`. The current working version
> is V3 with both reference weapons; read `RECOVERY.md` first, then `REFERENCE.md`,
> `README.md` and `QA.md`. The archived WIP patch below
> was used as a starting point and then revised. Do not reapply it to V3.

## Scope

This checkpoint preserves the work recovered after the previous conversation
stopped with an input-length error. No new appearance or motion changes were
implemented during this checkpoint. Metro source and assets are unchanged.

The active project is `blender-metro-demo/optimus`, on branch
`codex/optimus-prime-showcase`. The previous committed baseline is `9e0ad87`.

## Active Version

The active source, GLB, rig JSON, Blender file, still renders and MP4 are the
V2 metal study. It has 29 articulated groups, seven telescoping guides,
550 source meshes and 127 browser meshes. Of those browser meshes, 113 have
base-color and normal maps.

V2 adds brushed-metal maps, sharper armor bevels, studio reflections, revised
shoulder/foot/wheel timing and sampled ground-contact height. It remains a
boxy, G1-inspired visualization, not the requested final cinematic design.
Its title should not be interpreted as user acceptance of the appearance.

## Recovered, Unfinished Proportion Study

`wip/reference-proportions.patch` preserves the only source difference between
the active repository and `/private/tmp/optimus-metal-v2` at recovery time.
It is NOT applied to the active source or bundled assets.

The patch changes the helmet, chest/waist proportions, glazing, blue hands,
longer legs and rear wheel carriages. It adds two articulated bogie groups.
It has not been built, rendered, collision-audited or validated against the
existing motion code and tests. Applying it invalidates the current QA claims.
Existing model, renders and video do not show this unfinished work.

The patch applies cleanly to this checkpoint's `optimus/scripts/build_optimus.py`.
From the repository root, inspect before deliberately applying:

```sh
git apply --check optimus/wip/reference-proportions.patch
git apply optimus/wip/reference-proportions.patch
```

SHA-256 for exact recovery:

- Active builder: `03843ec4c3e1683dfcbead793a105a91f30e5d3c2c51e9034571becad2068848`
- Recovered builder: `b47e0d8a13db21f22e71df4ec280d231f59772c5354f77c633105dde5f084ba0`

The original temporary directory is left intact.

## Checks Repeated For This Checkpoint

- `npm test`: 44/44 pass.
- `npm run build`: pass; Vite warns about two chunks larger than 500 kB.
- `npm run verify:deploy -- --url http://127.0.0.1:5193`: pass;
  10 pages, 34 files, eight asset hashes and two video range requests.
  This checks a local preview, not a remote deployment.
- Blender `audit_motion.py`: pass, 21 selected pairs at 161 sampled states.
  The report hashes match the current GLB and rig JSON.
- FFmpeg full MP4 decode: pass. FFprobe confirms silent H.264, 80 seconds,
  1920 x 1080, 24 fps and 1,920 frames.
- Chrome/Playwright: inspected nine film states at 1440 x 1000 and a robot
  frame at 390 x 844. No page errors during this check, no horizontal mobile
  overflow, and sampled model bounds remain in frame and above the floor.

The collision check is not exhaustive: unlisted pairs, solid containment,
contacts between samples and nested guide tubes are not certified.

## Next Iteration

Wait for the user's reference images before changing the design. Target a
cinematic metal finish with fewer, larger armor panels and readable mechanical
connections. Resolve body proportions as well as materials. Recheck the complete
motion path after geometry changes; continuous motion alone does not prove that
parts are connected or collision-free. Rebuild and re-export the GLB, Blender
file, stills and movie together, then rerun tests and visual checks.
