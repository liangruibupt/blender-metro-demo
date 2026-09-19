"""Check the four established non-joint surface pairs at every animation frame."""
import hashlib
import json
from pathlib import Path

import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT/"assets/devastator-v2-assembly.json").read_text())
relative = "deliverables/devastator-v2-assembly.blend"
digest = hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
assert digest == manifest["files"][relative]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/relative))
scene = bpy.context.scene
pairs = [("03 Recessed helmet", "06 Raised crushing arm"),
         ("03 Recessed helmet", "08 Long armored cannon"),
         ("08 Long armored cannon", "09 Loader leg"),
         ("08 Long armored cannon", "10 Mixer leg")]
labels = {key for pair in pairs for key in pair}
groups = {}
for obj in bpy.data.collections[manifest["collection"]].objects:
    if obj.type == "MESH" and obj["assembly"] in labels:
        vertices = np.array([(*v.co, 1) for v in obj.data.vertices])
        corners = np.array([(*v, 1) for v in obj.bound_box])
        groups.setdefault(obj["assembly"], []).append((obj, vertices, corners))
faces = {}
for label, objects in groups.items():
    polygons, offset = [], 0
    for obj, vertices, _ in objects:
        polygons.extend(tuple(offset+i for i in polygon.vertices) for polygon in obj.data.polygons)
        offset += len(vertices)
    faces[label] = polygons
cache = {}
tested, broad_phase = 0, 0
for frame in range(1, manifest["settings"]["frames"]+1):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    bounds = {}
    for label, objects in groups.items():
        corners = np.concatenate([local @ np.array(obj.matrix_world).T for obj, _, local in objects])
        bounds[label] = (corners[:, :3].min(axis=0), corners[:, :3].max(axis=0))
    for a, b in pairs:
        low_a, high_a = bounds[a]
        low_b, high_b = bounds[b]
        if np.any(high_a < low_b) or np.any(high_b < low_a):
            broad_phase += 1
            continue
        for label in (a, b):
            objects = groups[label]
            key = tuple(tuple(value for row in obj.matrix_world for value in row) for obj, _, _ in objects)
            if label not in cache or cache[label][0] != key:
                points = np.concatenate([vertices @ np.array(obj.matrix_world).T
                                         for obj, vertices, _ in objects])
                cache[label] = (key, BVHTree.FromPolygons(points[:, :3].tolist(), faces[label]))
        overlap = cache[a][1].overlap(cache[b][1])
        assert not overlap, (frame, a, b, len(overlap))
        tested += 1
    if frame % 72 == 0:
        print(json.dumps({"frame": frame, "surfaceTests": tested, "boundsSeparated": broad_phase}), flush=True)
report = {
    "status": "PASS", "framesChecked": manifest["settings"]["frames"], "pairs": pairs,
    "pairFrameChecks": tested+broad_phase, "surfaceTests": tested,
    "boundsSeparated": broad_phase, "sceneSHA256": digest,
    "scriptSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "limits": ["Only the four named pairs; joints, containment and other pairs are excluded",
               "Per-frame surface checks are not continuous swept-volume collision certification"],
}
(ROOT/"qa/assembly-motion-clearance.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2))
