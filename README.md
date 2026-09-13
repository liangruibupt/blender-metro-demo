# Metro Atelier / M01

An original single-car metro concept built in Blender, with a Three.js viewer.
This is a visual design study, not a replica, engineering model, vehicle simulator,
or certified accessibility layout.

## Deliverables

- `deliverables/metro-atelier.blend`: editable model, materials, studio lights,
  three cameras, and a 240-frame exterior orbit at 24 fps.
- `deliverables/exterior.png`, `interior.png`, `cab.png`: Blender Cycles renders.
- `public/assets/metro.glb`: portable model with 12 independently sliding door
  leaves and a separately identified roof.
- `scripts/build_metro.py`: reproducible source of the Blender model.
- `src/`: browser viewer with exterior orbit, passenger and driver views,
  bounded walking, detail viewpoints, door animation, roof removal, PNG capture,
  fullscreen and GLB download.

## Start

```sh
npm ci
npm run dev -- --port 5187
```

Open the URL printed by Vite. Use another port if 5187 is occupied.
The viewer must be served over HTTP, not opened using `file://`.

Exterior: drag to orbit, scroll/pinch to zoom. Interior/cab: drag to look around;
WASD, arrow keys, or the on-screen arrows move along a bounded visitor aisle.
The tabs and model markers jump between viewpoints. The cab doorway is open,
so it can also be reached continuously through the passenger aisle.
First-person movement deliberately stays inside the vehicle, even when side
doors are open. It is not a general-purpose collision or walking simulator.

Instrument readouts are static concept graphics, not live train telemetry.
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

## Build

```sh
npm run build
npm run preview -- --port 4173
```

The app uses relative asset URLs. `vite.config.js` also uses a relative base so
`dist/` can be hosted at a GitHub Pages repository subpath.
No deployment is performed automatically.

## Model Organization

The Blender file separates shell, interior, cab, roof, undercarriage, sliding
doors, track and studio into named collections. Text remains editable in the
Blender original and is converted to mesh only during GLB export.
Coordinates: Blender X = car length, Y = width, Z = up. glTF X = length,
Y = up, Z = negative Blender Y.

Blender materials can be more detailed than glTF materials. The procedural floor
bump is retained in `.blend` but is not baked into the web export.
The viewer batches static geometry by material; editable source objects are
preserved in Blender. All three cameras and the 360-degree orbit live in the
Blender file; an MP4 is not pre-rendered.

## GitHub

The project is self-contained and ready to push to a user-selected repository.
`node_modules`, `dist`, logs, Blender backups and raw browser QA captures are
excluded. Current assets are below GitHub's individual file size limit.
For frequent binary revisions or larger future assets, use Git LFS.
No remote or repository visibility should be inferred without confirmation.
