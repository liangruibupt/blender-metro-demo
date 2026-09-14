"""Build an original reference-guided Devastator clay model and inspection assets."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import Workshop

ROOT = Path(__file__).resolve().parents[1]
ASSETS, DELIVERY = ROOT / "assets", ROOT / "deliverables"
ASSETS.mkdir(parents=True, exist_ok=True)
DELIVERY.mkdir(exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument("--render", action="store_true")
parser.add_argument("--resolution", type=int, default=1400)
parser.add_argument("--samples", type=int, default=48)
parser.add_argument("--views", nargs="+", default=["hero", "front", "rear", "detail"])
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
collection = bpy.data.collections.new("DEVASTATOR | Editable mechanical assemblies")
scene.collection.children.link(collection)
w = Workshop(collection)
for name, value, metal, rough in [
    ("armor", .26, .22, .44), ("edge", .40, .32, .36), ("steel", .22, .65, .32),
    ("joint", .075, .42, .44), ("recess", .032, .16, .52),
    ("rubber", .032, .05, .72), ("track", .16, .40, .47),
    ("glass", .11, .28, .21), ("optic", .66, .40, .23), ("concrete", .19, .0, .88),
]:
    w.material(name, value, metal, rough)

root = w.group("Devastator")
assemblies = {}


def assembly(name, pos, parent=root, rot=(0, 0, 0)):
    obj = w.group(name, pos, parent, rot, assembly=name)
    assemblies[name] = obj
    return obj


def ladder(pos, height, parent, width=.36, rear=False):
    x, y, z = pos
    for side in [-1, 1]:
        w.rod("Ladder rail", (x+side*width/2, y, z-height/2),
              (x+side*width/2, y, z+height/2), .024, "steel", parent)
    for i in range(max(2, round(height/.18))):
        zz = z-height/2+i*.18
        w.rod("Ladder rung", (x-width/2, y, zz), (x+width/2, y, zz), .021, "edge", parent)


def bucket(name, pos, width, parent, rot=(0, 0, 0)):
    g = w.group(name, pos, parent, rot)
    # Open scoop made from a folded rear wall, floor, ribs, and side cheeks.
    w.box("Scoop rear wall", (0, .12, .22), (width, .13, .90), "armor", g, .05, (.20, 0, 0))
    w.box("Scoop floor", (0, -.40, -.17), (width, 1.03, .14), "edge", g, .035, (.14, 0, 0))
    for side in [-1, 1]:
        cheek = w.plate("Scoop cheek", [(-.55, -.26), (.52, -.10), (.43, .63), (.21, .65)],
                        0, .10, "armor", g)
        cheek.rotation_euler.z = math.pi/2
        cheek.location.x = side*(width/2-.03)
    for x in [-width*.36, 0, width*.36]:
        w.box("Scoop reinforcement", (x, .24, .25), (.12, .15, .90), "steel", g)
    for i in range(7):
        x = (i-3)*width/7.2
        w.box("Forged scoop tooth", (x, -.99, -.21), (width/10, .27, .13), "steel", g, .035)
    return g


# Chest: broad structural bridge with a V-shaped lower edge, not a cuboid torso.
torso = assembly("01 Chest and abdomen", (0, 0, 7.65))
w.box("Thoracic chassis", (0, .08, .67), (2.60, 1.42, 2.08), "joint", torso, .12)
w.plate("Chest bridge backing", [(-1.88, 1.13), (0, .66), (1.88, 1.13),
        (1.72, 2.05), (-1.72, 2.05)], -.79, .30, "recess", torso, .08)
for side in [-1, 1]:
    profile = [(side*.10, .92), (side*1.74, 1.34), (side*1.70, 1.93), (side*.10, 1.83)]
    if side < 0:
        profile.reverse()
    w.plate("Swept chest armor", profile, -.98, .25, "armor", torso, .055)
    w.rod("Chest upper edge", (side*.13, -1.13, 1.77), (side*1.63, -1.13, 1.87),
          .052, "edge", torso)
    w.rod("Chest diagonal reinforcement", (side*.16, -1.14, 1.01), (side*1.66, -1.14, 1.42),
          .045, "edge", torso)
    for j in range(3):
        x = side*(.4+j*.45)
        z = 1.51+j*.045
        w.panel("Chest service plate", (x, -1.15, z), .37, .31, torso, "steel", .01)
        w.vent("Chest plate intake", (x, -1.265, z), .24, .14, torso, n=3)
        w.rod("Chest bridge vertical web", (x+side*.19, -1.17, 1.13+j*.09),
              (x+side*.19, -1.17, 1.81+j*.02), .025, "edge", torso)
    w.piston("Chest locking ram", (side*1.60, -1.16, 1.10), (side*1.57, -1.16, 1.97),
             torso, .075)
    w.box("Shoulder crossmember", (side*1.87, .05, 1.25), (.65, .75, .63), "joint", torso)
    w.cyl("Shoulder swivel", (side*2.03, 0, 1.38), .44, .55, "steel", torso, (1, 0, 0))
    for z in [-.18, .20, .56]:
        w.box("Oblique abdominal rib", (side*.91, -.20, z), (.32, 1.14, .22),
              "armor", torso, .045, (0, side*.18, 0))
    w.hose("Thoracic hydraulic hose", [(side*1.70, .18, 1.29), (side*1.25, -.30, .64),
           (side*1.06, -.58, -.34)], .047, "recess", torso)
    w.hose("Braided lower line", [(side*.92, -.69, .49), (side*.77, -.89, .08),
           (side*.83, -.61, -.48)], .032, "steel", torso)
    w.panel("Lower chest layered shield", (side*.56, -.96, .75), .73, .24, torso)
    for z in [.20, .40, .60]:
        w.panel("Abdominal overlapping shield", (side*.65, -.69, z), .40, .14, torso, "steel", .012)
    w.piston("Spinal side damper", (side*.61, .62, -.93), (side*.71, .65, 1.51), torso, .09)
    w.vent("Side torso heat exchanger", (side*1.08, -.65, .52), .35, .42, torso, n=7)
w.panel("Central chest lock", (0, -1.19, 1.40), .40, 1.04, torso, "edge", .035)
w.vent("Sternum slots", (0, -1.33, 1.27), .23, .46, torso, n=6)
w.panel("Upper sternum badge", (0, -1.34, 1.72), .21, .23, torso, "joint", .01)
w.box("Abdominal core", (0, .08, -.38), (1.59, 1.24, 1.53), "joint", torso, .15)
w.vent("Abdominal radiator", (0, -.62, -.35), .96, .95, torso, vertical=True, n=15)
for side in [-1, 1]:
    w.rod("Radiator diagonal brace", (side*.56, -.74, -.90), (-side*.56, -.74, .12),
          .025, "edge", torso)
    w.panel("Waist service hatch", (side*.83, -.63, -.69), .42, .48, torso)
    w.cyl("Side reservoir", (side*1.03, .30, -.65), .24, .84, "steel", torso)
    for z in [-.95, -.37]:
        w.ring("Reservoir strap", (side*1.03, .30, z), .245, .034, "edge", torso)

# Helmet and face are angular independent surfaces, with a recessed visor.
head = assembly("02 Head", (0, -.02, 10.15))
w.cyl("Neck bearing", (0, 0, -.22), .27, .38, "steel", head)
w.plate("Helmet silhouette", [(-.52, -.24), (-.55, .35), (-.37, .65), (.29, .68),
        (.51, .39), (.49, -.24)], 0, .68, "armor", head, .045)
for side in [-1, 1]:
    w.panel("Helmet cheek armor", (side*.42, -.40, -.02), .21, .57, head, "edge", .025)
    w.cyl("Auditory spindle", (side*.54, -.03, .18), .15, .105, "steel", head, (1, 0, 0))
w.plate("Visor recess", [(-.35, .12), (0, .03), (.35, .12), (.35, .29), (-.35, .29)],
        -.375, .035, "recess", head, .008)
w.plate("Twin optic slit", [(-.32, .16), (0, .10), (.32, .16), (.31, .23), (-.31, .23)],
        -.402, .02, "optic", head, .008)
w.plate("Faceted face", [(-.26, -.21), (-.33, .08), (0, .03), (.32, .08), (.25, -.22), (0, -.31)],
        -.40, .15, "steel", head, .02)
w.box("Recessed mouth", (0, -.49, -.16), (.21, .025, .045), "recess", head, .005)
w.panel("Helmet forehead ridge", (0, -.31, .49), .20, .21, head, "edge", .018)

# Pelvis, long articulated thighs, and distinctly different vehicle lower legs.
pelvis = assembly("03 Pelvis", (0, 0, 5.73))
w.cyl("Waist slew ring", (0, 0, .39), .83, .37, "steel", pelvis, n=48)
w.cyl("Waist rotary coupler", (0, 0, .68), .61, .47, "joint", pelvis, n=48)
for z in [.53, .65, .77, .89]:
    w.ring("Waist bellows reinforcement", (0, 0, z), .61, .045, "recess", pelvis)
for side in [-1, 1]:
    w.piston("Lumbar actuator", (side*.72, .28, .30), (side*.67, .27, 1.05), pelvis, .085)
w.box("Pelvic carrier", (0, .02, .03), (2.22, 1.12, .78), "joint", pelvis, .16)
w.panel("Belt plate", (0, -.67, .19), .61, .45, pelvis)
w.plate("Central pelvic apron", [(-.37, .00), (.37, .00), (.31, -.98), (.18, -1.14),
        (-.21, -1.10), (-.34, -.83)], -.65, .23, "armor", pelvis)
w.vent("Apron slots", (0, -.80, -.56), .29, .65, pelvis, n=7)
for side in [-1, 1]:
    w.panel("Hip skirt", (side*.82, -.71, -.12), .83, .72, pelvis)
    w.vent("Hip grille", (side*.82, -.85, -.10), .55, .22, pelvis, n=4)
    w.tire("Hip road wheel", (side*1.12, .20, -.02), .46, .23, pelvis)

for side, label in [(-1, "04 Loader leg"), (1, "05 Mixer leg")]:
    leg_angle = .105 if side < 0 else -.17
    leg = assembly(label, (side*1.03, 0, 5.46), rot=(0, leg_angle, 0))
    w.cyl("Hip universal", (0, 0, 0), .43, 1.0, "steel", leg, (1, 0, 0))
    w.box("Thigh skeleton", (0, .03, -.87), (.91, .86, 1.68), "joint", leg, .10)
    w.plate("Tapered thigh armor", [(-.55, -.19), (.55, -.19), (.43, -1.62), (-.43, -1.62)],
            -.49, .23, "armor", leg, .07)
    w.panel("Thigh split plate", (0, -.67, -.73), .55, .74, leg)
    w.vent("Thigh intake", (0, -.76, -.60), .28, .33, leg, n=5)
    for sx in [-1, 1]:
        w.panel("Thigh longitudinal panel", (sx*.37, -.67, -.89), .14, .96, leg, "edge", .012)
        w.rod("Exposed thigh conduit", (sx*.26, -.76, -.94), (sx*.26, -.76, -1.42),
              .029, "steel", leg)
    w.panel("Thigh lower hatch", (0, -.69, -1.37), .38, .23, leg, "steel")
    for sx in [-1, 1]:
        w.piston("Thigh actuator", (sx*.43, .12, -.20), (sx*.38, .12, -1.65), leg, .08)
    w.tire("Upper leg vehicle wheel", (side*.64, .17, -.81), .42, .23, leg)
    rear_thigh = w.group("Rear thigh detail", (0, .49, -.86), leg, (0, 0, math.pi))
    w.panel("Rear thigh service cover", (0, -.04, 0), .71, 1.13, rear_thigh, "armor")
    w.vent("Rear thigh cooling slots", (0, -.17, .20), .45, .27, rear_thigh, n=5)
    for sx in [-1, 1]:
        w.piston("Rear thigh hydraulic guide", (sx*.34, -.12, -.51),
                 (sx*.34, -.12, .48), rear_thigh, .038)
    w.cyl("Knee main pin", (0, -.01, -1.81), .37, 1.17, "steel", leg, (1, 0, 0))
    w.panel("Knee cap", (0, -.55, -1.80), .76, .56, leg, "edge")
    w.vent("Knee ridges", (0, -.70, -1.78), .49, .25, leg, n=4)
    shin = w.group("Lower vehicle chassis", (0, 0, -1.91), leg)
    w.box("Shin twin frame", (0, .22, -1.22), (1.17, 1.13, 2.47), "joint", shin, .12)
    rear_shin = w.group("Rear shin service bay", (0, .82, -1.26), shin, (0, 0, math.pi))
    w.panel("Rear engine access", (0, -.025, .06), .94, 1.98, rear_shin, "armor")
    w.vent("Rear chassis radiator", (0, -.15, .58), .65, .52, rear_shin, n=9)
    w.panel("Rear chassis auxiliary panel", (-.14, -.14, -.13), .41, .43, rear_shin, "steel")
    w.panel("Rear chassis battery hatch", (0, -.14, -.65), .57, .32, rear_shin)
    for sx in [-1, 1]:
        w.rod("Rear chassis external line", (sx*.41, -.17, -.78),
              (sx*.41, -.17, .31), .024, "steel", rear_shin)
    w.hazard((0, -.26, -.65), .44, .16, rear_shin)
    for sx in [-1, 1]:
        w.box("Chassis longitudinal beam", (sx*.51, .54, -1.18), (.19, .24, 2.71), "steel", shin)
        w.piston("Ankle load actuator", (sx*.52, .02, -.98), (sx*.54, -.02, -2.71), shin, .11)
        for z in [-.51, -1.58, -2.23]:
            w.tire("Lower chassis wheel", (sx*.73, .30, z), .39 if z > -2 else .34, .24, shin)
    if side < 0:
        w.box("Loader engine bay", (0, -.17, -1.13), (1.21, .93, 2.06), "armor", shin, .11)
        w.panel("Loader front service door", (0, -.70, -1.11), .93, 1.43, shin)
        w.vent("Loader grille", (0, -.85, -.59), .65, .33, shin, n=7)
        w.panel("Lower inspection cover", (-.12, -.85, -1.54), .47, .37, shin, "steel")
        w.panel("Central engine access", (-.10, -.84, -1.06), .48, .39, shin)
        w.vent("Lower engine cooling bank", (-.1, -.96, -1.48), .27, .18, shin, n=4)
        for sx in [-1, 1]:
            w.box("Vertical loader armor rail", (sx*.47, -.79, -1.16), (.13, .15, 1.94),
                  "steel", shin, .014)
        w.piston("Loader front hydraulic ram", (-.38, -.89, -.99), (-.38, -.90, -1.99),
                 shin, .046)
        w.box("Loader side tank", (-.73, .04, -.36), (.25, .61, .77), "edge", shin, .08)
        w.cyl("Loader exhaust", (-.67, .26, -.04), .076, .78, "steel", shin)
        ladder((.49, -.80, -1.28), 1.10, shin, .22)
    else:
        w.barrel("Concrete mixer drum", (0, -.46, -1.36),
                 [(-1.00, .29), (-.82, .49), (-.58, .67), (.29, .67), (.62, .48), (.94, .29)],
                 shin)
        for z, radius in [(-2.04, .61), (-1.65, .678), (-1.02, .678), (-.78, .55)]:
            w.ring("Drum rolling band", (0, -.46, z), radius, .042, "edge", shin)
        w.cyl("Mixer drive gear", (0, -.46, -.40), .30, .18, "joint", shin, n=32)
        for i in range(28):
            a = i*math.tau/28
            w.box("Mixer gear tooth", (math.cos(a)*.31, -.46+math.sin(a)*.31, -.42),
                  (.055, .055, .13), "steel", shin, .008, (0, 0, a))
        # Alternating dark strips wrap the cylindrical middle belt.
        for i in range(12):
            a0 = i*math.tau/12
            a1 = a0+math.tau/24
            vertices = [(r*math.cos(a), -.46+r*math.sin(a), z)
                        for z in [-1.64, -1.06] for a, r in [(a0, .675), (a1, .675)]]
            w.mesh("Mixer safety belt stripe", vertices, [(0, 1, 3, 2)], "recess", shin)
        ladder((.78, -.22, -1.34), 1.55, shin, .22)
        w.hose("Mixer delivery hose", [(-.75, .02, -.37), (-.84, -.10, -.87),
               (-.82, -.12, -2.15)], .06, "rubber", shin)
    foot = w.group("Grounded foot", (0, -.12, -2.87), shin, rot=(0, -leg_angle, 0))
    w.box("Foot structural sole", (0, -.39, -.25), (1.63, 2.05, .30), "joint", foot, .07)
    w.box("Foot armored deck", (0, -.46, -.07), (1.70, 1.91, .26), "armor", foot, .06)
    for x in [-.53, 0, .53]:
        w.panel("Toe plate", (x, -1.45, -.09), .43, .26, foot, "edge", .025)
    if side < 0:
        bucket("Loader foot scoop", (0, -.49, .17), 1.56, foot)
        for sx in [-1, 1]:
            w.piston("Loader scoop linkage", (sx*.61, .44, .55), (sx*.62, -.66, .19), foot, .085)
        for x in [-.47, 0, .47]:
            w.box("Scoop floor wear strip", (x, -.75, .08), (.075, .65, .055), "steel", foot, .009)
    else:
        w.box("Mixer truck cab", (0, -.18, .40), (1.44, 1.19, .92), "armor", foot, .11)
        w.panel("Cab windshield frame", (0, -.817, .59), 1.26, .47, foot, "edge")
        w.box("Dark windshield", (0, -.94, .61), (1.03, .028, .30), "glass", foot, .04)
        w.box("Windshield center pillar", (0, -.962, .61), (.043, .033, .31), "armor", foot, .007)
        w.vent("Truck grille", (0, -.825, .13), .75, .22, foot, n=5)
        for sx in [-1, 1]:
            w.box("Headlight recess", (sx*.57, -.83, .16), (.24, .055, .13), "recess", foot)
            for i in [-1, 1]:
                w.cyl("Headlight lens", (sx*.57+i*.054, -.88, .16), .043, .025,
                      "optic", foot, (0, 1, 0))
            w.rod("Mirror arm", (sx*.65, -.73, .68), (sx*.84, -.76, .66), .023, "steel", foot)
            w.box("Mirror", (sx*.86, -.76, .62), (.10, .075, .18), "joint", foot, .02)

# Shoulder crawler vehicles: one excavator and one bulldozer.
for side in [-1, 1]:
    shoulder = assembly("06 Excavator shoulder" if side < 0 else "07 Dozer shoulder",
                        (side*2.51, 0, 9.12))
    w.cyl("Shoulder rotary joint", (0, .01, -.28), .46, .90, "joint", shoulder, (1, 0, 0))
    w.box("Crawler platform", (0, .02, .24), (1.83, 1.23, .46), "steel", shoulder, .10)
    for yy in [-.62, .62]:
        w.track("Shoulder crawler", (0, yy, .38), 2.21, .38, .30, shoulder)
    w.box("Vehicle engine block", (-side*.22, .09, .89), (1.39, 1.17, .64), "armor", shoulder, .10)
    w.panel("Engine front hatch", (-side*.23, -.56, .98), .77, .41, shoulder)
    w.vent("Engine cooling grille", (-side*.25, -.70, .99), .47, .20, shoulder, n=5)
    w.box("Crawler cab", (side*.56, -.04, 1.07), (.58, .92, .81), "armor", shoulder, .06)
    w.panel("Crawler windshield", (side*.56, -.52, 1.16), .39, .38, shoulder, "glass")
    w.cyl("Engine exhaust stack", (-side*.67, .24, 1.38), .06, .52, "steel", shoulder)
    rear_engine = w.group("Crawler rear service face", (0, .70, .91), shoulder, (0, 0, math.pi))
    w.panel("Crawler rear engine door", (side*.21, -.02, 0), .81, .48, rear_engine)
    w.vent("Crawler rear air outlet", (side*.21, -.15, 0), .52, .23, rear_engine, n=5)
    for sx in [-1, 1]:
        w.rod("Engine deck handrail", (sx*.80, .39, 1.36), (sx*.80, -.36, 1.36),
              .023, "edge", shoulder)
        for yy in [-.36, .39]:
            w.rod("Handrail upright", (sx*.80, yy, 1.11), (sx*.80, yy, 1.36),
                  .025, "steel", shoulder)
    if side > 0:
        bucket("Raised bulldozer blade", (0, -.15, 1.58), 2.37, shoulder, (.30, 0, 0))
        for sx in [-1, 1]:
            w.piston("Blade lift cylinder", (sx*.65, .15, .56), (sx*.78, -.01, 1.63),
                     shoulder, .085)
    else:
        boom = w.group("Folded excavator boom", (-.43, .73, .83), shoulder, (.48, -.30, 0))
        w.box("Excavator boom base", (0, 0, .52), (.35, .40, 1.27), "armor", boom)
        w.cyl("Boom pivot pin", (0, -.03, .05), .20, .58, "steel", boom, (0, 1, 0))
        w.box("Folded stick", (.37, 0, .95), (.83, .36, .28), "edge", boom)
        w.piston("Excavator boom piston", (-.10, -.26, .02), (.26, -.26, 1.05), boom, .065)
        bucket("Excavator bucket", (.74, -.05, .96), .66, boom, (0, -.9, 0))


def hand(name, parent, pos, curl=True):
    h = w.group(name, pos, parent)
    w.cyl("Wrist bearing", (0, 0, .23), .27, .30, "steel", h)
    w.box("Palm housing", (0, 0, -.12), (.92, .58, .65), "joint", h, .10)
    w.panel("Hand dorsal armor", (0, -.35, -.09), .77, .46, h, "armor", .05)
    for i in range(4):
        x = (i-1.5)*.215
        for j in range(3):
            y = -.09-j*.135
            z = -.45-j*.095
            w.box("Articulated finger segment", (x, y, z), (.185, .225, .22),
                  "armor" if j != 1 else "steel", h, .035, (j*.45, 0, 0))
            w.cyl("Finger knuckle pin", (x, y, z+.03), .07, .195, "joint", h, (1, 0, 0), 12)
    w.box("Thumb proximal", (-.51, -.05, -.20), (.25, .30, .33), "armor", h, .05, (0, -.45, 0))
    w.box("Thumb tip", (-.48, -.24, -.43), (.24, .27, .26), "edge", h, .05, (.40, 0, 0))
    return h


for side in [-1, 1]:
    arm = assembly("08 Raised arm" if side < 0 else "09 Weapon arm",
                   (side*2.52, 0, 8.89), rot=(0, -side*.20, 0))
    w.cyl("Upper arm swivel", (0, 0, -.12), .35, .89, "steel", arm, (1, 0, 0))
    w.box("Upper arm structure", (0, 0, -.60), (.74, .75, .91), "joint", arm)
    w.panel("Upper arm armor", (0, -.46, -.54), .86, .84, arm)
    for sx in [-1, 1]:
        w.piston("Biceps ram", (sx*.38, -.05, -.15), (sx*.39, -.05, -1.17), arm, .065)
    elbow = w.group("Elbow flexion", (0, 0, -1.19), arm,
                    rot=(math.radians(-106 if side < 0 else -16), 0, 0))
    w.cyl("Elbow hinge", (0, 0, 0), .30, 1.13, "steel", elbow, (1, 0, 0))
    w.box("Heavy forearm carrier", (0, 0, -.68), (1.19, 1.08, 1.25), "joint", elbow, .15)
    rear_arm = w.group("Forearm rear detail", (0, .56, -.68), elbow, (0, 0, math.pi))
    w.panel("Rear forearm shell", (0, -.03, 0), .93, .94, rear_arm)
    w.vent("Rear forearm outlet", (0, -.16, .17), .58, .26, rear_arm, n=5)
    w.panel("Rear forearm access", (0, -.15, -.23), .56, .24, rear_arm, "steel")
    w.plate("Forearm shell", [(-.65, -.12), (.65, -.12), (.59, -1.13),
            (.39, -1.31), (-.43, -1.31), (-.62, -1.11)], -.55, .20, "armor", elbow, .06)
    w.panel("Forearm inspection panel", (0, -.71, -.48), .83, .52, elbow)
    w.vent("Forearm louvres", (0, -.84, -.47), .52, .27, elbow, n=5)
    for sx in [-1, 1]:
        w.panel("Forearm reinforcing rail", (sx*.48, -.73, -.76), .15, .61, elbow, "steel", .015)
        w.rod("Cuff locking tie", (sx*.34, -.70, -.81), (sx*.34, -.69, -1.19),
              .031, "edge", elbow)
    for sx in [-1, 1]:
        w.cyl("Forearm hydraulic tank", (sx*.65, .10, -.63), .17, .89, "armor", elbow)
        for z in [-.98, -.32]:
            w.ring("Tank clamp", (sx*.65, .10, z), .18, .024, "edge", elbow)
        w.hose("Forearm return hose", [(sx*.47, -.49, -.16), (sx*.58, -.67, -.30),
               (sx*.46, -.70, -1.12)], .028, "steel", elbow)
    w.panel("Forearm cuff", (0, -.60, -1.18), .93, .24, elbow, "edge")
    fist = hand("Mechanical fist", elbow, (0, -.02, -1.53))
    if side > 0:
        weapon = assembly("10 Four-bore cannon", (.08, -.14, -.29), fist,
                          rot=(0, -.68, 0))
        w.box("Cannon receiver", (0, .05, -.39), (.69, .67, 1.35), "joint", weapon, .08)
        w.panel("Cannon receiver plate", (0, -.32, -.41), .54, 1.05, weapon, "armor")
        for z in [-.32, -.72]:
            w.box("Cannon side rail", (.44, 0, z), (.25, .57, .23), "edge", weapon)
        w.cyl("Barrel locking collar", (0, 0, -1.11), .42, .33, "steel", weapon, n=40)
        for x, y in [(-.17, -.17), (.17, -.17), (-.17, .17), (.17, .17)]:
            w.cyl("Long cannon barrel", (x, y, -2.11), .135, 2.02, "steel", weapon)
            w.cyl("Muzzle rim", (x, y, -3.14), .165, .18, "edge", weapon)
            w.cyl("Dark recessed bore", (x, y, -3.237), .116, .007, "recess", weapon)
        for z in [-1.47, -2.51, -3.02]:
            w.ring("Barrel bundle band", (0, 0, z), .43, .070, "armor", weapon)
        for sx in [-1, 1]:
            w.box("Floating barrel shroud", (sx*.40, .04, -2.18), (.13, .60, 1.77),
                  "armor", weapon, .035)
            for z in [-1.55, -1.91, -2.27, -2.63]:
                w.bolt((sx*.40, -.30, z), weapon)
        w.box("Top sight", (0, -.43, -.44), (.15, .15, .57), "edge", weapon)

# Crane backpack with open trusses, exposed winches and a folded long boom.
back = assembly("11 Crane backpack", (0, .98, 8.06))
w.box("Backpack base", (0, .17, .53), (2.12, .63, 1.71), "joint", back, .13)
for sx in [-1, 1]:
    w.box("Backpack longitudinal rail", (sx*.90, .51, .55), (.22, .32, 2.17), "armor", back)
    w.cyl("Backpack winch", (sx*.51, .55, -.40), .31, .80, "steel", back)
    for z in [-.73, -.45, -.17]:
        w.ring("Winch band", (sx*.51, .55, z), .32, .035, "edge", back)
    w.hose("Back hydraulic circuit", [(sx*.86, .65, 1.18), (sx*.55, .79, .59),
           (sx*.39, .79, -.22)], .052, "recess", back)
    w.rod("Back diagonal brace", (sx*.91, .75, -.32), (-sx*.86, .75, 1.31), .065, "steel", back)
    w.cyl("Exhaust outlet", (sx*.84, .52, .15), .15, .39, "edge", back, (0, 1, 0))
    w.cyl("Exhaust hollow", (sx*.84, .725, .15), .115, .015, "recess", back, (0, 1, 0))
boom = w.group("Folded crane mast", (0, .70, .87), back, (0, -.14, 0))
w.box("Crane boom central spine", (0, .06, -.65), (.28, .34, 3.80), "joint", boom)
for sx in [-1, 1]:
    w.box("Crane lattice main rail", (sx*.43, .06, -.65), (.17, .27, 3.95), "armor", boom)
    for i in range(8):
        z = -2.40+i*.48
        w.rod("Crane lattice cross brace", (sx*.41, .04, z), (-sx*.41, .04, z+.44), .04, "steel", boom)
    w.rod("Steel hoist cable", (sx*.20, .25, -2.75), (sx*.20, .25, 1.60), .021, "recess", boom)
    w.cyl("Crane sheave", (sx*.20, .13, 1.35), .20, .13, "steel", boom, (1, 0, 0))
w.box("Crane mast head", (0, .06, 1.55), (1.06, .41, .28), "armor", boom)
w.box("Hook carrier", (0, .23, -2.82), (.51, .38, .30), "edge", boom)
w.ring("Crane hook eye", (0, .24, -3.08), .15, .047, "steel", boom, (0, 1, 0))
for sx in [-1, 1]:
    ladder((sx*1.01, .73, .49), 1.75, back, .22)

# Sparse industrial plinth: the model, rather than scenery, remains the focal point.
base = assembly("12 Display plinth", (0, 0, -.32))
w.cyl("Machined display plinth", (0, 0, -.22), 4.23, .30, "joint", base, n=96)
w.cyl("Concrete inset", (0, 0, -.05), 4.09, .09, "concrete", base, n=96)
w.ring("Plinth perimeter", (0, 0, -.065), 4.11, .045, "steel", base)
for i in range(32):
    a = i*math.tau/32
    w.box("Perimeter index", (4.18*math.cos(a), 4.18*math.sin(a), -.12),
          (.025, .13, .04), "edge", base, .006, (0, 0, a))

# Normalize foot contact once using evaluated sole vertices, leaving the plinth separate.
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
feet = [o for o in collection.objects if o.name.startswith("Foot structural sole")]
lowest = min((o.matrix_world @ Vector(c))[2] for o in feet for c in o.bound_box)
offset = -.315-lowest
for obj in assemblies.values():
    if obj.parent == root and obj != base:
        obj.location.z += offset
bpy.context.view_layer.update()
for sole in feet:
    leg = sole.parent
    while leg.parent != root:
        leg = leg.parent
    low = min((sole.matrix_world @ Vector(c)).z for c in sole.bound_box)
    leg.location.z += -.315-low
bpy.context.view_layer.update()

def bounds(objects):
    # Rotated object bounding-box corners overestimate the exported geometry.
    pts = []
    for obj in objects:
        if obj.type not in {"MESH", "CURVE"}:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        pts.extend(obj.matrix_world @ v.co for v in mesh.vertices)
        evaluated.to_mesh_clear()
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    return lo, hi


source_objects = list(collection.objects)
lo, hi = bounds(source_objects)
mesh_count = sum(o.type == "MESH" for o in source_objects)
scene["Study"] = "Devastator V1 | Reference-guided clay study"
scene["Scope"] = "Static combined form. No vehicle transformation or physical mechanism validation."
scene["Reference"] = "Rex Hsu / https://www.artstation.com/artwork/w6KbAZ"

# Batch evaluated geometry by assembly and material only for the browser asset.
# The editable Blender source retains every panel, hose, track shoe and fastener.
export_collection = bpy.data.collections.new("Temporary GLB batches")
scene.collection.children.link(export_collection)
buckets = {}
for obj in source_objects:
    if obj.type not in {"MESH", "CURVE"}:
        continue
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    ancestor = obj.parent
    while ancestor and "assembly" not in ancestor:
        ancestor = ancestor.parent
    label = ancestor["assembly"] if ancestor else "Unassigned"
    mat = obj.material_slots[0].material
    key = (label, mat.name)
    vertices, faces, normals = buckets.setdefault(key, ([], [], []))
    start = len(vertices)
    vertices.extend(tuple(obj.matrix_world @ v.co) for v in mesh.vertices)
    normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
    corner_normals = mesh.corner_normals
    for face in mesh.polygons:
        faces.append(tuple(start+i for i in face.vertices))
        normals.extend(tuple((normal_matrix @ corner_normals[i].vector).normalized())
                       for i in face.loop_indices)
    evaluated.to_mesh_clear()
bpy.ops.object.select_all(action="DESELECT")
triangle_count = 0
for (label, material), (vertices, faces, normals) in buckets.items():
    mesh = bpy.data.meshes.new(label+" / "+material)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.normals_split_custom_set(normals)
    mesh.materials.append(w.materials[material])
    triangle_count += sum(len(face)-2 for face in faces)
    obj = bpy.data.objects.new(label+" / "+material, mesh)
    export_collection.objects.link(obj)
    obj["assembly"] = label
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ASSETS / "devastator.glb"), export_format="GLB",
                         use_selection=True, export_extras=True, export_animations=False)
for obj in list(export_collection.objects):
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(data)
bpy.data.collections.remove(export_collection)

scene.render.engine = "CYCLES"
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.render.resolution_x = scene.render.resolution_y = args.resolution
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.fps = 24
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.22, .22, .22, 1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .45
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -.70))
floor = bpy.context.object
floor.name = "Studio ground (not exported)"
floor.data.materials.append(w.material("studio", .065, .0, .77))


def light(name, location, power, size, target):
    bpy.ops.object.light_add(type="AREA", location=location)
    obj = bpy.context.object
    obj.name, obj.data.energy, obj.data.shape = name, power, "DISK"
    obj.data.size = size
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z", "Y").to_euler()


light("Large overhead key", (-6, -8, 15), 2800, 7, (0, 0, 6))
light("Front fill", (7, -10, 8), 1200, 6, (0, 0, 6))
light("Rear rim", (4, 6, 13), 4400, 5, (0, 0, 7))
light("Side strip", (-8, 3, 6), 2100, 5, (0, 0, 6))
bpy.ops.object.camera_add()
camera = bpy.context.object
camera.name = "Inspection camera"
camera.data.type = "ORTHO"
camera.data.clip_end = 250
scene.camera = camera
center = (lo+hi)/2
views = {
    "hero": ((12, -26, 10), (0.6, 0, 5.2), 14.7),
    "front": ((0, -26, 8), (0.6, 0, 5.2), 14.5),
    "rear": ((-14, 24, 12), (0, 0, 5.2), 15.0),
    "detail": ((-9, -15, 12), (-.4, -.05, 8.6), 7.7),
}


def camera_pose(pos, target, scale):
    camera.location = pos
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.ortho_scale = scale


# Use a separate orbit camera so rendering inspection stills never clears motion.
scene.frame_start, scene.frame_end = 1, 241
orbit = bpy.data.objects.new("Turntable orbit", None)
scene.collection.objects.link(orbit)
orbit.location = (0, 0, 5.2)
orbit.empty_display_size = .3
orbit.rotation_euler.z = .43
orbit.keyframe_insert("rotation_euler", frame=1, index=2)
orbit.rotation_euler.z = .43+math.tau
orbit.keyframe_insert("rotation_euler", frame=241, index=2)
for layer in orbit.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in bag.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation = "LINEAR"
orbit_camera = bpy.data.objects.new("Animated turntable camera", camera.data.copy())
scene.collection.objects.link(orbit_camera)
orbit_camera.parent = orbit
orbit_camera.location = (0, -26, 6.8)
orbit_camera.rotation_euler = (-orbit_camera.location).to_track_quat("-Z", "Y").to_euler()
orbit_camera.data.ortho_scale = 15.8
scene.frame_set(1)
camera_pose(*views["hero"])
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.region_3d.view_perspective = "CAMERA"
bpy.ops.wm.save_as_mainfile(filepath=str(DELIVERY / "devastator-clay.blend"), compress=True)
if args.render:
    for view in args.views:
        camera_pose(*views[view])
        scene.render.filepath = str(DELIVERY / f"devastator-{view}.png")
        bpy.ops.render.render(write_still=True)
manifest = {
    "name": "Devastator / V1 clay study", "version": 1, "sourceMeshCount": mesh_count,
    "browserMeshCount": len(buckets), "triangles": triangle_count,
    "assemblies": list(assemblies), "boundsBlender": {"min": list(lo), "max": list(hi)},
    "units": "meters (artistic scale)", "reference": "https://www.artstation.com/artwork/w6KbAZ",
    "scope": "Static combined form. No transformation, collision certification, or final paint.",
    "renderViews": list(views),
    "animation": {"camera": orbit_camera.name, "orbit": orbit.name,
                  "frameStart": 1, "frameEnd": 241, "fps": 24,
                  "scope": "Camera orbit only; static combined robot"},
    "renderSettings": {"engine": "CYCLES", "resolution": args.resolution,
                       "samples": args.samples},
    "files": {},
}
for path in [ASSETS/"devastator.glb", DELIVERY/"devastator-clay.blend",
             ROOT/"scripts/build_devastator.py", ROOT/"scripts/geometry.py",
             ROOT/"scripts/audit_scene.py"]:
    manifest["files"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
if args.render:
    for view in args.views:
        path = DELIVERY / f"devastator-{view}.png"
        manifest["files"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
(ASSETS/"devastator.json").write_text(json.dumps(manifest, indent=2)+"\n")
print(json.dumps(manifest, indent=2))
