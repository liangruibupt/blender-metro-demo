# Devastator Checkpoint QA

Date: 2026-09-14.

## Performed

- Both Python scripts pass `ast.parse` syntax validation.
- The failed Blender invocation exited with code 139 during native startup;
  the crash stack is summarized in `RECOVERY.md`.
- Staging `assets/`, `deliverables/`, `src/` and `qa/` folders were inspected
  and contained no generated files.
- Six reference JPEGs and the two source scripts are included in the
  SHA-256 checkpoint manifest.

## Not Verified

- Blender execution of either Python module.
- Blender API compatibility, generated topology, normals or GLB export.
- Visual similarity, body proportions, material appearance or render framing.
- Intersections, attachment continuity, foot contact or physical mechanisms.
- Camera animation. A known detachment of the turntable action is documented
  in `RECOVERY.md`.
- Browser rendering, mobile layout, automated viewer tests or deployment.

AST parsing is not a Blender runtime test. The repository's existing Metro
and Optimus tests do not validate this new draft, and their prior passing
results must not be cited as Devastator verification.
