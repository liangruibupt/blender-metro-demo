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
- Restore the station enclosure when returning to platform, saloon or cab views.
- Add responsive framing and underside illumination without changing model assets.

## Verification

- `npm test`: 15 camera, visibility and navigation tests.
- `npm run build`.
- Asset validation using the shared Python virtual environment.
- Playwright desktop/mobile screenshots and canvas-pixel verification.

## Publication Prerequisite

Code Defender blocked the station push to this external repository. Repository
approval must be completed before uploading the pending commits. The remote
currently contains only `codex/metro-demo` at `3b7942a`, with no `main` branch.
Creating a PR is not an alternative route around that approval.
