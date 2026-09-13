"""Sample selected moving surfaces with Blender's triangle BVH; does not save the scene."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_motion import matrices

parser = argparse.ArgumentParser()
parser.add_argument("--samples", type=int, default=161)
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
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

pairs = [("head", other) for other in ["left_roof", "right_roof", "cab_shell"]]
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
    ])
used = {name for pair in pairs for name in pair}
hits = {}
for sample in range(args.samples):
    transform = sample/(args.samples-1)
    frame = matrices(definition["joints"], transform)
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
report = {
    "version": definition["version"], "samples": args.samples, "pairs": len(pairs),
    "method": "triangle surface intersection, 0.1 mm BVH epsilon",
    "excluded": "same-assembly seams, guide tube nesting and intentional bearing couplings",
    "result": "PASS" if not hits else "FAIL",
    "intersections": {key: {**value, "objects": sorted(value["objects"])} for key, value in hits.items()},
    "assetSha256": hashlib.sha256((ROOT/"assets/optimus.glb").read_bytes()).hexdigest(),
    "rigSha256": hashlib.sha256((ROOT/"assets/optimus-rig.json").read_bytes()).hexdigest(),
}
(ROOT/"qa").mkdir(exist_ok=True)
(ROOT/"qa/motion-audit.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2))
if hits:
    raise RuntimeError("Selected moving surfaces intersect; see optimus/qa/motion-audit.json")
