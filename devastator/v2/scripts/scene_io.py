"""Independent V2 exports, fitted perspective cameras and resource manifest."""
import hashlib
import itertools
import json
import math

import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


def finish_scene(root, args, workshop, collection, assemblies, soles):
    assets, delivery = root/"assets", root/"deliverables"
    assets.mkdir(parents=True, exist_ok=True)
    delivery.mkdir(exist_ok=True)
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    seen = set()
    for obj in collection.objects:
        if obj.type == "MESH" and obj.data not in seen:
            seen.add(obj.data)
            mesh = bmesh.new()
            mesh.from_mesh(obj.data)
            bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
            mesh.to_mesh(obj.data)
            mesh.free()
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    buckets, points, fit_points = {}, [], []
    source = list(collection.objects)
    for obj in source:
        if obj.type not in {"MESH", "CURVE"}:
            continue
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        label = obj.parent.get("assembly", "Unassigned")
        material = obj.material_slots[0].material.name
        vertices, faces, normals = buckets.setdefault((label, material), ([], [], []))
        offset = len(vertices)
        transformed = [obj.matrix_world @ v.co for v in mesh.vertices]
        points.extend(transformed)
        vertices.extend(tuple(v) for v in transformed)
        normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
        for face in mesh.polygons:
            faces.append(tuple(offset+i for i in face.vertices))
            normals.extend(tuple((normal_matrix @ mesh.corner_normals[i].vector).normalized())
                           for i in face.loop_indices)
        evaluated.to_mesh_clear()
    bounds = {key: [operation(v[i] for v in points) for i in range(3)]
              for key, operation in [("min", min), ("max", max)]}
    export = bpy.data.collections.new("Temporary evaluated export")
    scene.collection.children.link(export)
    bpy.ops.object.select_all(action="DESELECT")
    triangles = 0
    for (label, material), (vertices, faces, normals) in buckets.items():
        data = bpy.data.meshes.new(label+" / "+material)
        data.from_pydata(vertices, [], faces)
        data.update()
        data.normals_split_custom_set(normals)
        data.materials.append(workshop.materials[material])
        triangles += sum(len(face)-2 for face in faces)
        obj = bpy.data.objects.new(data.name, data)
        export.objects.link(obj)
        obj["assembly"] = label
        obj.select_set(True)
        low = [min(v[i] for v in vertices) for i in range(3)]
        high = [max(v[i] for v in vertices) for i in range(3)]
        fit_points.extend(Vector(v) for v in itertools.product(*zip(low, high)))
    bpy.ops.export_scene.gltf(filepath=str(assets/"devastator-v2.glb"), export_format="GLB",
                             use_selection=True, export_extras=True, export_animations=False)
    for obj in list(export.objects):
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(data)
    bpy.data.collections.remove(export)

    scene.render.engine = "CYCLES"
    if args.device == "METAL":
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = "METAL"
        preferences.get_devices()
        for device in preferences.devices:
            device.use = device.type == "METAL"
        if not any(device.use for device in preferences.devices):
            raise RuntimeError("No Metal GPU found; use --device CPU")
        scene.cycles.device = "GPU"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = round(args.resolution*.75)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.fps = 24
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.16, .16, .16, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .33
    nodes, links = scene.world.node_tree.nodes, scene.world.node_tree.links
    light_path = nodes.new("ShaderNodeLightPath")
    camera_background = nodes.new("ShaderNodeBackground")
    camera_background.inputs["Color"].default_value = (.003, .003, .003, 1)
    mixed = nodes.new("ShaderNodeMixShader")
    links.new(light_path.outputs["Is Camera Ray"], mixed.inputs[0])
    links.new(nodes["Background"].outputs[0], mixed.inputs[1])
    links.new(camera_background.outputs[0], mixed.inputs[2])
    links.new(mixed.outputs[0], nodes["World Output"].inputs["Surface"])
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    # A continuous 360-degree cyclorama removes the floor/world horizon at low angles.
    count = 128
    rings = [(42+12*math.sin(i*math.pi/48), -.64+12*(1-math.cos(i*math.pi/48)))
             for i in range(25)]+[(54, 45)]
    vertices = [(0, 0, -.64)]+[(r*math.cos(i*math.tau/count), r*math.sin(i*math.tau/count), z)
                             for r, z in rings for i in range(count)]
    faces = [(0, 1+i, 1+(i+1) % count) for i in range(count)]
    for j in range(len(rings)-1):
        faces += [(1+j*count+i, 1+(j+1)*count+i, 1+(j+1)*count+(i+1) % count,
                   1+j*count+(i+1) % count) for i in range(count)]
    data = bpy.data.meshes.new("Continuous studio cyclorama")
    data.from_pydata(vertices, [], faces)
    data.update()
    for face in data.polygons:
        face.use_smooth = True
    studio = bpy.data.objects.new("Studio cyclorama (not exported)", data)
    scene.collection.objects.link(studio)
    data.materials.append(workshop.material("studio", .070, 0, .81))
    for name, pos, energy, size in [
        ("Upper-left key", (-8, -10, 16), 2500, 6),
        ("Frontal fill", (7, -9, 9), 1050, 7),
        ("Sculpture rim", (5, 7, 14), 2900, 6),
        ("Left rear edge", (-8, 5, 7), 1600, 6),
    ]:
        bpy.ops.object.light_add(type="AREA", location=pos)
        obj = bpy.context.object
        obj.name, obj.data.energy, obj.data.shape, obj.data.size = name, energy, "DISK", size
        obj.rotation_euler = (Vector((0, 0, 5.5))-obj.location).to_track_quat("-Z", "Y").to_euler()

    def camera(name, direction, target, full=True):
        bpy.ops.object.camera_add()
        obj = bpy.context.object
        obj.name = "V2 View "+name
        obj.data.lens = 55
        obj.data.sensor_fit = "HORIZONTAL"
        obj.data.clip_end = 500
        direction, target = Vector(direction).normalized(), Vector(target)
        distance = 19 if full else 12
        for _ in range(80):
            obj.location = target+direction*distance
            obj.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
            bpy.context.view_layer.update()
            projected = [world_to_camera_view(scene, obj, p) for p in fit_points] if full else []
            if full:
                # Lens shift centers the asymmetric silhouette without changing the viewpoint.
                obj.data.shift_x += (min(p.x for p in projected)+max(p.x for p in projected))/2-.5
                obj.data.shift_y += ((min(p.y for p in projected)+max(p.y for p in projected))/2-.5
                                     )*scene.render.resolution_y/scene.render.resolution_x
                projected = [world_to_camera_view(scene, obj, p) for p in fit_points]
            if not full or all(.065 < p.x < .935 and .065 < p.y < .935 and p.z > .1 for p in projected):
                return obj
            distance *= 1.025
        raise RuntimeError("Camera could not frame the model: "+name)

    cameras = {
        "hero": camera("hero", (.86, -1, .10), (.65, -.1, 5.2)),
        "front": camera("front", (0, -1, .025), (.65, -.1, 5.2)),
        "rear": camera("rear", (.48, 1, .12), (.4, .0, 5.3)),
        "detail": camera("detail", (-.34, -1, .07), (-.1, -.1, 8.2), False),
    }
    # A separate camera orbits without altering any static inspection camera.
    orbit = bpy.data.objects.new("V2 Turntable orbit", None)
    scene.collection.objects.link(orbit)
    orbit.location = (.4, 0, 5.2)
    orbit.rotation_euler.z = math.atan2(.86, 1)
    orbit.keyframe_insert("rotation_euler", frame=1, index=2)
    orbit.rotation_euler.z += math.tau
    orbit.keyframe_insert("rotation_euler", frame=289, index=2)
    for layer in orbit.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation = "LINEAR"
    orbit_camera = camera("turntable", (0, -1, .04), orbit.location)
    orbit_camera.data.shift_x = orbit_camera.data.shift_y = 0
    orbit_camera.parent = orbit
    orbit_camera.location = (0, -40, 1.6)
    orbit_camera.rotation_euler = (-orbit_camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.frame_start, scene.frame_end = 1, 288
    scene.frame_set(1)
    scene.camera = cameras["hero"]
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
    scene["Scope"] = "V2 reference proportion study; combined form only; no physical transformation."
    scene["Reference"] = "Rex Hsu: https://www.artstation.com/artwork/w6KbAZ"
    scene["Reference video"] = "2-00x-3840x2160-alq-8-1.mp4; 12.01s; supplied by user"
    scene["Revision"] = "V2 video-guided refinement"
    bpy.ops.wm.save_as_mainfile(filepath=str(delivery/"devastator-v2.blend"), compress=True)
    if args.render:
        for view in args.views:
            scene.camera = cameras[view]
            scene.render.filepath = str(delivery/f"devastator-v2-{view}.png")
            bpy.ops.render.render(write_still=True)
    feet = [{"name": obj.name, "ground": z,
             "actual": min((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)}
            for obj, z in soles]
    metadata = {
        "version": 2, "revision": "video-refinement", "collection": collection.name,
        "sourceMeshes": sum(obj.type == "MESH" for obj in source),
        "browserMeshes": len(buckets), "triangles": triangles, "assemblies": list(assemblies),
        "bounds": bounds, "feet": feet,
        "cameras": {view: obj.name for view, obj in cameras.items()},
        "orbitCamera": orbit_camera.name,
        "studio": studio.name,
        "heroAzimuthDegrees": math.degrees(math.atan2(.86, 1)),
        "renderSettings": {"width": args.resolution, "height": round(args.resolution*.75),
                           "samples": args.samples, "engine": "CYCLES", "device": args.device},
        "turntableSettings": {"width": 1920, "height": 1080, "fps": 24, "frames": 288,
                              "loopFrame": 289, "seconds": 12, "engine": "BLENDER_EEVEE",
                              "samples": 64},
        "renderedViews": args.views if args.render else [],
        "scope": "Static gray sculpture. Not an exact reconstruction or validated transformation.",
        "files": {},
    }
    paths = list((root/"scripts").glob("*.py"))+[assets/"devastator-v2.glb", delivery/"devastator-v2.blend"]
    paths += [delivery/f"devastator-v2-{view}.png" for view in metadata["renderedViews"]]
    for path in paths:
        metadata["files"][str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    (assets/"devastator-v2.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(json.dumps({"version": 2, "meshes": metadata["sourceMeshes"], "feet": feet,
                      "output": str(delivery)}, indent=2))
