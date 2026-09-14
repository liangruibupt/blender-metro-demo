"""Check the saved scene, export integrity, foot contact and turntable framing."""

import hashlib
import json
import math
from pathlib import Path
import struct

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
metadata = json.loads((ROOT / "assets/devastator.json").read_text())
for name, expected in metadata["files"].items():
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert actual == expected, f"Stale asset/source: {name}"

bpy.ops.wm.open_mainfile(filepath=str(ROOT / "deliverables/devastator-clay.blend"))
scene = bpy.context.scene
collection = bpy.data.collections["DEVASTATOR | Editable mechanical assemblies"]
objects = list(collection.objects)
meshes = [o for o in objects if o.type == "MESH"]
assert len(meshes) == metadata["sourceMeshCount"]
assert scene.camera.name == "Inspection camera"
assert scene.camera.animation_data is None
for obj in meshes:
    assert obj.material_slots and obj.material_slots[0].material, obj.name
    assert all(math.isfinite(v) for row in obj.matrix_world for v in row), obj.name
    assert len(obj.data.vertices) and len(obj.data.polygons), obj.name

feet = {}
for obj in meshes:
    if obj.name.startswith("Foot structural sole"):
        minimum = min((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)
        feet[obj.name] = minimum
        assert abs(minimum+.315) < .002, f"Foot contact: {obj.name}: {minimum}"
assert len(feet) == 2

orbit = bpy.data.objects["Turntable orbit"]
camera = bpy.data.objects[metadata["animation"]["camera"]]
assert orbit.animation_data and orbit.animation_data.action
samples = []
positions = []
for frame in range(1, 242, 10):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    positions.append(list(camera.matrix_world.translation))
    points = [world_to_camera_view(scene, camera, obj.matrix_world @ Vector(c))
              for obj in meshes for c in obj.bound_box]
    extents = {
        "minX": min(p.x for p in points), "maxX": max(p.x for p in points),
        "minY": min(p.y for p in points), "maxY": max(p.y for p in points),
        "minDepth": min(p.z for p in points),
    }
    assert .025 < extents["minX"] < extents["maxX"] < .975, (frame, extents)
    assert .025 < extents["minY"] < extents["maxY"] < .975, (frame, extents)
    assert extents["minDepth"] > camera.data.clip_start, (frame, extents)
    samples.append({"frame": frame, **extents})
assert (Vector(positions[0])-Vector(positions[12])).length > 40
assert (Vector(positions[0])-Vector(positions[-1])).length < .001

binary = (ROOT / "assets/devastator.glb").read_bytes()
magic, version, length = struct.unpack_from("<III", binary)
assert magic == 0x46546C67 and version == 2 and length == len(binary)
size, kind = struct.unpack_from("<II", binary, 12)
assert kind == 0x4E4F534A
gltf = json.loads(binary[20:20+size])
assert len(gltf["meshes"]) == metadata["browserMeshCount"]
assert not gltf.get("images"), "Unexpected external or embedded reference images"
assert not gltf.get("animations"), "Static export must not imply transformation"
labels = {n.get("extras", {}).get("assembly") for n in gltf["nodes"]}
assert set(metadata["assemblies"]) <= labels
for material in gltf["materials"]:
    color = material["pbrMetallicRoughness"]["baseColorFactor"]
    assert max(color[:3])-min(color[:3]) < 1e-6, "V1 must remain grayscale"

renders = {}
for name in metadata["renderViews"]:
    relative = f"deliverables/devastator-{name}.png"
    assert relative in metadata["files"], f"Unverified render: {name}"
    image = (ROOT / relative).read_bytes()
    assert image[:8] == b"\x89PNG\r\n\x1a\n", relative
    width, height = struct.unpack_from(">II", image, 16)
    assert width == height == metadata["renderSettings"]["resolution"], relative
    renders[name] = {"width": width, "height": height}

# Independently import the exported GLB to check coordinate/geometry preservation.
source_bounds = metadata["boundsBlender"]
import_scene = bpy.data.scenes.new("Temporary GLB verification")
bpy.context.window.scene = import_scene
bpy.ops.import_scene.gltf(filepath=str(ROOT / "assets/devastator.glb"))
bpy.context.view_layer.update()
imported = [o for o in import_scene.objects if o.type == "MESH"]
assert len(imported) == metadata["browserMeshCount"]
points = [o.matrix_world @ Vector(c) for o in imported for c in o.bound_box]
imported_bounds = {
    "min": [min(p[i] for p in points) for i in range(3)],
    "max": [max(p[i] for p in points) for i in range(3)],
}
for key in ["min", "max"]:
    for a, b in zip(imported_bounds[key], source_bounds[key]):
        assert abs(a-b) < .025, f"Export extent mismatch: {key}: {a} vs {b}"
imported_triangles = sum(len(p.vertices)-2 for o in imported for p in o.data.polygons)
assert imported_triangles == metadata["triangles"]

report = {
    "status": "PASS", "sourceMeshes": len(meshes),
    "browserMeshes": len(gltf["meshes"]), "assemblies": len(metadata["assemblies"]),
    "footContactZ": feet, "turntableSamples": samples,
    "renders": renders, "reimportedTriangles": imported_triangles,
    "reimportedBounds": imported_bounds,
    "checkedFiles": metadata["files"],
    "limitations": [
        "No exhaustive collision or physical transformation validation",
        "Orbit framing sampled every 10 frames, not a swept-volume proof",
        "Independent vehicle forms and final paint are outside this study",
    ],
}
(ROOT / "qa").mkdir(exist_ok=True)
(ROOT / "qa/scene-audit.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps({"status": report["status"], "sourceMeshes": len(meshes),
                  "browserMeshes": len(gltf["meshes"]), "samples": len(samples)}))
