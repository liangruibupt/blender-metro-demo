"""V2 metal study: large armor panels, packed PBR maps and guided mechanisms."""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Euler, Matrix, Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metal_surfaces import build_maps
from rig_motion import pose, smooth, ramp, matrices

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
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
PALETTE = {
    "red": ((.23, .016, .024), .84, .26),
    "red_dark": ((.075, .009, .014), .88, .32),
    "blue": ((.018, .040, .115), .86, .27),
    "blue_light": ((.025, .078, .18), .88, .29),
    "silver": ((.43, .47, .52), .98, .28),
    "dark": ((.038, .046, .058), .88, .38),
}
SURFACES, NORMAL = build_maps(ASSETS / "surfaces", PALETTE)


def xyz(point):
    return C @ Vector(point)


def rotation(angles):
    return (C @ Euler(angles, "XYZ").to_matrix() @ C.inverted()).to_quaternion()


def mat(name, color, metal=0.0, rough=.35, emission=0, surface=None, coat=0):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*color, 1)
    value.use_nodes = True
    shader = value.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    shader.inputs["Coat Weight"].default_value = coat
    shader.inputs["Coat Roughness"].default_value = .22
    if surface:
        base, packed = SURFACES[surface]
        color_node = value.node_tree.nodes.new("ShaderNodeTexImage")
        color_node.image = base
        value.node_tree.links.new(color_node.outputs["Color"], shader.inputs["Base Color"])
        packed_node = value.node_tree.nodes.new("ShaderNodeTexImage")
        packed_node.image = packed
        separate = value.node_tree.nodes.new("ShaderNodeSeparateColor")
        value.node_tree.links.new(packed_node.outputs["Color"], separate.inputs["Color"])
        value.node_tree.links.new(separate.outputs["Green"], shader.inputs["Roughness"])
        value.node_tree.links.new(separate.outputs["Blue"], shader.inputs["Metallic"])
        normal_image = value.node_tree.nodes.new("ShaderNodeTexImage")
        normal_image.image = NORMAL
        normal = value.node_tree.nodes.new("ShaderNodeNormalMap")
        normal.inputs["Strength"].default_value = .35
        value.node_tree.links.new(normal_image.outputs["Color"], normal.inputs["Color"])
        value.node_tree.links.new(normal.outputs["Normal"], shader.inputs["Normal"])
    if emission:
        shader.inputs["Emission Color"].default_value = (*color, 1)
        shader.inputs["Emission Strength"].default_value = emission
    return value


M = {
    "red": mat("Weathered crimson alloy", *PALETTE["red"], surface="red", coat=.22),
    "red_dark": mat("Recessed crimson metal", *PALETTE["red_dark"], surface="red_dark"),
    "blue": mat("Deep cobalt alloy", *PALETTE["blue"], surface="blue", coat=.18),
    "blue_light": mat("Cobalt armor plate", *PALETTE["blue_light"], surface="blue_light"),
    "silver": mat("Brushed exposed steel", *PALETTE["silver"], surface="silver"),
    "dark": mat("Gunmetal structure", *PALETTE["dark"], surface="dark"),
    "tire": mat("Tread rubber", (.018, .021, .025), .0, .78),
    "glass": mat("Laminated smoked glass", (.014, .04, .055), .08, .12, coat=.95),
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
    uv = obj.data.uv_layers.active
    for polygon in obj.data.polygons:
        for index, loop in enumerate(polygon.loop_indices):
            uv.data[loop].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][index]
    if bevel:
        modifier = obj.modifiers.new("Machined edge", "BEVEL")
        modifier.width = min(bevel*.38, min(size)*.16)
        modifier.segments = 1 if material in ["red", "red_dark", "blue", "blue_light"] else 2
        obj.modifiers.new("Panel normals", "WEIGHTED_NORMAL")
    return obj


def cylinder(name, pos, radius, depth, material, parent, axis=(1, 0, 0), vertices=24, hollow=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                       location=xyz(pos), end_fill_type="NOTHING" if hollow else "NGON")
    obj = bpy.context.object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = xyz(axis).to_track_quat("Z", "Y")
    finish(obj, name, material, parent)
    if hollow:
        wall = obj.modifiers.new("Tube wall", "SOLIDIFY")
        wall.thickness = .007
    bevel = obj.modifiers.new("Edge bevel", "BEVEL")
    bevel.width = .004 if hollow else .009
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
box("Structural spine", (0, -.15, -.83), (.64, 2.30, .22), "dark", root)
for y in [-.8, -.35, .1, .55]:
    box("Backbone rib", (0, y, -.99), (1.05, .15, .14), "silver", root, .025)
chest = joint("cab_shell", root, (0, 0, 0), explode=(0, .55, -.95), order=4,
              label="Cab shell")
box("Cab rear panel", (0, .32, -.69), (2.66, 1.9, .16), "red", chest)
for side in [-1, 1]:
    box("Cab upper side frame", (side*1.26, .87, -.04), (.16, .76, 1.20), "red", chest)
    box("Side glazing", (side*1.352, .65, .14), (.034, .68, .79), "glass", chest, .04)
    box("Door chrome strip", (side*1.36, .30, .11), (.035, .052, .86), "silver", chest, .01)
    box("Side handle", (side*1.39, .39, -.05), (.05, .05, .25), "silver", chest, .015)
for x in [-.40, .40]:
    box("Cab lower crossmember", (x, -.55, 0), (.50, .18, 1.32), "dark", chest)
for side, tag in [(-1, "left"), (1, "right")]:
    win = joint(f"{tag}_windscreen", root, (side*.65, .65, .72),
                explode=(side*.4, .45, 1.0), order=6, label="Windscreen / chest armor")
    box("Red window frame", (0, 0, 0), (1.27, 1.06, .17), "red", win, .065)
    box("Window rubber gasket", (0, .025, .093), (1.07, .80, .035), "dark", win, .04)
    box("Windshield", (0, .025, .117), (.96, .68, .025), "glass", win, .035)
    wiper = box("Wiper", (.06, -.27, .153), (.61, .026, .025), "dark", win, .01)
    wiper.rotation_mode = "QUATERNION"
    wiper.rotation_quaternion = rotation((0, 0, side*.09))
    roof = joint(f"{tag}_roof", root, (side*.67, 1.26, -.01),
                 explode=(side*.35, 1.20, -.2), order=7, label="Sliding roof hatch",
                 motion={"type": "roof", "side": side})
    # A real central notch clears the neck while the roof is closed in robot form.
    box("Roof outer plate", (side*.1275, 0, 0), (1.055, .14, 1.50), "red", roof, .035)
    for z in [-.505, .505]:
        box("Roof notch bridge", (-side*.5275, 0, z), (.255, .14, .49), "red", roof, .025)
    for x in [-.32, .32]:
        box("Roof marker base", (x, .096, .55), (.15, .075, .13), "dark", roof, .02)
        box("Roof amber marker", (x, .13, .56), (.11, .065, .11), "amber", roof, .02)

head = joint("head", root, (0, 1.45, -.02), (0, -.17, -.02),
             explode=(0, 1.7, .1), interval=(.13, .36), order=8, label="Helmet / optics")
box("Neck column", (0, -.065, 0), (.43, .42, .43), "silver", head)
box("Helmet core", (0, .56, 0), (.98, 1.04, .75), "blue", head, .14)
box("Crown ridge", (0, 1.06, -.01), (.25, .16, .68), "blue_light", head)
box("Dark face recess", (0, .49, .41), (.74, .65, .08), "dark", head, .055)
box("Optic brow", (0, .75, .46), (.82, .12, .16), "blue_light", head, .04)
for side in [-1, 1]:
    box("Eye", (side*.205, .61, .472), (.28, .066, .05), "eye", head, .018)
    box("Ear block", (side*.59, .59, -.07), (.20, .56, .38), "blue", head)
    box("Antenna", (side*.64, .98, -.06), (.105, .64, .17), "blue_light", head, .025)
    cylinder("Ear hinge", (side*.705, .52, -.06), .15, .075, "silver", head)
box("Silver faceplate", (0, .31, .51), (.65, .40, .21), "silver", head, .075)
for x in [-.17, 0, .17]:
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
    shoulder = joint(f"{tag}_shoulder", root, (side*1.93, .68, .02),
                     (side*1.26, -.16, .02), angles=(0, 0, side*.07),
                     explode=(side*1.28, .26, .15), interval=(.53, .83), order=3,
                     label="Shoulder / cab flank", motion={"type": "shoulder", "side": side})
    cylinder("Shoulder bearing", (side*-.36, -.05, 0), .36, .34, "dark", shoulder)
    box("Red shoulder cap", (0, .025, 0), (.95, .52, 1.11), "red", shoulder, .09)
    box("Upper arm beam", (0, -.52, 0), (.50, .65, .76), "dark", shoulder, .045)
    box("Shoulder face inset", (0, .02, .578), (.61, .30, .035), "red_dark", shoulder, .025)
    bolts(shoulder, [-.30, .30], [-.59, -.28], .395)
    cylinder("Upper arm piston", (side*.28, -.65, -.10), .065, .62,
             "silver", shoulder, (0, 1, 0))
    box("Exhaust mount", (side*.45, .0, -.39), (.19, .46, .19), "dark", shoulder)
    cylinder("Chrome exhaust stack", (side*.48, .72, -.4), .105, 1.62,
             "silver", shoulder, (0, 1, 0))
    cylinder("Exhaust opening", (side*.48, 1.54, -.4), .072, .025,
             "dark", shoulder, (0, 1, 0))
    elbow = joint(f"{tag}_forearm", shoulder, (0, -1.03, 0),
                  truck_angles=(math.pi/2, 0, 0), explode=(side*.32, -.60, .30),
                  interval=(.25, .52), order=4, label="Forearm / folding fairing")
    cylinder("Elbow axle", (0, .015, 0), .26, .74, "silver", elbow)
    for x in [-.32, .32]:
        box("Forearm sleeve side", (x, -.60, 0), (.10, 1.05, .91), "red", elbow)
    for z in [-.40, .40]:
        box("Forearm sleeve panel", (0, -.60, z), (.54, 1.05, .13), "red", elbow)
    box("Forearm raised panel", (0, -.56, .49), (.46, .69, .09), "red_dark", elbow)
    for y in [-.38, -.58, -.78]:
        box("Arm vent", (0, y, .547), (.30, .045, .025), "silver", elbow, .01)
    fist = joint(f"{tag}_fist", elbow, (0, -1.28, 0), (0, -.54, 0),
                 explode=(side*.24, -.52, .25), interval=(.02, .19), order=7,
                 label="Retractable fist")
    box("Palm", (0, -.12, 0), (.46, .38, .50), "dark", fist, .045)
    for x in [-.17, -.057, .057, .17]:
        box("Finger", (x, -.20, .26), (.10, .28, .12), "silver", fist, .022)
    box("Thumb", (side*-.215, -.04, .12), (.075, .27, .24), "dark", fist, .022)
    axle = joint(f"{tag}_front_axle", root, (side*1.70, -.05, -1.25),
                 (side*1.94, -1.15, .22), explode=(side*.8, .1, -.7),
                 interval=(.82, .98), order=5, label="Front axle carrier",
                 motion={"type": "axle", "side": side})
    box("Axle bracket", (side*-.10, 0, 0), (.20, .26, .25), "dark", axle)
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
    box("Calf structure", (0, -.82, -.12), (.89, 1.56, .87), "dark", shin, .055)
    for x in [-.46, .46]:
        box("Calf side armor", (x, -.96, -.12), (.09, 1.69, .88), "blue", shin, .05)
    box("Shin front", (0, -.93, .43), (.84, 1.53, .19), "blue_light", shin, .065)
    box("Knee shield", (0, -.12, .47), (1.00, .45, .20), "blue", shin, .06)
    box("Calf rear deck", (0, -.91, -.69), (.88, 1.60, .13), "dark", shin, .04)
    for y in [-.49, -.77, -1.05, -1.33]:
        box("Calf deck rib", (0, y, -.77), (.76, .095, .08), "silver", shin, .015)
    for y in [-.32, -1.68]:
        wheel(f"{tag}_rear_wheel_{int(abs(y)*100)}", shin,
              (side*.70, y, .50), (side*.66, 0, -.12), 6)
    foot = joint(f"{tag}_foot", shin, (0, -1.92, .1),
                 truck_angles=(math.pi/2, 0, 0), explode=(side*.12, -.55, .6),
                 interval=(.55, .78), order=3, label="Foot / rear deck lock")
    cylinder("Ankle pivot", (0, 0, 0), .16, .70, "silver", foot)
    box("Foot sole", (0, -.20, .63), (1.18, .30, 1.20), "dark", foot, .06)
    box("Blue toe", (0, -.03, .90), (1.16, .34, .90), "blue", foot, .055)
    box("Foot instep", (0, -.10, .19), (.97, .26, .32), "blue", foot, .045)
    for x in [-.28, .28]:
        box("Toe armor line", (x, .15, .90), (.035, .025, .67), "silver", foot, .007)
    box("Rear red lens", (0, -.08, 1.38), (.64, .16, .055), "red", foot, .02)

# Solve a deterministic ground-contact curve from actual evaluated vertices.
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
contact_points = {}
for obj in MODEL.objects:
    if obj.type != "MESH":
        continue
    owner = obj.parent
    while owner and not owner.get("rigId"):
        owner = owner.parent
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    local = np.asarray(owner.matrix_world.inverted() @ obj.matrix_world)
    points = np.asarray([tuple(vertex.co) for vertex in mesh.vertices])
    transformed = points @ local[:3, :3].T+local[:3, 3]
    contact_points.setdefault(owner["rigId"], []).append(transformed)
    evaluated.to_mesh_clear()
contact_points = {key: np.concatenate(value) for key, value in contact_points.items()}
height_curve = []
for sample in range(257):
    frame = matrices(JOINTS, sample/256)
    minimum = min(float(np.min(points @ np.asarray(frame[key])[2, :3]+frame[key][2][3]))
                  for key, points in contact_points.items())
    height_curve.append(float(frame["chassis"][2][3]+.04-minimum))
JOINTS[0]["motion"] = {"type": "grounded", "heightCurve": height_curve}
JOINTS[0]["robot"][1] = height_curve[0]
JOINTS[0]["truck"][1] = height_curve[-1]

LINKS = [
    dict(id="head_guide", base="chassis", target="head",
         start=[0, -1.10, -.30], end=[0, -.065, -.15], radius=.070),
]
for side, tag in [(-1, "left"), (1, "right")]:
    LINKS.extend([
        dict(id=f"{tag}_shoulder_guide", base="chassis", target=f"{tag}_shoulder",
             start=[side*1.0, .25, -.55], end=[0, 0, -.30], radius=.075),
        dict(id=f"{tag}_axle_guide", base="chassis", target=f"{tag}_front_axle",
             start=[side*.65, -.70, -.70], end=[side*-.16, 0, 0], radius=.085),
        dict(id=f"{tag}_waist_guide", base="chassis", target="pelvis",
             start=[side*.55, -.80, -.55], end=[side*.30, -.02, 0], radius=.065),
    ])

LINK_NODES = {}
for link in LINKS:
    distances = []
    for index in range(161):
        frame = matrices(JOINTS, index/160)
        start = xyz(link["start"])
        end = frame[link["base"]].inverted() @ frame[link["target"]] @ xyz(link["end"])
        distances.append((end-start).length)
    minimum, maximum = min(distances), max(distances)
    stages = max(2, math.ceil(maximum/(minimum*.82)+.25))
    assert stages <= 6, f"Unbuildable telescoping range: {link['id']}"
    link.update(stages=stages, stageLength=maximum/(stages-.25),
                minLength=minimum, maxLength=maximum)
    group = bpy.data.objects.new("Guide_"+link["id"], None)
    MODEL.objects.link(group)
    group.parent = NODES[link["base"]]
    group["linkId"] = link["id"]
    NODES["guide_"+link["id"]] = group
    parts = []
    for index in range(stages):
        stage = cylinder(f"{link['id']}_stage_{index}", (0, link["stageLength"]/2, 0),
                         link["radius"]*(.77**index), link["stageLength"],
                         "dark" if index == 0 else "silver", "guide_"+link["id"],
                         axis=(0, 1, 0), hollow=index < stages-1)
        stage["linkStage"] = index
        parts.append(stage)
    end_cap = cylinder("Guide eyelet", (0, 0, 0), link["radius"]*1.4, .10,
                       "silver", "guide_"+link["id"])
    end_cap["linkEnd"] = True
    cylinder("Guide pivot", (0, 0, 0), link["radius"]*1.5, .12,
             "dark", "guide_"+link["id"])
    LINK_NODES[link["id"]] = (group, parts, end_cap)


def apply_pose(transform=0, explosion=0, assembly=None, keyframe=None):
    for entry in JOINTS:
        obj = NODES[entry["id"]]
        obj.location, obj.rotation_quaternion = pose(entry, transform, explosion, assembly)
        if keyframe is not None:
            obj.keyframe_insert("location", frame=keyframe)
            obj.keyframe_insert("rotation_quaternion", frame=keyframe)
    frame = matrices(JOINTS, transform)
    for link in LINKS:
        group, parts, end_cap = LINK_NODES[link["id"]]
        start = xyz(link["start"])
        end = frame[link["base"]].inverted() @ frame[link["target"]] @ xyz(link["end"])
        delta = end-start
        group.location = start
        group.rotation_mode = "QUATERNION"
        group.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(delta.normalized())
        for index, part in enumerate(parts):
            part.location.z = (delta.length-link["stageLength"])*index/(link["stages"]-1)+link["stageLength"]/2
            if keyframe is not None:
                part.keyframe_insert("location", frame=keyframe)
        end_cap.location.z = delta.length
        if keyframe is not None:
            group.keyframe_insert("location", frame=keyframe)
            group.keyframe_insert("rotation_quaternion", frame=keyframe)
            end_cap.keyframe_insert("location", frame=keyframe)


# Export one mesh set, with stable joint identifiers, before adding studio objects.
apply_pose()
bpy.ops.object.select_all(action="DESELECT")
for obj in MODEL.objects:
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ASSETS / "optimus.glb"), export_format="GLB",
                          use_selection=True, export_extras=True, export_animations=False,
                          export_apply=True)
manifest = {"name": "Optimus Prime / V2 metal study", "version": 2, "units": "meters",
            "coordinateSystem": "right-handed Y-up, front +Z", "joints": JOINTS,
            "links": LINKS, "finish": "Packed brushed-metal PBR surfaces",
            "grounding": {"samples": len(height_curve), "clearance": .04},
            "meshCount": sum(obj.type == "MESH" for obj in MODEL.objects),
            "note": "Original fan study; simplified mechanical motion, not a production toy mechanism."}
(ASSETS / "optimus-rig.json").write_text(json.dumps(manifest, indent=2)+"\n")

SCENE.render.engine = "CYCLES"
SCENE.cycles.samples = 48
SCENE.render.resolution_x = 1100
SCENE.render.resolution_y = 1100
SCENE.render.resolution_percentage = 100
SCENE.render.fps = 24
SCENE.world.use_nodes = True
SCENE.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.28, .30, .34, 1)
SCENE.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .65
SCENE.view_settings.view_transform = "AgX"
bpy.ops.mesh.primitive_plane_add(size=200)
floor = bpy.context.object
floor.name = "Studio ground"
floor.data.materials.append(mat("Studio neutral", (.25, .28, .33), .12, .65))


def area(name, pos, power, size):
    bpy.ops.object.light_add(type="AREA", location=xyz(pos))
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = size
    light.rotation_euler = (xyz((0, 3, 0))-light.location).to_track_quat("-Z", "Y").to_euler()


area("Softbox key", (5, 13, 9), 2300, 5)
area("Softbox fill", (-7, 8, 4), 1300, 6)
area("Rim", (3, 11, -7), 3200, 4)
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
