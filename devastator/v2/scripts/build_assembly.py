"""Build an animated evaluated copy without modifying the accepted V2 sculpture."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembly_motion import (BEATS, CAMERA, COLLECTION, FRAMES, FPS, SCHEDULE,
                             SECONDARY, SETTINGS, camera_matrix, control_matrix, linear_keys)

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT/"assets/devastator-v2.json").read_text())
for path, digest in source["files"].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
bpy.ops.wm.open_mainfile(filepath=str(ROOT/"deliverables/devastator-v2.blend"))
scene = bpy.context.scene
scene.frame_set(1)
studio = bpy.data.objects["Studio cyclorama (not exported)"]
for vertex in studio.data.vertices:
    radius = (vertex.co.x**2+vertex.co.y**2)**.5
    if radius > 1:
        vertex.co.x *= (radius+25)/radius
        vertex.co.y *= (radius+25)/radius
studio.data.update()
original = bpy.data.collections[source["collection"]]
objects = list(original.objects)
graph = bpy.context.evaluated_depsgraph_get()
rest_world = {key: bpy.data.objects[key].matrix_world.copy() for key in SCHEDULE}
secondary_objects = {}
for obj in objects:
    label = obj.get("assembly", "")
    if obj.type == "EMPTY" and obj.name.startswith("Bent elbow"):
        key = label+" / elbow"
        secondary_objects[obj] = key
        rest_world[key] = obj.matrix_world.copy()
    if obj.type == "EMPTY" and obj.name == "Folded telescopic crane":
        key = label+" / boom"
        secondary_objects[obj] = key
        rest_world[key] = obj.matrix_world.copy()
assert set(secondary_objects.values()) == set(SECONDARY)

collection = bpy.data.collections.new(COLLECTION)
scene.collection.children.link(collection)
controls, rest_basis = {}, {}
for key in [*SCHEDULE, *SECONDARY]:
    control = bpy.data.objects.new("Assemble | "+key, None)
    collection.objects.link(control)
    control.empty_display_size = .3
    control["motionKey"] = key
    if key in SECONDARY:
        parent = controls[SECONDARY[key][0]]
        control.parent = parent
        rest_basis[key] = rest_world[SECONDARY[key][0]].inverted() @ rest_world[key]
    else:
        rest_basis[key] = rest_world[key].copy()
    control.matrix_basis = rest_basis[key]
    control.rotation_mode = "QUATERNION"
    controls[key] = control
bpy.context.view_layer.update()

buckets = {}
source_triangles = 0
source_meshes = 0
for obj in objects:
    if obj.type not in {"MESH", "CURVE"}:
        continue
    source_meshes += obj.type == "MESH"
    assembly = obj.parent.get("assembly")
    key = assembly if assembly in SCHEDULE else None
    ancestor = obj.parent
    while ancestor is not None and ancestor.get("assembly") == assembly:
        if ancestor in secondary_objects:
            key = secondary_objects[ancestor]
            break
        ancestor = ancestor.parent
    material = obj.material_slots[0].material
    vertices, faces, normals = buckets.setdefault((assembly, key, material.name), ([], [], []))
    evaluated = obj.evaluated_get(graph)
    mesh = evaluated.to_mesh()
    offset = len(vertices)
    # Bake evaluated geometry and custom normals exactly as the static V2 export.
    vertices.extend(tuple(obj.matrix_world @ v.co) for v in mesh.vertices)
    normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
    for face in mesh.polygons:
        faces.append(tuple(offset+i for i in face.vertices))
        source_triangles += len(face.vertices)-2
        normals.extend(tuple((normal_matrix @ mesh.corner_normals[i].vector).normalized())
                       for i in face.loop_indices)
    evaluated.to_mesh_clear()
assert source_triangles == source["triangles"]
assert source_meshes == source["sourceMeshes"]
bind_geometry = {}
for (assembly, key, material), (vertices, faces, normals) in buckets.items():
    name = (key or assembly)+" / "+material
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.normals_split_custom_set(normals)
    mesh.materials.append(bpy.data.materials[material])
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj["assembly"], obj["motionKey"] = assembly, key or "STATIC"
    if key:
        obj.parent = controls[key]
        obj.matrix_parent_inverse = rest_world[key].inverted()
    bind_geometry[obj.name] = {
        "vertices": len(vertices), "triangles": sum(len(f)-2 for f in faces),
        "material": material, "motionKey": key or "STATIC",
    }
for obj in objects:
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.collections.remove(original)

data = bpy.data.cameras.new(CAMERA)
data.lens, data.sensor_fit, data.clip_end = 55, "HORIZONTAL", 500
camera = bpy.data.objects.new(CAMERA, data)
scene.collection.objects.link(camera)
camera.rotation_mode = "QUATERNION"
scene.camera = camera
scene.frame_start, scene.frame_end = 1, FRAMES
scene.render.fps = FPS
scene.render.resolution_x, scene.render.resolution_y = SETTINGS["width"], SETTINGS["height"]
scene.render.resolution_percentage = 100
scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = SETTINGS["samples"]
scene.eevee.use_raytracing = True
scene.eevee.use_fast_gi = True
scene.eevee.shadow_ray_count, scene.eevee.shadow_step_count = 2, 8
scene.render.use_persistent_data = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"
for frame in range(1, FRAMES+1):
    time = (frame-1)/FPS
    for key, control in controls.items():
        control.matrix_basis = control_matrix(key, rest_basis[key], time)
        control.keyframe_insert("location", frame=frame)
        control.keyframe_insert("rotation_quaternion", frame=frame)
    camera.matrix_world = camera_matrix(time)
    camera.keyframe_insert("location", frame=frame)
    camera.keyframe_insert("rotation_quaternion", frame=frame)
for obj in [*controls.values(), camera]:
    linear_keys(obj)
scene.timeline_markers.clear()
for frame, name in BEATS:
    scene.timeline_markers.new(name, frame=frame)
scene["Scope"] = "V2 cinematic modular assembly; not six independent vehicle transformations."
scene["Revision"] = "V2 assembly animation, 18 seconds; original sculpture unchanged"
scene.frame_set(1)
bpy.context.view_layer.update()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.region_3d.view_perspective = "CAMERA"
bpy.context.preferences.filepaths.save_version = 0
output = ROOT/"deliverables/devastator-v2-assembly.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
paths = [output, *[ROOT/"scripts"/name for name in [
    "assembly_motion.py", "build_assembly.py", "audit_assembly.py",
    "render_assembly.py", "encode_assembly.py"]]]
manifest = {
    "version": 2, "revision": "assembly-animation", "settings": SETTINGS,
    "collection": COLLECTION, "camera": CAMERA, "sourceMeshes": source_meshes,
    "animatedMeshes": len(buckets), "triangles": source_triangles,
    "controls": {key: obj.name for key, obj in controls.items()},
    "restWorld": {key: [list(row) for row in matrix] for key, matrix in rest_world.items()},
    "restBasis": {key: [list(row) for row in matrix] for key, matrix in rest_basis.items()},
    "bindGeometry": bind_geometry, "beats": BEATS,
    "sourceInputs": {path: source["files"][path] for path in
                     ["deliverables/devastator-v2.blend", "assets/devastator-v2.glb"]},
    "files": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
    "scope": "Rigid modules with articulated elbows and folding crane; no vehicle mode or solved transformation.",
    "rendered": False,
}
(ROOT/"assets/devastator-v2-assembly.json").write_text(json.dumps(manifest, indent=2)+"\n")
print(json.dumps({"status": "BUILT", "triangles": source_triangles, "meshes": len(buckets),
                  "controls": len(controls), "frames": FRAMES}), flush=True)
