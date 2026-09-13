"""Original G1-inspired study; Blender generates the shared articulated asset."""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "public" / "assets"
DELIVERY = ROOT / "deliverables"
ASSETS.mkdir(parents=True, exist_ok=True)
DELIVERY.mkdir(exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument("--render", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
SCENE = bpy.context.scene
C = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))
JOINTS = []
NODES = {}
MODEL = bpy.data.collections.new("OPTIMUS / Articulated assemblies")
SCENE.collection.children.link(MODEL)


def xyz(point):
    return C @ Vector(point)


def rotation(angles):
    return (C @ Euler(angles, "XYZ").to_matrix() @ C.inverted()).to_quaternion()


def mat(name, color, metal=0.0, rough=.35, emission=0):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*color, 1)
    value.use_nodes = True
    shader = value.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    if emission:
        shader.inputs["Emission Color"].default_value = (*color, 1)
        shader.inputs["Emission Strength"].default_value = emission
    return value


M = {
    "red": mat("Signal red enamel", (.58, .028, .038), .38, .28),
    "red_dark": mat("Crimson panel inset", (.26, .014, .025), .3),
    "blue": mat("Cobalt enamel", (.018, .065, .32), .5, .29),
    "blue_light": mat("Cobalt chamfer", (.035, .15, .52), .45),
    "silver": mat("Satin aluminium", (.56, .63, .68), .8, .25),
    "dark": mat("Joint graphite", (.033, .043, .055), .6, .38),
    "tire": mat("Tread rubber", (.018, .021, .025), .0, .78),
    "glass": mat("Cyan smoked glazing", (.025, .23, .33), .5, .15),
    "eye": mat("Optic ice blue", (.2, .79, 1), .25, .2, 2.5),
    "white": mat("Ivory headlight", (.88, .94, 1), .2, .2, .5),
    "amber": mat("Amber marker", (1, .34, .045), .3, .3, .4),
}


def joint(name, parent, robot, truck=None, angles=None, truck_angles=None,
          explode=(0, 0, 0), interval=(.2, .8), order=0, label=None, motion=None):
    entry = dict(id=name, parent=parent, robot=list(robot), truck=list(truck or robot),
                 angles=list(angles or (0, 0, 0)), truckAngles=list(truck_angles or (0, 0, 0)),
                 explode=list(explode), interval=list(interval), order=order,
                 label=label or name.replace("_", " ").title())
    if motion:
        entry["motion"] = motion
    JOINTS.append(entry)
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = .22
    MODEL.objects.link(obj)
    if parent:
        obj.parent = NODES[parent]
    obj["rigId"] = name
    obj.location = xyz(robot)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = rotation(entry["angles"])
    NODES[name] = obj
    return name


def finish(obj, name, material, parent):
    obj.name = name
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    MODEL.objects.link(obj)
    obj.data.materials.append(M[material])
    obj.parent = NODES[parent]
    return obj


def box(name, pos, size, material, parent, bevel=.045):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz(pos))
    obj = bpy.context.object
    obj.scale = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(obj, name, material, parent)
    if bevel:
        modifier = obj.modifiers.new("Machined edge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new("Panel normals", "WEIGHTED_NORMAL")
    return obj


def cylinder(name, pos, radius, depth, material, parent, axis=(1, 0, 0), vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                       location=xyz(pos))
    obj = bpy.context.object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = xyz(axis).to_track_quat("Z", "Y")
    finish(obj, name, material, parent)
    bevel = obj.modifiers.new("Edge bevel", "BEVEL")
    bevel.width = .018
    bevel.segments = 2
    obj.modifiers.new("Cylinder normals", "WEIGHTED_NORMAL")
    return obj


def bolts(parent, x_values, y_values, z):
    for x in x_values:
        for y in y_values:
            cylinder("Hex fastener", (x, y, z), .035, .025, "silver", parent, (0, 0, 1), 6)


def wheel(name, parent, pos, explode, order):
    node = joint(name, parent, pos, explode=explode, order=order, label="Wheel / hub")
    cylinder("Tire", (0, 0, 0), .63, .36, "tire", node, vertices=40)
    for side in [-1, 1]:
        cylinder("Sidewall ring", (side*.181, 0, 0), .48, .025, "dark", node, vertices=40)
        cylinder("Alloy hub", (side*.20, 0, 0), .34, .035, "silver", node, vertices=32)
        cylinder("Hub cap", (side*.227, 0, 0), .14, .038, "dark", node)
        for i in range(8):
            a = 2*math.pi*i/8
            cylinder("Wheel stud", (side*.247, .235*math.sin(a), .235*math.cos(a)),
                     .028, .035, "silver", node, vertices=6)
    for i in range(32):
        a = 2*math.pi*i/32
        obj = box("Tread block", (0, .62*math.cos(a), .62*math.sin(a)),
                  (.33, .035, .067), "tire", node, .01)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = rotation((a, 0, 0))
    return node


root = joint("chassis", None, (0, 5.3, 0), (0, 1.8, 1.35), interval=(.50, .96), explode=(0, 2.2, 0),
             order=8, label="Primary chassis", motion={"type": "lift"})
box("Structural spine", (0, -.15, -.52), (.64, 2.30, .28), "dark", root)
for y in [-.8, -.35, .1, .55]:
    box("Backbone rib", (0, y, -.71), (1.05, .15, .18), "silver", root, .025)
chest = joint("cab_shell", root, (0, 0, 0), explode=(0, .55, -.95), order=4,
              label="Cab shell")
box("Cab rear panel", (0, .32, -.69), (2.66, 1.9, .16), "red", chest)
for side in [-1, 1]:
    box("Cab side", (side*1.26, .29, -.04), (.16, 1.98, 1.20), "red", chest)
    box("Side glazing", (side*1.352, .65, .14), (.034, .68, .79), "glass", chest, .04)
    box("Door chrome strip", (side*1.36, -.08, .11), (.035, .052, .86), "silver", chest, .01)
    box("Side handle", (side*1.39, .09, -.05), (.05, .05, .25), "silver", chest, .015)
box("Cab lower crossmember", (0, -.55, 0), (2.60, .18, 1.32), "red_dark", chest)
for side, tag in [(-1, "left"), (1, "right")]:
    win = joint(f"{tag}_windscreen", root, (side*.65, .65, .72),
                explode=(side*.4, .45, 1.0), order=6, label="Windscreen / chest armor")
    box("Red window frame", (0, 0, 0), (1.27, 1.06, .17), "red", win, .065)
    box("Window rubber gasket", (0, .025, .093), (1.07, .80, .035), "dark", win, .04)
    box("Windshield", (0, .025, .117), (.96, .68, .025), "glass", win, .035)
    box("Window glint", (-.36, .13, .134), (.026, .39, .008), "eye", win, .005)
    wiper = box("Wiper", (.06, -.27, .153), (.61, .026, .025), "dark", win, .01)
    wiper.rotation_mode = "QUATERNION"
    wiper.rotation_quaternion = rotation((0, 0, side*.09))
    roof = joint(f"{tag}_roof", root, (side*.67, 1.26, -.01),
                 explode=(side*.35, 1.20, -.2), order=7, label="Sliding roof hatch",
                 motion={"type": "roof", "side": side})
    box("Roof hatch", (0, 0, 0), (1.31, .14, 1.50), "red", roof, .055)
    for x in [-.32, .32]:
        box("Roof marker base", (x, .096, .55), (.15, .075, .13), "dark", roof, .02)
        box("Roof amber marker", (x, .13, .56), (.11, .065, .11), "amber", roof, .02)

head = joint("head", root, (0, 1.57, -.02), (0, -.17, -.02),
             explode=(0, 1.7, .1), interval=(.13, .36), order=8, label="Helmet / optics")
box("Neck column", (0, -.11, 0), (.43, .56, .43), "silver", head)
box("Helmet core", (0, .56, 0), (.98, 1.04, .75), "blue", head, .14)
box("Crown ridge", (0, 1.06, -.01), (.25, .16, .68), "blue_light", head)
box("Dark face recess", (0, .49, .41), (.74, .65, .08), "dark", head, .055)
box("Optic brow", (0, .75, .46), (.82, .12, .16), "blue_light", head, .04)
for side in [-1, 1]:
    box("Eye", (side*.205, .61, .472), (.29, .102, .05), "eye", head, .018)
    box("Ear block", (side*.59, .59, -.07), (.20, .56, .38), "blue", head)
    box("Antenna", (side*.64, .98, -.06), (.105, .64, .17), "blue_light", head, .025)
    cylinder("Ear hinge", (side*.705, .52, -.06), .15, .075, "silver", head)
box("Silver faceplate", (0, .31, .51), (.65, .40, .21), "silver", head, .075)
for x in [-.20, -.10, 0, .10, .20]:
    box("Mask flute", (x, .31, .621), (.018, .28, .012), "dark", head, .004)

grille = joint("grille", root, (0, -.53, .75), explode=(0, -.15, 1.28), order=5,
               label="Grille / abdominal armor")
box("Grille surround", (0, 0, 0), (2.62, 1.10, .19), "silver", grille, .06)
box("Grille black inset", (0, .02, .11), (1.62, .84, .04), "dark", grille)
for y in [-.30, -.15, 0, .15, .30]:
    box("Horizontal grille blade", (0, y, .155), (1.53, .063, .045), "silver", grille, .012)
for side in [-1, 1]:
    box("Headlight recess", (side*1.04, .04, .115), (.34, .54, .055), "dark", grille, .035)
    for y in [-.11, .17]:
        box("Headlight lens", (side*1.04, y, .154), (.265, .18, .065), "white", grille, .03)
box("Bumper", (0, -.70, .04), (2.89, .24, .43), "silver", grille, .04)
bolts(grille, [-1.25, 1.25], [-.42, .42], .13)

pelvis = joint("pelvis", root, (0, -1.40, -.10), (0, -.45, -.88),
               explode=(0, -.35, -.9), interval=(.4, .82), order=0, label="Hip / fifth-wheel carrier")
box("Pelvis block", (0, -.02, 0), (1.65, .59, .88), "dark", pelvis, .10)
box("Waist fascia", (0, -.05, .50), (1.55, .44, .20), "silver", pelvis)
box("Belt center", (0, -.05, .63), (.37, .29, .07), "amber", pelvis, .025)
for side, tag in [(-1, "left"), (1, "right")]:
    shoulder = joint(f"{tag}_shoulder", root, (side*1.87, .68, -.04),
                     (side*1.26, .30, -.30), angles=(0, 0, side*.07),
                     explode=(side*1.28, .26, .15), interval=(.53, .83), order=3,
                     label="Shoulder / cab flank", motion={"type": "shoulder", "side": side})
    cylinder("Shoulder bearing", (side*-.36, -.05, 0), .36, .34, "dark", shoulder)
    box("Red shoulder cap", (0, .025, 0), (.95, .52, 1.11), "red", shoulder, .09)
    box("Upper arm", (0, -.52, 0), (.76, .65, .76), "red", shoulder, .06)
    box("Shoulder face inset", (0, .02, .578), (.61, .30, .035), "red_dark", shoulder, .025)
    bolts(shoulder, [-.30, .30], [-.59, -.28], .395)
    cylinder("Upper arm piston", (side*.41, -.65, -.10), .072, .62,
             "silver", shoulder, (0, 1, 0))
    box("Exhaust mount", (side*.45, .0, -.39), (.19, .46, .19), "dark", shoulder)
    cylinder("Chrome exhaust stack", (side*.48, .72, -.4), .105, 1.62,
             "silver", shoulder, (0, 1, 0))
    cylinder("Exhaust opening", (side*.48, 1.54, -.4), .072, .025,
             "dark", shoulder, (0, 1, 0))
    elbow = joint(f"{tag}_forearm", shoulder, (0, -1.03, 0),
                  truck_angles=(math.pi/2, 0, 0), explode=(side*.32, -.60, .30),
                  interval=(.25, .52), order=4, label="Forearm / folding fairing")
    cylinder("Elbow axle", (0, .015, 0), .26, .89, "silver", elbow)
    for x in [-.37, .37]:
        box("Forearm sleeve side", (x, -.60, 0), (.14, 1.05, .91), "red", elbow)
    for z in [-.40, .40]:
        box("Forearm sleeve panel", (0, -.60, z), (.66, 1.05, .13), "red", elbow)
    box("Forearm raised panel", (0, -.56, .49), (.46, .69, .09), "red_dark", elbow)
    for y in [-.38, -.58, -.78]:
        box("Arm vent", (0, y, .547), (.30, .045, .025), "silver", elbow, .01)
    fist = joint(f"{tag}_fist", elbow, (0, -1.28, 0), (0, -.54, 0),
                 explode=(side*.24, -.52, .25), interval=(.02, .19), order=7,
                 label="Retractable fist")
    box("Palm", (0, -.12, 0), (.60, .43, .57), "blue", fist, .065)
    for x in [-.22, -.075, .075, .22]:
        box("Finger", (x, -.23, .32), (.13, .34, .18), "blue_light", fist, .03)
    box("Thumb", (side*-.34, -.04, .15), (.16, .32, .30), "blue", fist, .04)
    axle = joint(f"{tag}_front_axle", root, (side*1.44, -.05, -.91),
                 (side*1.48, -1.15, .22), explode=(side*.8, .1, -.7),
                 interval=(.56, .91), order=5, label="Front axle carrier")
    box("Axle bracket", (side*-.21, 0, 0), (.37, .26, .25), "dark", axle)
    wheel(f"{tag}_front_wheel", axle, (0, 0, 0), (side*.45, 0, 0), 6)
    hip = joint(f"{tag}_hip", pelvis, (side*.69, -.20, 0),
                truck_angles=(math.pi/2, 0, 0), explode=(side*.65, -.35, .12),
                interval=(.31, .73), order=1, label="Hip hinge / frame rail")
    cylinder("Hip bearing", (0, -.04, 0), .30, .94, "silver", hip)
    box("Thigh structural beam", (0, -.68, 0), (.68, 1.18, .62), "silver", hip)
    box("Thigh face armor", (0, -.66, .39), (.82, .94, .20), "silver", hip)
    for y in [-.41, -.72, -.95]:
        box("Thigh rib", (0, y, .51), (.59, .06, .03), "dark", hip, .01)
    shin = joint(f"{tag}_shin", hip, (0, -1.24, 0), explode=(side*.23, -.88, -.25),
                 order=2, label="Lower leg / rear chassis")
    cylinder("Knee joint", (0, -.01, 0), .28, 1.06, "dark", shin)
    box("Blue calf", (0, -.95, -.12), (1.02, 1.82, .97), "blue", shin, .11)
    box("Shin front", (0, -.93, .43), (.84, 1.53, .19), "blue_light", shin, .065)
    box("Knee shield", (0, -.12, .47), (1.00, .45, .20), "blue", shin, .06)
    box("Calf rear deck", (0, -.91, -.69), (.88, 1.60, .13), "dark", shin, .04)
    for y in [-.49, -.77, -1.05, -1.33]:
        box("Calf deck rib", (0, y, -.77), (.76, .095, .08), "silver", shin, .015)
    for y in [-.46, -1.52]:
        wheel(f"{tag}_rear_wheel_{int(abs(y)*100)}", shin,
              (side*.70, y, .50), (side*.66, 0, -.12), 6)
    foot = joint(f"{tag}_foot", shin, (0, -1.92, .1),
                 truck_angles=(-math.pi/2, 0, 0), explode=(side*.12, -.55, .6),
                 interval=(.08, .27), order=3, label="Foot / rear deck lock")
    box("Foot sole", (0, -.18, .32), (1.18, .37, 1.64), "dark", foot, .08)
    box("Blue toe", (0, .015, .63), (1.16, .36, 1.07), "blue", foot, .11)
    box("Foot instep", (0, .06, -.07), (.97, .46, .70), "blue", foot, .09)
    for x in [-.28, .28]:
        box("Toe armor line", (x, .20, .72), (.035, .025, .67), "silver", foot, .007)
    box("Rear red lens", (0, -.08, -.52), (.64, .16, .055), "red", foot, .02)


def smooth(value):
    value = min(1, max(0, value))
    return value*value*(3-2*value)


def ramp(value, start, end):
    return smooth((value-start)/(end-start))


def pose(entry, transform=0, explosion=0, assembly=None):
    t = ramp(transform, *entry["interval"])
    position = Vector(entry["robot"]).lerp(Vector(entry["truck"]), t)
    a = Euler(entry["angles"], "XYZ").to_quaternion()
    b = Euler(entry["truckAngles"], "XYZ").to_quaternion()
    orient = a.slerp(b, t)
    motion = entry.get("motion", {})
    if motion.get("type") == "roof":
        position.x += motion["side"]*.84*ramp(transform, .02, .12)*(1-ramp(transform, .38, .53))
    if motion.get("type") == "shoulder":
        position.x += motion["side"]*.48*ramp(transform, .12, .25)*(1-ramp(transform, .50, .8))
    if motion.get("type") == "lift":
        position.y += .30*ramp(transform, .02, .10)*(1-ramp(transform, .35, .50))
    amount = explosion
    if assembly is not None:
        amount = 1-ramp(assembly, entry["order"]*.075, entry["order"]*.075+.36)
    position += Vector(entry["explode"])*amount
    return xyz(position), (C @ orient.to_matrix() @ C.inverted()).to_quaternion()


def apply_pose(transform=0, explosion=0, assembly=None, keyframe=None):
    for entry in JOINTS:
        obj = NODES[entry["id"]]
        obj.location, obj.rotation_quaternion = pose(entry, transform, explosion, assembly)
        if keyframe is not None:
            obj.keyframe_insert("location", frame=keyframe)
            obj.keyframe_insert("rotation_quaternion", frame=keyframe)


# Export one mesh set, with stable joint identifiers, before adding studio objects.
apply_pose()
bpy.ops.object.select_all(action="DESELECT")
for obj in MODEL.objects:
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ASSETS / "optimus.glb"), export_format="GLB",
                          use_selection=True, export_extras=True, export_animations=False,
                          export_apply=True)
manifest = {"name": "G1-inspired Optimus Prime", "version": 1, "units": "meters",
            "coordinateSystem": "right-handed Y-up, front +Z", "joints": JOINTS,
            "meshCount": sum(obj.type == "MESH" for obj in MODEL.objects),
            "note": "Original fan study; simplified mechanical motion, not a production toy mechanism."}
(ASSETS / "optimus-rig.json").write_text(json.dumps(manifest, indent=2)+"\n")

SCENE.render.engine = "CYCLES"
SCENE.cycles.samples = 24
SCENE.render.resolution_x = 1100
SCENE.render.resolution_y = 1100
SCENE.render.resolution_percentage = 100
SCENE.render.fps = 24
SCENE.world.color = (.27, .27, .27)
SCENE.view_settings.view_transform = "AgX"
bpy.ops.mesh.primitive_plane_add(size=200)
floor = bpy.context.object
floor.name = "Studio ground"
floor.data.materials.append(mat("Studio chalk", (.68, .71, .72), 0, .7))


def area(name, pos, power, size):
    bpy.ops.object.light_add(type="AREA", location=xyz(pos))
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = size
    light.rotation_euler = (xyz((0, 3, 0))-light.location).to_track_quat("-Z", "Y").to_euler()


area("Softbox key", (5, 13, 9), 1800, 7)
area("Softbox fill", (-7, 8, 4), 1400, 6)
area("Rim", (3, 11, -7), 2200, 5)
bpy.ops.object.camera_add(location=xyz((11, 8, 15)))
camera = bpy.context.object
camera.name = "Showcase camera"
camera.data.lens = 50
SCENE.camera = camera


def camera_pose(position, target):
    camera.location = xyz(position)
    camera.rotation_euler = (xyz(target)-camera.location).to_track_quat("-Z", "Y").to_euler()


if args.render:
    for name, t, pos, target in [
        ("optimus-robot", 0, (11, 8, 15), (0, 4, 0)),
        ("optimus-truck", 1, (9, 5, 11), (0, 1.5, -.1)),
    ]:
        apply_pose(t)
        camera_pose(pos, target)
        SCENE.render.filepath = str(DELIVERY / f"{name}.png")
        bpy.ops.render.render(write_still=True)

# The editable Blender file includes the same staged joints, plus a camera orbit.
SCENE.frame_start = 1
SCENE.frame_end = 1920
for frame in sorted(set(list(range(1, 1921, 8))+[1920])):
    sec = (frame-1)/24
    transform = ramp(sec, 44, 58)*(1-ramp(sec, 66, 79))
    explosion = ramp(sec, 12, 20) if sec < 28 else 0
    assembly = (sec-28)/12 if 28 <= sec < 40 else None
    apply_pose(transform, explosion, assembly, frame)
    extent = explosion if assembly is None else 1-ramp(assembly, .58, 1)
    radius = 18+4*extent-5*transform
    angle = .55+2*math.pi*sec/24
    target = Vector((0, 4+2*extent-2.6*transform, 0))
    camera_pose((math.sin(angle)*radius, 8+3*extent-3*transform, math.cos(angle)*radius), target)
    camera.keyframe_insert("location", frame=frame)
    camera.keyframe_insert("rotation_euler", frame=frame)
SCENE.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(DELIVERY / "optimus-prime.blend"), compress=True)
print(json.dumps({"joints": len(JOINTS), "meshes": manifest["meshCount"],
                  "blend": str(DELIVERY / "optimus-prime.blend")}))
