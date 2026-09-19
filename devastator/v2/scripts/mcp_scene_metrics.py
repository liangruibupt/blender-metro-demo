"""Read-only scene metrics payload executed inside Blender through official MCP."""
import math

import bpy
import numpy as np

scene = bpy.context.scene
collection = bpy.data.collections["DEVASTATOR V2 | Assembly animation"]
meshes = [obj for obj in collection.objects if obj.type == "MESH"]
controls = [obj for obj in collection.objects if obj.get("motionKey") and obj.type == "EMPTY"]
triangles = sum(len(face.vertices)-2 for obj in meshes for face in obj.data.polygons)
corners = {obj.name: np.array([(*point, 1) for point in obj.bound_box]) for obj in meshes}
original_frame = scene.frame_current
original_subframe = scene.frame_subframe
original_filepath = scene.render.filepath
framing_failures = []
lowest_moving_point = float("inf")
maximum_scale_error = 0.0
extents = []
try:
    for frame in range(scene.frame_start, scene.frame_end+1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        world = np.concatenate([corners[obj.name] @ np.array(obj.matrix_world).T for obj in meshes])
        camera = scene.camera
        projection = camera.calc_matrix_camera(
            bpy.context.evaluated_depsgraph_get(),
            x=scene.render.resolution_x, y=scene.render.resolution_y)
        clip = world @ np.array(projection @ camera.matrix_world.inverted()).T
        projected = clip[:, :2]/clip[:, 3:4]*.5+.5
        low, high = projected.min(axis=0), projected.max(axis=0)
        if not (np.all(clip[:, 3] > .1) and np.all(low > .025) and np.all(high < .975)):
            framing_failures.append(frame)
        for obj in meshes:
            if obj["motionKey"] != "STATIC":
                points = corners[obj.name] @ np.array(obj.matrix_world).T
                lowest_moving_point = min(lowest_moving_point, float(points[:, 2].min()))
        for control in controls:
            maximum_scale_error = max(maximum_scale_error, *(abs(float(v)-1) for v in control.scale))
        if frame in [1, 73, 145, 217, 289, 361, 432]:
            extents.append({"frame": frame, "min": low.tolist(), "max": high.tolist()})
    maximum_final_vertex_error = max(
        (obj.matrix_world @ vertex.co-vertex.co).length for obj in meshes for vertex in obj.data.vertices)
    result = {
        "blenderVersion": bpy.app.version_string,
        "blendFile": bpy.data.filepath,
        "meshCount": len(meshes),
        "triangleCount": triangles,
        "motionControls": len(controls),
        "frameCount": scene.frame_end-scene.frame_start+1,
        "fps": scene.render.fps,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "renderEngine": scene.render.engine,
        "renderSamples": scene.eevee.taa_render_samples,
        "rayTracing": scene.eevee.use_raytracing,
        "fastGI": scene.eevee.use_fast_gi,
        "camera": scene.camera.name,
        "framingFailures": framing_failures,
        "minimumMovingBoundingZ": lowest_moving_point,
        "maximumScaleError": maximum_scale_error,
        "maximumFinalVertexError": maximum_final_vertex_error,
        "sampledFraming": extents,
        "missingMaterials": [obj.name for obj in meshes if not obj.material_slots or
                             any(slot.material is None for slot in obj.material_slots)],
        "finiteTransforms": all(math.isfinite(v) for obj in meshes for row in obj.matrix_world for v in row),
    }
finally:
    scene.frame_set(original_frame, subframe=original_subframe)
    bpy.context.view_layer.update()
    assert scene.render.filepath == original_filepath
result["restoredFrame"] = scene.frame_current
result["restoredSubframe"] = scene.frame_subframe
