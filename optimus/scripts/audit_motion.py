"""Sample selected moving surfaces with Blender's triangle BVH; does not save the scene."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_motion import C, matrices, pose

parser = argparse.ArgumentParser()
parser.add_argument("--samples", type=int, default=321)
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
if args.samples < 2:
    parser.error("--samples must be at least 2")
definition = json.loads((ROOT/"assets/optimus-rig.json").read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/"deliverables/optimus-prime.blend"))
bpy.context.scene.frame_set(1)
depsgraph = bpy.context.evaluated_depsgraph_get()
groups = {}
triangle_names = {}
for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    owner = obj.parent
    dynamic = False
    while owner and not owner.get("rigId"):
        if owner.get("linkId"):
            dynamic = True
            break
        owner = owner.parent
    if dynamic or owner is None:
        continue
    key = owner["rigId"]
    vertices, faces = groups.setdefault(key, ([], []))
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    matrix = owner.matrix_world.inverted() @ obj.matrix_world
    offset = len(vertices)
    vertices.extend(matrix @ vertex.co for vertex in mesh.vertices)
    faces.extend(tuple(offset+i for i in triangle.vertices) for triangle in mesh.loop_triangles)
    triangle_names.setdefault(key, []).extend([obj.name]*len(mesh.loop_triangles))
    evaluated.to_mesh_clear()

pairs = [("head", other) for other in [
    "left_roof", "right_roof", "cab_shell", "left_windscreen", "right_windscreen", "grille",
]]
for side in ["left", "right"]:
    pairs.extend([
        (f"{side}_fist", f"{side}_forearm"),
        (f"{side}_shoulder", "cab_shell"),
        (f"{side}_forearm", "cab_shell"),
        (f"{side}_front_wheel", f"{side}_forearm"),
        (f"{side}_front_wheel", f"{side}_shoulder"),
        (f"{side}_front_wheel", "cab_shell"),
        (f"{side}_front_axle", f"{side}_forearm"),
        (f"{side}_rear_wheel_32", f"{side}_rear_wheel_168"),
        (f"{side}_foot", f"{side}_shin"),
        (f"{side}_rear_bogie", f"{side}_shin"),
        (f"{side}_rear_wheel_32", f"{side}_shin"),
        (f"{side}_rear_wheel_168", f"{side}_shin"),
        (f"{side}_rear_wheel_32", f"{side}_foot"),
        (f"{side}_rear_wheel_168", f"{side}_foot"),
        (f"{side}_shoulder", "grille"),
        (f"{side}_forearm", "grille"),
        (f"{side}_front_wheel", f"{side}_roof"),
        (f"{side}_hip", "grille"),
        (f"{side}_foot", f"{side}_hip"),
    ])
pairs.append(("left_shin", "right_shin"))
for side, kind in [("left", "axe"), ("right", "rifle")]:
    pairs.extend((f"{side}_{kind}", other) for other in [
        f"{side}_forearm", f"{side}_shoulder", f"{side}_front_wheel",
        f"{side}_hip", f"{side}_shin", f"{side}_foot",
        f"{side}_rear_wheel_32", f"{side}_rear_wheel_168",
        "cab_shell", "grille", "head",
    ])
used = {name for pair in pairs for name in pair}
hits = {}
ground_failures = []
body_clearances = []
surface_clearances = []
truck_wheel_clearances = {}
ground_points = {key: np.asarray(vertices) for key, (vertices, _) in groups.items()}
for sample in range(args.samples):
    transform = sample/(args.samples-1)
    frame = matrices(definition["joints"], transform)
    minimums = {key: float(np.min(points @ np.asarray(frame[key])[2, :3]+frame[key][2][3]))
                for key, points in ground_points.items()}
    body_min = min(value for key, value in minimums.items()
                   if not any(word in key for word in ["weapon", "rifle", "axe"]))
    surface_min = min(minimums.values())
    body_clearances.append(body_min)
    surface_clearances.append(surface_min)
    if body_min > .065 or surface_min < .02:
        ground_failures.append({"transform": transform, "body": body_min, "surface": surface_min})
    if sample == args.samples-1:
        truck_wheel_clearances = {key: value for key, value in minimums.items() if "wheel" in key}
        if any(value > .07 or value < .02 for value in truck_wheel_clearances.values()):
            ground_failures.append({"transform": transform, "wheels": truck_wheel_clearances})
    trees = {
        name: BVHTree.FromPolygons([frame[name] @ vertex for vertex in groups[name][0]],
                                  groups[name][1], all_triangles=True, epsilon=.0001)
        for name in used
    }
    for left, right in pairs:
        overlaps = trees[left].overlap(trees[right])
        if overlaps:
            key = f"{left} / {right}"
            record = hits.setdefault(key, {"first": transform, "last": transform, "samples": 0,
                                           "maxTrianglePairs": 0, "objects": set()})
            record["last"] = transform
            record["samples"] += 1
            record["maxTrianglePairs"] = max(record["maxTrianglePairs"], len(overlaps))
            record["objects"].update(f"{triangle_names[left][a]} / {triangle_names[right][b]}" for a, b in overlaps)
pose_samples = []
for sample in range(17):
    transform = sample/16
    values = {}
    for entry in definition["joints"]:
        position, orient = pose(entry, transform)
        q = (C.inverted() @ orient.to_matrix() @ C).to_quaternion()
        values[entry["id"]] = {"position": list(C.inverted() @ position),
                              "quaternion": [q.x, q.y, q.z, q.w]}
    pose_samples.append({"transform": transform, "joints": values})
report = {
    "version": definition["version"], "samples": args.samples, "pairs": len(pairs),
    "method": "triangle surface intersection, 0.1 mm BVH epsilon",
    "excluded": "same-assembly seams, guide tube nesting and intentional bearing couplings",
    "result": "PASS" if not hits and not ground_failures else "FAIL",
    "grounding": {
        "bodyMin": min(body_clearances), "bodyMax": max(body_clearances),
        "surfaceMin": min(surface_clearances), "failures": ground_failures,
        "truckWheels": truck_wheel_clearances,
    },
    "intersections": {key: {**value, "objects": sorted(value["objects"])} for key, value in hits.items()},
    "assetSha256": hashlib.sha256((ROOT/"assets/optimus.glb").read_bytes()).hexdigest(),
    "rigSha256": hashlib.sha256((ROOT/"assets/optimus-rig.json").read_bytes()).hexdigest(),
    "blendSha256": hashlib.sha256((ROOT/"deliverables/optimus-prime.blend").read_bytes()).hexdigest(),
    "poseEvaluatorSha256": hashlib.sha256((ROOT/"scripts/rig_motion.py").read_bytes()).hexdigest(),
    "generatorSha256": hashlib.sha256((ROOT/"scripts/build_optimus.py").read_bytes()).hexdigest(),
    "weaponGeneratorSha256": hashlib.sha256((ROOT/"scripts/weapons.py").read_bytes()).hexdigest(),
    "checkedPairs": pairs,
    "poseSamples": pose_samples,
}
(ROOT/"qa").mkdir(exist_ok=True)
(ROOT/"qa/motion-audit.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps({key: value for key, value in report.items()
                  if key not in ["poseSamples", "checkedPairs"]}, indent=2))
if hits or ground_failures:
    raise RuntimeError("Motion collision or ground-contact failure; see optimus/qa/motion-audit.json")
