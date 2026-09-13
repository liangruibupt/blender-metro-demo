# Task Layout and Deployment Verification

Verified locally on 2026-09-13. This records validation of a deployable static
build, not a deployment to a remote hosting account.

## Organization and Integrity

- 51 existing files moved into the `metro/` and `optimus/` task directories.
- Each task owns its pages, source, styles, assets, scripts, deliverables and
  documentation. Root files are shared build/test infrastructure and legacy
  HTML redirects only.
- Every move was SHA-256 checked before and after the rename. The 18 model,
  image, movie and asset-metadata files retain their original bytes.
- No Blender model was rebuilt and neither full MP4 was re-encoded.
- Blender scripts now derive the task root and write to that task's `assets/`
  and `deliverables/`. Metro's Python asset check passed after relocation.
- 41 tests passed: the previous 36 behavior tests and five layout/build tests.

## Static Build

- `npm run build` passed.
- `npm run verify:deploy` passed: 10 HTML pages, 34 emitted/referenced files,
  and eight byte-identical runtime models, rig data, movies and posters.
- Model/rig imports use Vite asset URLs instead of document-relative strings.
  Download links use those same resolved URLs.
- The output was served at both `/` and `/blender-metro-demo/`.
- Static hosting tests used a byte-range-capable server with SPA fallback
  disabled. A nonexistent HTML URL returned 404 rather than a fallback page.
- `npm run verify:deploy -- --url <local-subpath>` passed for all 34 HTTP files
  and both video range responses.

## Browser Checks

- Chrome loaded Metro and Optimus at both base paths without runtime errors
  or missing local resources.
- Cross-task navigation worked. Both GLB download responses began with the
  `glTF` header and stayed inside the selected deployment prefix.
- Legacy `index.html`, `film.html`, `watch.html`, `optimus.html` and
  `optimus-watch.html` continued to reach their canonical task pages.
  Query strings and fragments were preserved in the checked legacy links.
- Both 80-second videos played and sought to 45 seconds, then advanced beyond
  45.2 seconds. Both base paths returned `206` and correct `Content-Range` for
  a video byte-range request.
- The initial basic Python HTTP server ignored Range and reset video seeking
  to the start. Rechecking with Range support passed; the hosting requirement
  is documented in the repository README and checked by `verify:deploy`.
- Metro film rendered a nonblank frame and exported a one-second / 24-frame
  smoke MP4, proving its lazy encoder chunk resolved under the subpath.
- Optimus rendered an exploded view and successfully canceled an export
  without leaving its controls locked.
- Desktop (1440 x 1000) and mobile (390 x 844) screenshots inspected.
  Sampled pixel variances: Metro film 3692, Optimus exploded 1381,
  mobile Metro 2351. No mobile horizontal overflow was observed.
- Development-mode Optimus and Metro film pages also loaded successfully.

Screenshots and the temporary smoke movie are in ignored `output/playwright/`.
Physical mobile devices and an actual remote deployment were not tested.
