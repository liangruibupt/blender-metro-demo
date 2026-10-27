# Mechanical Atelier

**English** | [简体中文](README.zh-CN.md)

Three independent Blender studies in one repository: a metro station and train,
an Optimus Prime fan study, and a Devastator clay sculpture. Metro and Optimus
also have Three.js viewers. Each task owns its pages, JavaScript, styles, source
assets, Blender scripts, deliverables and documentation. Dependencies and
deployment remain shared at the repository root.

## Tasks

| Task | Interactive entry | Video | Documentation |
| --- | --- | --- | --- |
| Metro / Central & M01 | [metro/index.html](metro/index.html) | [metro/watch.html](metro/watch.html) | [Metro README](metro/README.md) |
| Optimus Prime / Metal V3 | [optimus/index.html](optimus/index.html) | [optimus/watch.html](optimus/watch.html) | [Optimus README](optimus/README.md) |
| Devastator / Clay V2 | — (Blender + GLB only) | [360° turntable](devastator/v2/deliverables/devastator-v2-360.mp4) · [18 s assembly](devastator/v2/deliverables/devastator-v2-assembly.mp4) | [Devastator README](devastator/README.md) |

## Gallery

Screenshots live in `docs/screenshots/`: downscaled copies of each task's
Blender renders and video contact sheets, plus captures of the Three.js viewers.
Full-resolution renders are in each task's `deliverables/` directory.

### Metro / Central & M01

An original island-platform station and single-car M01 metro (Cycles renders).

| Station overview | Platform | Train exterior |
| --- | --- | --- |
| ![Metro station overview](docs/screenshots/metro-station-overview.jpg) | ![Metro station platform](docs/screenshots/metro-station-platform.jpg) | ![Metro train exterior](docs/screenshots/metro-exterior.jpg) |
| **Passenger interior** | **Driver cab** | |
| ![Metro train interior](docs/screenshots/metro-interior.jpg) | ![Metro driver cab](docs/screenshots/metro-cab.jpg) | |

Interactive viewer ([metro/index.html](metro/index.html), Three.js):

| Platform view | 360° overview |
| --- | --- |
| ![Metro viewer platform view](docs/screenshots/ui-metro-platform.jpg) | ![Metro viewer 360 overview](docs/screenshots/ui-metro-overview.jpg) |
| **Passenger cabin** | **Driver cab** |
| ![Metro viewer passenger cabin](docs/screenshots/ui-metro-cabin.jpg) | ![Metro viewer driver cab](docs/screenshots/ui-metro-cab.jpg) |

Video: [80-second storyboard preview](metro/deliverables/metro-storyboard-preview.mp4)

### Optimus Prime / Metal V3

A G1-inspired fan study. The robot and the cab-over truck share one articulated
mesh set.

| Robot mode | Truck mode |
| --- | --- |
| ![Optimus robot mode](docs/screenshots/optimus-robot.jpg) | ![Optimus truck mode](docs/screenshots/optimus-truck.jpg) |

Interactive viewer ([optimus/index.html](optimus/index.html), Three.js):

| 360° showcase | Exploded view | Truck mode |
| --- | --- | --- |
| ![Optimus viewer 360 showcase](docs/screenshots/ui-optimus.jpg) | ![Optimus viewer exploded view](docs/screenshots/ui-optimus-exploded.jpg) | ![Optimus viewer truck mode](docs/screenshots/ui-optimus-truck.jpg) |

Video: [80-second transformation showcase](optimus/deliverables/optimus-showcase.mp4)

### Devastator / Clay V2

A combined-form clay sculpture: 610,432 triangles, rendered in Cycles at 1600 × 1200.
There is no Three.js viewer for this task.

| Hero | Front | Rear |
| --- | --- | --- |
| ![Devastator hero view](docs/screenshots/devastator-hero.jpg) | ![Devastator front view](docs/screenshots/devastator-front.jpg) | ![Devastator rear view](docs/screenshots/devastator-rear.jpg) |

![Devastator upper-body detail](docs/screenshots/devastator-detail.jpg)

| 360° turntable (12 decoded frames) | 18 s assembly (decoded frames) |
| --- | --- |
| ![Devastator 360 turntable contact sheet](docs/screenshots/devastator-360-sheet.jpg) | ![Devastator assembly contact sheet](docs/screenshots/devastator-assembly-sheet.jpg) |

Videos: [12-second 360° turntable](devastator/v2/deliverables/devastator-v2-360.mp4) ·
[18-second modular assembly](devastator/v2/deliverables/devastator-v2-assembly.mp4)

## Layout

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
devastator/
  README.md, REFERENCE.md
  references/            user-supplied reference images and video
  v2/
    scripts/, assets/, deliverables/, qa/
    README.md, ASSEMBLY.md, QA.md, PROMPTS.md, MCP_SETUP.md
docs/screenshots/        README gallery images
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

Devastator is Blender-only (no Three.js page or `npm` tests). Its build,
render and audit steps are documented in
[devastator/v2/README.md](devastator/v2/README.md) and
[devastator/v2/ASSEMBLY.md](devastator/v2/ASSEMBLY.md), for example:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python-exit-code 1 --python devastator/v2/scripts/build_assembly.py
```

Each script derives its own task directory from its file location and writes
only to that task's `assets/` and `deliverables/`. Regenerating a model does not
regenerate its MP4; export the corresponding movie again when model geometry
or animation changes.
