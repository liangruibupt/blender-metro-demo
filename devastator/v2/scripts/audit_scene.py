"""Reopen V2 and verify exports, contacts, cameras and selected clearances."""
import hashlib
import json
import math
from pathlib import Path
import struct

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
metadata = json.loads((ROOT/"assets/devastator-v2.json").read_text())
for path, digest in metadata["files"].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
assert set(metadata["renderedViews"]) == {"hero", "front", "rear", "detail"}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/"deliverables/devastator-v2.blend"))
scene = bpy.context.scene
objects = list(bpy.data.collections[metadata["collection"]].objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
assert not any(obj.animation_data for obj in objects), "The sculpture must remain rigid during the orbit"
assert len(meshes) == metadata["sourceMeshes"]
assert scene.camera.name == metadata["cameras"]["hero"]
assert not bpy.data.libraries, "Scene should have no linked external library"
assert not [image for image in bpy.data.images if image.source == "FILE" and not image.packed_file]
for obj in meshes:
    assert obj.material_slots and obj.material_slots[0].material, obj.name
    assert all(math.isfinite(v) for row in obj.matrix_world for v in row), obj.name

contacts = []
for foot in metadata["feet"]:
    obj = bpy.data.objects[foot["name"]]
    lowest = min((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)
    assert abs(lowest-foot["ground"]) < .002, foot
    if foot["ground"] > 0:
        slab = bpy.data.objects["Raised mixer contact slab"]
        for corner in obj.bound_box:
            local = slab.matrix_world.inverted() @ obj.matrix_world @ Vector(corner)
            assert abs(local.x) < 2.23/2 and abs(local.y) < 2.98/2, "Unsupported foot corner"
    contacts.append({"name": obj.name, "z": lowest, "target": foot["ground"]})


world_corners = np.array([(*tuple(obj.matrix_world @ Vector(corner)), 1)
                         for obj in meshes for corner in obj.bound_box])


def frame_extent(camera):
    projection = camera.calc_matrix_camera(
        bpy.context.evaluated_depsgraph_get(), x=scene.render.resolution_x, y=scene.render.resolution_y)
    clip = world_corners @ np.array(projection @ camera.matrix_world.inverted()).T
    normalized = clip[:, :2]/clip[:, 3:4]*.5+.5
    extent = {"minX": float(normalized[:, 0].min()), "maxX": float(normalized[:, 0].max()),
              "minY": float(normalized[:, 1].min()), "maxY": float(normalized[:, 1].max())}
    assert np.all(clip[:, 3] > camera.data.clip_start)
    assert .02 < extent["minX"] < extent["maxX"] < .98, extent
    assert .02 < extent["minY"] < extent["maxY"] < .98, extent
    return extent


presets = {}
for view in ["hero", "front", "rear"]:
    camera = bpy.data.objects[metadata["cameras"][view]]
    assert camera.data.type == "PERSP"
    presets[view] = frame_extent(camera)
    extent = presets[view]
    assert abs((extent["minX"]+extent["maxX"])/2-.5) < .06, (view, extent)
    assert abs((extent["minY"]+extent["maxY"])/2-.5) < .06, (view, extent)
hero = bpy.data.objects[metadata["cameras"]["hero"]]
direction = hero.matrix_world.to_quaternion() @ Vector((0, 0, 1))
azimuth = math.degrees(math.atan2(direction.x, -direction.y))
assert 38 < azimuth < 44, azimuth
assert abs(azimuth-metadata["heroAzimuthDegrees"]) < .001

studio = bpy.data.objects[metadata["studio"]]
assert studio not in objects, "Studio must not be part of the exported sculpture"
topology = bmesh.new()
topology.from_mesh(studio.data)
boundary = [edge for edge in topology.edges if edge.is_boundary]
assert len(boundary) == 128, "Unexpected studio opening"
assert all(abs(vertex.co.z-45) < .00001 for edge in boundary for vertex in edge.verts)
assert all(edge.is_manifold or edge.is_boundary for edge in topology.edges)
topology.free()
# Axis-aligned rays can land exactly on shared triangle edges at quarter turns.
studio_tree = BVHTree.FromPolygons(
    [studio.matrix_world @ v.co for v in studio.data.vertices],
    [tuple(face.vertices) for face in studio.data.polygons], epsilon=.00001)


def check_background(camera):
    corners = camera.data.view_frame(scene=scene)
    for u in [0, .5, 1]:
        for v in [0, .5, 1]:
            local = corners[0].lerp(corners[1], u).lerp(corners[3].lerp(corners[2], u), v)
            ray = (camera.matrix_world.to_3x3() @ local).normalized()
            hit, _, _, _ = studio_tree.ray_cast(camera.matrix_world.translation, ray)
            assert hit is not None, f"Studio gap: {camera.name}, frame {scene.frame_current}, sample {(u, v)}"


for name in metadata["cameras"].values():
    check_background(bpy.data.objects[name])
orbit = bpy.data.objects["V2 Turntable orbit"]
assert orbit.animation_data and orbit.animation_data.action
camera = bpy.data.objects[metadata["orbitCamera"]]
samples, positions = [], []
static_resolution = (scene.render.resolution_x, scene.render.resolution_y)
scene.render.resolution_x = metadata["turntableSettings"]["width"]
scene.render.resolution_y = metadata["turntableSettings"]["height"]
assert scene.frame_end == metadata["turntableSettings"]["frames"]
for frame in range(1, metadata["turntableSettings"]["loopFrame"]+1):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    positions.append(camera.matrix_world.translation.copy())
    samples.append({"frame": frame, **frame_extent(camera)})
    check_background(camera)
assert (positions[0]-positions[metadata["turntableSettings"]["frames"]//2]).length > 60
assert (positions[0]-positions[-1]).length < .001
scene.render.resolution_x, scene.render.resolution_y = static_resolution
for view in metadata["renderedViews"]:
    path = ROOT/f"deliverables/devastator-v2-{view}.png"
    image = path.read_bytes()
    assert image[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack_from(">II", image, 16)
    assert (width, height) == (metadata["renderSettings"]["width"], metadata["renderSettings"]["height"])

binary = (ROOT/"assets/devastator-v2.glb").read_bytes()
magic, version, total = struct.unpack_from("<III", binary)
assert magic == 0x46546C67 and version == 2 and total == len(binary)
size, kind = struct.unpack_from("<II", binary, 12)
assert kind == 0x4E4F534A
gltf = json.loads(binary[20:20+size])
assert len(gltf["meshes"]) == metadata["browserMeshes"]
assert not gltf.get("images") and not gltf.get("animations")
for material in gltf["materials"]:
    color = material["pbrMetallicRoughness"]["baseColorFactor"]
    assert max(color[:3])-min(color[:3]) < .00001

import_scene = bpy.data.scenes.new("Independent GLB import check")
bpy.context.window.scene = import_scene
bpy.ops.import_scene.gltf(filepath=str(ROOT/"assets/devastator-v2.glb"))
bpy.context.view_layer.update()
imported = [obj for obj in import_scene.objects if obj.type == "MESH"]
assert len(imported) == metadata["browserMeshes"]
assert sum(len(p.vertices)-2 for obj in imported for p in obj.data.polygons) == metadata["triangles"]
points = [obj.matrix_world @ v.co for obj in imported for v in obj.data.vertices]
for key, operation in [("min", min), ("max", max)]:
    assert all(abs(operation(v[i] for v in points)-metadata["bounds"][key][i]) < .002 for i in range(3))

groups = {}
for obj in imported:
    vertices, faces = groups.setdefault(obj["assembly"], ([], []))
    offset = len(vertices)
    vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
    faces.extend(tuple(offset+i for i in face.vertices) for face in obj.data.polygons)
trees = {label: BVHTree.FromPolygons(vertices, faces) for label, (vertices, faces) in groups.items()}
pairs = [("03 Recessed helmet", "06 Raised crushing arm"),
         ("03 Recessed helmet", "08 Long armored cannon"),
         ("08 Long armored cannon", "09 Loader leg"),
         ("08 Long armored cannon", "10 Mixer leg")]
for a, b in pairs:
    assert not trees[a].overlap(trees[b]), f"Selected surface intersection: {a} / {b}"
report = {
    "status": "PASS", "sourceMeshes": len(meshes), "browserMeshes": len(imported),
    "triangles": metadata["triangles"], "footContacts": contacts,
    "cameraPresets": presets, "orbitSamples": samples, "checkedSurfacePairs": pairs,
    "heroAzimuthDegrees": azimuth, "studioRayChecks": 9*(len(metadata["cameras"])+len(samples)),
    "studioRayTolerance": .00001, "studioBoundary": "Top rim only; no internal open edges",
    "checkedFiles": metadata["files"],
    "limits": ["Not an exhaustive collision or containment check",
               "No physical transformation or independent vehicle form is implemented",
               "Reference similarity requires visual judgement, not object-count metrics"],
}
(ROOT/"qa").mkdir(exist_ok=True)
(ROOT/"qa/scene-audit.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps({"status": "PASS", "presets": len(presets), "orbitSamples": len(samples),
                  "clearancePairs": len(pairs), "footContacts": contacts}))
