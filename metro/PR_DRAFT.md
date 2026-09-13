# Add Central station and full underside inspection

Status: local draft only. No GitHub pull request has been created.

## Intended Branches

- Base: `main`, to be initialized from the existing remote baseline `3b7942a`
  once repository approval is resolved.
- Head: `codex/metro-bottom-view`.
- The head includes the locally committed Central station work (`ded5168`)
  followed by the underside inspection changes.

## Summary

- Add the original Central island-platform station, editable Blender scene,
  station GLB, preview renders and a continuous platform-to-train visitor route.
- Add separate station and train inspection scopes.
- Allow orbiting below the horizon and add an underside camera preset.
- Hide presentation ground and foundation below the station; hide station and
  track geometry when inspecting the standalone train undercarriage.
- Make station underside inspection an X-ray view: hide opaque decks and
  trackbeds while preserving solid rails and train running gear, with a faint
  platform reference outline.
- Restore the station enclosure when returning to platform, saloon or cab views.
- Add responsive framing and underside illumination without changing model assets.

## Verification

- `npm test`: 18 camera, visibility, mesh grouping and navigation tests.
- `npm run build`.
- Asset validation using the shared Python virtual environment.
- Playwright desktop/mobile screenshots and canvas-pixel verification.

## Publication Prerequisite

Code Defender blocked prior assistant pushes to this external repository.
A later read-only check found remote `codex/metro-bottom-view` at `0fb3288`,
and local upstream tracking is now configured. The X-ray correction is a
subsequent local change; no `main` branch was present at the latest check.
Further publishing must pass the configured security checks. Creating a PR is
not an alternative route around repository approval.
