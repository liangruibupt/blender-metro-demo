# Metro Atelier / Central & M01

An original island-platform station and single-car metro concept built in Blender,
with a Three.js viewer and a continuous platform-to-train visitor route.
This is a visual design study, not a replica, engineering model, vehicle simulator,
or certified accessibility layout.

## Deliverables

- `deliverables/central-station.blend`: complete station and editable M01 train.
- `deliverables/station-platform.png`, `station-overview.png`: station renders.
- `public/assets/station.glb`: original station environment, composed with the
  separate train GLB in the viewer.
- `scripts/build_station.py`: reproducible station construction script.
- `deliverables/metro-atelier.blend`: editable model, materials, studio lights,
  three cameras, and a 240-frame exterior orbit at 24 fps.
- `deliverables/exterior.png`, `interior.png`, `cab.png`: Blender Cycles renders.
- `public/assets/metro.glb`: portable model with 12 independently sliding door
  leaves and a separately identified roof.
- `scripts/build_metro.py`: reproducible source of the Blender model.
- `src/`: browser viewer with station overview, platform, passenger and driver
  views, bounded walking, detail viewpoints, door animation, roof removal, PNG
  capture, fullscreen and train GLB download.

## Start

```sh
npm ci
npm run dev -- --port 5187
```

Open the URL printed by Vite. Use another port if 5187 is occupied.
The viewer must be served over HTTP, not opened using `file://`.

Overview: drag to orbit, scroll/pinch to zoom. Platform/interior/cab: drag to look around;
WASD, arrow keys, or the on-screen arrows move along a bounded visitor aisle.
The tabs and model markers jump between viewpoints. The cab doorway is open,
so it can also be reached continuously through the passenger aisle.
The boarding marker positions the visitor at the central door; move forward to
board when the doors are open. Only the six platform-facing door leaves open.
Closing is refused while the visitor is in a doorway. Platform, aisle and cab
navigation is continuous; track areas and furniture are not walkable. The exit
stairs are modeled as scenery, not as an explorable upper concourse.
This uses a level, constrained visitor route, not general-purpose physics.

In the 360-degree overview, select station or train using the inspection selector.
The bottom-view button moves below the selected subject. Orbit dragging can also
cross below the horizon. Presentation ground is automatically hidden below the
scene; standalone train inspection also hides the station and the display track
to expose the wheels, bogies and underslung equipment. Returning to an upper
view or a first-person view restores the appropriate environment.

Arrival boards and instrument readouts are static concept graphics, not live
service information or train telemetry.
No external models or image assets are required. An optional Google Fonts CSS
request supplies Barlow; system fonts are used if it is unavailable.

## Python Environment

Use the shared environment for standalone Python utilities:

```sh
/Users/ruiliang/Documents/workspaces/venv/bin/python scripts/check_assets.py
```

Blender's `bpy` is available in Blender's bundled Python, not the shared venv.
Generate the asset with Blender itself:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/build_metro.py -- --render
```

Omit `-- --render` to rebuild the `.blend` and GLB without rendering PNGs.
Do not install `bpy` in the shared virtual environment.

Build the station after the original train exists:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/build_station.py -- --render
```

The station script opens the original train file and writes a separate combined
file; it does not overwrite the standalone train. Run the Python asset check
after both scripts have generated their assets and renders.

## Build

```sh
npm test
npm run build
npm run preview -- --port 4173
```

The app uses relative asset URLs. `vite.config.js` also uses a relative base so
`dist/` can be hosted at a GitHub Pages repository subpath.
No deployment is performed automatically.

## Model Organization

The Blender files separate shell, interior, cab, roof, undercarriage, sliding
doors, track, station, station cover and lights into named collections. Text remains editable in the
Blender original and is converted to mesh only during GLB export.
Coordinates: Blender X = car length, Y = width, Z = up. glTF X = length,
Y = up, Z = negative Blender Y.

Blender materials can be more detailed than glTF materials. The procedural floor
bump is retained in `.blend` but is not baked into the web export.
The viewer batches static geometry by material; editable source objects are
preserved in Blender. All three cameras and the 360-degree orbit live in the
standalone train file; an MP4 is not pre-rendered.
The station vault and near facade are hidden in the architectural overview to
avoid blocking the train. First-person views restore the enclosure; the roof
button removes the train roof only.

## Visual Reference

The island-platform arrangement, repeated piers, vaulted ceiling and departure
boards were informed by [Subway station by Zeps3D on Sketchfab](https://sketchfab.com/3d-models/subway-station-bb68e4b3ac6646d2a59bffa7fa7818aa).
Our geometry, maps, signage, furniture and materials are original procedural
work. No model, texture, thumbnail or other asset from that listing is included
in this repository.

## GitHub

Repository: [liangruibupt/blender-metro-demo](https://github.com/liangruibupt/blender-metro-demo)
(private). Development branch: `codex/metro-demo`.
Pending PR work is on local branch `codex/metro-bottom-view`; `PR_DRAFT.md`
records the intended `main` target and publication prerequisite. No PR has been
created while the repository is awaiting Code Defender approval.

The project is self-contained.
`node_modules`, `dist`, logs, Blender backups and raw browser QA captures are
excluded. Current assets are below GitHub's individual file size limit.
For frequent binary revisions or larger future assets, use Git LFS.
The repository is private; no public deployment is configured.
