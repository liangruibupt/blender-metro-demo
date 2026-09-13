# Optimus V2 Verification

Verified locally on 2026-09-13 with Blender 5.2.1 LTS, Node.js 22, Three.js 0.180,
Vite 7 and Chrome/Playwright. V1 remains available in Git history.

## Assets and Appearance

- 29 main articulated groups, seven guided telescoping supports.
- 550 source mesh objects; 127 browser meshes after static batching.
- 113 browser meshes carry base-color and micro-normal textures with UVs.
- Six metal finish families use embedded base-color, packed metal/roughness and
  shared brushed-normal maps. The editable maps live in `assets/surfaces/`;
  Blender packs them and GLB embeds them.
- Smaller, mostly single-segment armor bevels replace the rounded V1 edges.
- Reflective steel, darker painted metal, distinct rubber/glass and strip-light
  reflections were inspected in Blender renders and browser screenshots.
- Robot, truck, exploded view and intermediate transformation frames inspected
  at 1440 x 1000 and 390 x 844. No horizontal mobile page overflow.

## Motion

- 44 Node tests pass, including the unchanged Metro and layout tests.
- Pose endpoints, object reuse, head/roof timing and all 1,920 film-frame
  continuity checks pass.
- Seven guide assemblies keep fixed tube lengths with overlapping stages.
  Endpoint tests follow the real target joints at 161 transformation states;
  no tube scaling or geometry replacement is used.
- `scripts/audit_motion.py` uses evaluated triangles and Blender BVH at 161
  transformation states for 21 selected pairs. Final result: PASS.
- The audit found shoulder-bearing/crossmember intersections near the truck
  endpoint during development. The crossmembers were narrowed; the final
  audit has no intersections in the selected pairs.
- The passing report in `qa/motion-audit.json` records the GLB and rig SHA-256
  hashes. Node tests reject stale reports after an asset rebuild.
- A 257-sample chassis height curve uses evaluated vertices for grounding.
  Browser checks at 0.5-second intervals throughout the 80-second sequence found
  minimum actual surface Y = 0.03975 m, and maximum projected bounding-box
  magnitude = 0.892858. No sampled surface crossed the floor or camera frame.

The collision audit checks selected triangle surfaces, not all solid containment,
all possible component pairs, or every instant between samples. Nested guide
tubes and unlisted bearing contacts are outside its scope. It is not a physical
or manufacturing certification. Mobile checks emulate viewports, not devices.

The Metro source and its model/movie assets are unchanged. Screenshots are in
the ignored repository-root `output/playwright/` directory.
