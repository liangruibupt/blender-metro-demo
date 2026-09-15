"""Build the current V2 sculpture, stills and reproducible turntable scene."""
import argparse
from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import Workshop
from parts import loft
from upper_body import build_upper
from lower_body import build_pelvis, build_legs
from scene_io import finish_scene
import refinement

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--render", action="store_true")
parser.add_argument("--resolution", type=int, default=1600)
parser.add_argument("--samples", type=int, default=64)
parser.add_argument("--device", choices=["CPU", "METAL"], default="METAL")
parser.add_argument("--views", nargs="+", default=["hero", "front", "rear", "detail"])
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
collection = bpy.data.collections.new("DEVASTATOR V2 | Reference silhouette")
scene.collection.children.link(collection)
w = Workshop(collection)
for name, value, metal, rough in [
    ("armor", .24, .24, .41), ("edge", .34, .45, .33), ("steel", .20, .78, .32),
    ("joint", .074, .45, .40), ("recess", .023, .08, .61),
    ("rubber", .038, .01, .72), ("track", .155, .52, .46),
    ("glass", .066, .20, .20), ("optic", .45, .22, .27), ("concrete", .145, 0, .90),
]:
    w.material(name, value, metal, rough)
root = w.group("Devastator V2")
assemblies = {}


def assembly(name, pos, parent=root, rot=(0, 0, 0)):
    obj = w.group(name, pos, parent, rot, name)
    assemblies[name] = obj
    return obj


pelvis = build_pelvis(w, assembly)
build_upper(w, assembly, pelvis)
soles = build_legs(w, assembly)
base = assembly("12 Fractured concrete base", (0, 0, 0))
outline = [(-3.4, -2.0), (-2.8, -2.7), (.7, -2.85), (3.3, -2.3),
           (3.65, -.7), (3.1, 1.6), (.7, 2.35), (-2.8, 1.9), (-3.6, .7)]
vertices = [(x, y, z) for z in [-.60, 0] for x, y in outline]
n = len(outline)
faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
faces += [(i, (i+1) % n, (i+1) % n+n, i+n) for i in range(n)]
w.mesh("Broken industrial foundation", vertices, faces, "concrete", base, .065)
w.box("Raised mixer contact slab", (2.15, -1.25, .10), (2.23, 2.98, .20), "concrete", base, .03,
      (0, 0, .06))
for i, (x, y, sx, sy, z) in enumerate([
    (-2.8, -1.9, .51, .62, .16), (-.1, -2.29, .62, .41, .18),
    (.46, 1.65, .85, .43, .19), (-2.84, .99, .49, .60, .28),
    (3.23, .50, .40, .54, .23), (-.29, .48, .49, .51, .26),
]):
    group = w.group("Concrete fragment", (x, y, .01), base, (.05, -.07, i*.63))
    loft(w, "Fractured rubble", [(0, sx, sy, 0, 0), (z*.71, sx*.79, sy*.86, .03, 0),
         (z, sx*.43, sy*.45, .01, .04)], group, "concrete")
for x in [-2.6, -1.2, .1, 1.4]:
    w.rod("Exposed reinforcement bar", (x, -2.63, -.37), (x+.28, -2.91, -.27), .026, "steel", base)
refinement.rubble(w, base)
finish_scene(ROOT, args, w, collection, assemblies, soles)
