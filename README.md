# Mechanical Atelier

Two independent Blender and Three.js studies in one repository. Each task owns
its pages, JavaScript, styles, source assets, Blender scripts, deliverables and
documentation. Dependencies and deployment remain shared at the repository root.

## Tasks

| Task | Interactive entry | Video | Documentation |
| --- | --- | --- | --- |
| Metro / Central & M01 | [metro/index.html](metro/index.html) | [metro/watch.html](metro/watch.html) | [Metro README](metro/README.md) |
| Optimus Prime / Metal V3 | [optimus/index.html](optimus/index.html) | [optimus/watch.html](optimus/watch.html) | [Optimus README](optimus/README.md) |

```text
metro/
  index.html, film.html, watch.html
  src/
  assets/
  scripts/
  deliverables/
  README.md, QA.md, VIDEO.md, PR_DRAFT.md
optimus/
  index.html, watch.html
  src/
  assets/
  scripts/
  deliverables/
  README.md, QA.md
public/favicon.svg
scripts/check_deployment.mjs
tests/layout.test.js
package.json, package-lock.json, vite.config.js
```

Root HTML files are compatibility redirects only, not duplicate applications.
The root page still opens Metro. Existing `/film.html`, `/watch.html`,
`/optimus.html` and `/optimus-watch.html` links redirect to their new task pages,
preserving query strings and fragments when JavaScript is enabled.

## Develop

Run commands from the repository root:

```sh
npm ci
npm run dev -- --port 5193
```

Open `http://127.0.0.1:5193/metro/` or
`http://127.0.0.1:5193/optimus/`. Pick another port if needed.
The interactive pages require HTTP and WebGL; native video pages do not require
WebGL. Do not open the interactive HTML files directly with `file://`.

## Build and Verify

```sh
npm test
npm run build
npm run verify:deploy
npm run preview -- --port 5193
```

Task-only tests are available as `npm run test:metro` and `npm run test:optimus`.
The deployment check verifies all ten page entries, every manifest-referenced
chunk, CSS file and asset, and the hashes of the runtime models, rig data,
movies and video posters.

Publish the entire contents of `dist/` without flattening its directories.
The build uses relative URLs, so it can be hosted at a domain root or at a
repository subpath such as `/blender-metro-demo/`. No SPA fallback or route
rewrite is required. The two task directories in `dist/` contain their pages;
Vite places their shared and fingerprinted runtime files in `dist/assets/`.
Directory organization in Git is independent of this generated asset layout.

The host must serve MP4 as `video/mp4` and support HTTP byte-range requests
(`206 Partial Content`) for reliable seeking. A basic server that ignores Range
may play a video but reset it to the beginning when seeking.

Check a running preview or an already deployed site with its directory URL:

```sh
npm run verify:deploy -- --url http://127.0.0.1:5193/
npm run verify:deploy -- --url https://example.com/blender-metro-demo/
```

This additionally checks every emitted file over HTTP and both video range
responses. It does not publish anything or change the remote site.

Blender `.blend` source files, build scripts and documentation remain in Git;
they are not copied into the deployed website. Browser model downloads use the
GLB assets emitted by Vite. Native video pages include the existing MP4 files.
Old fingerprinted asset URLs are not permanent APIs; legacy HTML page URLs are
retained as redirects.

No remote deployment is performed automatically. Use the repository's approved
publishing workflow and deploy only after the checks above pass.

## Blender Assets

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python metro/scripts/build_metro.py -- --render
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python metro/scripts/build_station.py -- --render
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python optimus/scripts/build_optimus.py -- --render
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python optimus/scripts/audit_motion.py
python3 metro/scripts/check_assets.py
```

Each script derives its own task directory from its file location and writes
only to that task's `assets/` and `deliverables/`. Regenerating a model does not
regenerate its MP4; export the corresponding movie again when model geometry
or animation changes.
