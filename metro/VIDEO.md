# Metro Storyboard Preview

## Delivery

- `deliverables/metro-storyboard-preview.mp4`: 1920 x 1080, 24 fps, 80 seconds.
- `watch.html`: standard MP4 playback, without WebGL, Three.js or WebCodecs.
- `film.html`: local playback, timeline scrubbing and deterministic MP4 export.
- `src/film-timeline.js`: camera poses, train movement, doors and shot boundaries.
- `src/film-scene.js`: the film-only scene assembled from the Blender GLB assets.

The preview is silent. No stock footage, licensed music or external visual
assets are used. The video is rendered from the existing Blender-exported
models through Three.js; it is not a screen recording of manual mouse actions.
WebCodecs encoding advances at exactly 1/24 second per frame, independent of
the wall-clock time required to render and encode.

## Shot List

| Time | Shot |
| --- | --- |
| 00:00-00:12 | Train enters from the rear tunnel, decelerates and stops; platform doors open. |
| 00:12-00:24 | Complete 360-degree station overview, with roof and perimeter walls removed for visibility. |
| 00:24-00:36 | Complete 360-degree train presentation. |
| 00:36-00:42 | Continuous approach toward the rear end door; station context returns. |
| 00:42-00:45 | Camera passes through the open rear end door. |
| 00:45-00:54 | Forward travel along the passenger saloon aisle. |
| 00:54-01:00 | Enter the driver cab and inspect its instruments. |
| 01:00-01:07 | Exit the cab through its original doorway, then leave via a platform-side passenger door. |
| 01:07-01:20 | Platform doors close, train accelerates out of the station, then fade out. |

## Scene Variant

Only the film scene replaces the solid rear bulkhead with a framed opening and
an animated sliding end door. The movie's door-status display follows the door
animation. The original `.blend` and `.glb` files, and the
interactive inspection viewer, are not modified. The train and wheels move as
one vehicle; rails remain stationary. Tunnel clipping prevents the train from
appearing outside the station's modeled portals.

Station-to-train inspection uses a cut at 00:24. From the train orbit through
the cab exit, camera position and orientation remain continuous. Station
geometry fades back in during the rear approach; the roof is restored only
after the camera has descended into the station.

## Reproduce

Run these commands from the repository root.

```sh
npm ci
npm run dev -- --port 5187
```

Open `http://127.0.0.1:5187/metro/film.html`. Use the timeline to inspect a frame, or
the export button to produce the MP4. Export requires a browser with WebCodecs
H.264 encoding, such as a supported version of Chrome on this Mac.

For ordinary viewing, open `watch.html` or the MP4 directly. The live `film.html`
scene must be served over HTTP. Encoder dependencies load only when exporting;
startup errors and long loading times show a retry state rather than an endless
loading message. Production playback uses `npm run build` followed by
`npm run preview -- --port 5190`, avoiding Vite development dependency caches.

Tests: `npm test`. The timeline tests verify full orbits, stationary boarding,
rear-door opening, continuous camera transforms and doorway clearance.
