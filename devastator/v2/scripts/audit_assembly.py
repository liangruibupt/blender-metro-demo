"""Independent reopening, full-frame checks and exact assembled-pose verification."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembly_motion import SCHEDULE, SECONDARY, control_matrix

ROOT = Path(__file__).resolve().parents[1]
metadata = json.loads((ROOT/"assets/devastator-v2-assembly.json").read_text())
for path, digest in {**metadata["files"], **metadata["sourceInputs"]}.items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
bpy.ops.wm.open_mainfile(filepath=str(ROOT/"deliverables/devastator-v2-assembly.blend"))
scene = bpy.context.scene
settings = metadata["settings"]
meshes = [o for o in bpy.data.collections[metadata["collection"]].objects if o.type == "MESH"]
assert len(meshes) == metadata["animatedMeshes"]
assert sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons) == metadata["triangles"]
assert scene.frame_end == settings["frames"] and scene.render.fps == settings["fps"]
assert scene.camera.name == metadata["camera"]
assert not bpy.data.libraries
assert not [i for i in bpy.data.images if i.source == "FILE" and not i.packed_file]
assert (scene.render.resolution_x, scene.render.resolution_y) == (settings["width"], settings["height"])
assert scene.eevee.taa_render_samples == 64 and scene.eevee.use_raytracing and scene.eevee.use_fast_gi
corners = {o.name: np.array([(*v, 1) for v in o.bound_box]) for o in meshes}
controls = {key: bpy.data.objects[name] for key, name in metadata["controls"].items()}
rest = {key: Matrix(value) for key, value in metadata["restBasis"].items()}
studio = bpy.data.objects["Studio cyclorama (not exported)"]
studio_tree = BVHTree.FromPolygons([studio.matrix_world @ v.co for v in studio.data.vertices],
                                 [tuple(p.vertices) for p in studio.data.polygons], epsilon=.00001)
studio_inner_radius = min((v.co.x**2+v.co.y**2)**.5 for v in studio.data.vertices if v.co.xy.length > 1)
positions, minimum_floor, max_motion_error = [], float("inf"), 0
for frame in range(1, settings["frames"]+1):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    world = np.concatenate([corners[o.name] @ np.array(o.matrix_world).T for o in meshes])
    camera = scene.camera
    assert camera.matrix_world.translation.xy.length < studio_inner_radius, "Camera outside cyclorama"
    projection = camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),
                                          x=settings["width"], y=settings["height"])
    clip = world @ np.array(projection @ camera.matrix_world.inverted()).T
    normalized = clip[:, :2]/clip[:, 3:4]*.5+.5
    low, high = normalized.min(axis=0), normalized.max(axis=0)
    assert np.all(clip[:, 3] > .1)
    assert np.all(low > .025) and np.all(high < .975), (frame, low.tolist(), high.tolist())
    for key, control in controls.items():
        expected = control_matrix(key, rest[key], (frame-1)/settings["fps"])
        error = float(np.abs(np.array(control.matrix_basis)-np.array(expected)).max())
        max_motion_error = max(max_motion_error, error)
        assert error < .0001, (frame, key, error)
        assert all(abs(v-1) < .00001 for v in control.scale), "Scaling geometry is prohibited"
    moving = [o for o in meshes if o["motionKey"] != "STATIC"]
    floor = min(float((corners[o.name] @ np.array(o.matrix_world).T)[:, 2].min()) for o in moving)
    minimum_floor = min(minimum_floor, floor)
    assert floor > -.01, (frame, "Sculpture below floor", floor)
    view = camera.data.view_frame(scene=scene)
    for u in [0, .5, 1]:
        for v in [0, .5, 1]:
            local = view[0].lerp(view[1], u).lerp(view[3].lerp(view[2], u), v)
            ray = (camera.matrix_world.to_3x3() @ local).normalized()
            assert studio_tree.ray_cast(camera.matrix_world.translation, ray)[0] is not None, (frame, u, v)
    positions.append({"frame": frame, "minX": float(low[0]), "maxX": float(high[0]),
                      "minY": float(low[1]), "maxY": float(high[1])})

max_final_error = 0
groups = {}
for obj in meshes:
    spec = metadata["bindGeometry"][obj.name]
    assert len(obj.data.vertices) == spec["vertices"]
    assert obj.material_slots[0].material.name == spec["material"]
    assert all(math.isfinite(v) for row in obj.matrix_world for v in row)
    for vertex in obj.data.vertices:
        max_final_error = max(max_final_error, (obj.matrix_world @ vertex.co-vertex.co).length)
    vertices, faces = groups.setdefault(obj["assembly"], ([], []))
    offset = len(vertices)
    vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
    faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
assert max_final_error < .0001, max_final_error
trees = {key: BVHTree.FromPolygons(v, f) for key, (v, f) in groups.items()}
pairs = [("03 Recessed helmet", "06 Raised crushing arm"),
         ("03 Recessed helmet", "08 Long armored cannon"),
         ("08 Long armored cannon", "09 Loader leg"), ("08 Long armored cannon", "10 Mixer leg")]
for a, b in pairs:
    assert not trees[a].overlap(trees[b]), (a, b)
report = {
    "status": "PASS", "framesChecked": len(positions), "framing": positions,
    "triangles": metadata["triangles"], "animatedMeshes": len(meshes),
    "controls": len(controls), "studioRays": len(positions)*9,
    "minimumSculptureBoundingZ": minimum_floor, "maxControlMatrixError": max_motion_error,
    "maxFinalVertexError": max_final_error, "finalSurfacePairs": pairs,
    "checkedFiles": {**metadata["files"], **metadata["sourceInputs"]},
    "limits": ["Not a swept-volume collision certification", "Modules are not independent vehicle forms",
               "All-frame bounding checks and final-pose surface checks require sampled visual QA"],
}
(ROOT/"qa/assembly-scene-audit.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps({k: v for k, v in report.items() if k not in {"framing", "checkedFiles"}}, indent=2))
