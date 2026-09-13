"""Reproducible concept metro asset. Run with Blender --background --python."""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--render", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
ASSETS = ROOT / "public" / "assets"
DELIVERY = ROOT / "deliverables"
ASSETS.mkdir(parents=True, exist_ok=True)
DELIVERY.mkdir(exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.materials):
    bpy.data.materials.remove(block)


def material(name, color, metal=0, rough=0.45, emission=0, alpha=1):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, alpha)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, alpha)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Alpha"].default_value = alpha
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emission
    if alpha < 1:
        mat.surface_render_method = "DITHERED"
    return mat


M = {
    "shell": material("Pearl aluminium", (0.72, 0.78, 0.79), 0.58, 0.29),
    "white": material("Porcelain interior", (0.86, 0.88, 0.85), 0.08),
    "teal": material("Jade livery", (0.018, 0.37, 0.33), 0.34, 0.3),
    "lime": material("Wayfinding citron", (0.77, 0.92, 0.22), 0.08),
    "black": material("Graphite rubber", (0.022, 0.033, 0.039), 0.12),
    "steel": material("Brushed stainless steel", (0.45, 0.51, 0.55), 0.78, 0.25),
    "glass": material("Smoked window glass", (0.12, 0.25, 0.28), 0.2, 0.12, alpha=0.26),
    "seat": material("Jade molded seat", (0.025, 0.32, 0.30), 0.14, 0.35),
    "priority": material("Priority seats", (0.67, 0.37, 0.15), 0.06),
    "floor": material("Speckled graphite floor", (0.22, 0.27, 0.28), 0.05, 0.85),
    "light": material("Warm LED", (1.0, 0.94, 0.76), 0, 0.35, emission=2.7),
    "screen": material("LCD black", (0.007, 0.028, 0.035), 0.1, 0.23),
    "cyan": material("LCD mint", (0.17, 0.9, 0.65), 0, 0.4, emission=0.6),
    "red": material("Safety red", (0.8, 0.045, 0.025), 0, 0.4),
    "yellow": material("Safety yellow", (0.96, 0.73, 0.05), 0, 0.5),
    "concrete": material("Track concrete", (0.36, 0.40, 0.40), 0, 0.95),
}
# Subtle physical-scale floor texture remains editable in the Blender original.
floor_nodes = M["floor"].node_tree
noise = floor_nodes.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 160
bump = floor_nodes.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.16
bump.inputs["Distance"].default_value = 0.01
floor_nodes.links.new(noise.outputs["Fac"], bump.inputs["Height"])
floor_nodes.links.new(bump.outputs["Normal"], floor_nodes.nodes["Principled BSDF"].inputs["Normal"])

collections = {}
for name in ["01_Shell", "02_Interior", "03_Cab", "04_Roof", "05_Undercarriage", "06_Doors", "07_Track", "08_Studio"]:
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    collections[name] = col
current = "01_Shell"


def finish(obj, name, mat, parent=None):
    obj.name = name
    obj["zone"] = current
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    collections[current].objects.link(obj)
    if mat:
        obj.data.materials.append(M.get(mat, mat))
    if parent:
        obj.parent = parent
    return obj


def box(name, pos, size, mat, bevel=0.02, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(obj, name, mat, parent)
    if bevel:
        modifier = obj.modifiers.new("Machined edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        modifier = obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def rod(name, a, b, radius, mat, vertices=12, parent=None):
    a, b = Vector(a), Vector(b)
    vec = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=vec.length, location=(a+b)/2)
    obj = bpy.context.object
    obj.rotation_euler = vec.to_track_quat("Z", "Y").to_euler()
    finish(obj, name, mat, parent)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def mesh(name, verts, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collections[current].objects.link(obj)
    obj.data.materials.append(M[mat])
    return obj


def text(name, value, pos, size=0.12, mat="black", rotation=(0, 0, 0), parent=None, align="CENTER"):
    bpy.ops.object.text_add(location=pos, rotation=rotation)
    obj = bpy.context.object
    obj.data.body = value
    obj.data.size = size
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.extrude = 0.0005
    obj.data.resolution_u = 4
    finish(obj, name, mat, parent)
    return obj


def side_text(value, x, y, z, size=0.12, mat="white", parent=None, inward=False):
    rot = (math.pi/2, 0, 0) if y < 0 else (math.pi/2, 0, math.pi)
    if inward:
        rot = (math.pi/2, 0, math.pi) if y < 0 else (math.pi/2, 0, 0)
    return text("Label_" + value.replace("\n", "_"), value, (x, y, z), size, mat, rot, parent)


def front_text(value, x, y, z, size=0.12, mat="cyan"):
    return text("Front_" + value, value, (x,y,z), size, mat, (math.pi/2, 0, math.pi/2))


def frame_window(name, x, y, z, width, height, parent=None):
    for dx in [-width/2, width/2]:
        box(name+"_jamb", (x+dx,y,z), (.045,.065,height+.045), "black", .02, parent)
    for dz in [-height/2,height/2]:
        box(name+"_sill", (x,y,z+dz), (width,.065,.045), "black", .02, parent)
    box(name+"_Glass", (x,y,z), (width-.035,.025,height-.035), "glass", .01, parent)


# Carbody: separate panels leave real openings for windows and sliding doors.
box("Main chassis", (0,0,.98), (18.6,2.91,.27), "black", .09)
box("Passenger floor", (-.8,0,1.145), (16.6,2.79,.12), "floor", .02)
box("Cab floor", (8.15,0,1.145), (2.15,2.7,.12), "floor")
door_x = [-6.1, -.8, 4.5]
door_width = 1.44
wall_intervals = [(-9.05,-6.82),(-5.38,-1.52),(-.08,3.78),(5.22,7.25)]
windows = [(-8.0,1.40),(-3.45,2.86),(1.85,2.86),(6.18,1.10)]
for side in [-1, 1]:
    y = side*1.46
    for a,b in wall_intervals:
        box("Shell_lower_panel", ((a+b)/2,y,1.60), (b-a,.105,.9), "shell", .035)
        box("Livery_jade_belt", ((a+b)/2,y+side*.06,1.84), (b-a,.019,.27), "teal", .012)
        box("Livery_citron_pinstripe", ((a+b)/2,y+side*.072,1.67), (b-a,.012,.037), "lime", .003)
        box("Interior_wall", ((a+b)/2,y-side*.064,1.63), (b-a,.025,.80), "white")
    box("Shell_header", (-.90,y,3.32), (16.35,.12,.31), "shell", .045)
    for x,w in windows:
        frame_window("Passenger_window", x,y,2.60,w,1.05)
    spans = [(-9.075,-8.70),(-7.30,-6.82),(-5.38,-4.88),(-2.02,-1.52),
             (-.08,.42),(3.28,3.78),(5.22,5.63),(6.73,7.28)]
    for a,b in spans:
        box("Shell_window_pillar", ((a+b)/2,y,2.60), (b-a,.12,1.15), "shell", .025)
    side_text("M  /  01", -8.0,y+side*.071,1.40,.18,"teal")
    side_text("METRO  ATELIER", 1.85,y+side*.071,1.40,.105,"black")
    side_text("001-A", 6.15,y+side*.071,1.39,.12,"black")

# Sliding door leaf groups are exported intact for the interactive door animation.
current = "06_Doors"
for side in [-1,1]:
    for index,x in enumerate(door_x):
        box("Door_portal", (x,side*1.47,3.20), (1.51,.16,.10), "black")
        box("Door_threshold", (x,side*1.43,1.23), (1.47,.24,.045), "steel", .007)
        box("Door_safety_edge", (x,side*1.30,1.242), (1.44,.06,.015), "yellow", .002)
        for direction in [-1,1]:
            group = bpy.data.objects.new(f"Door_{side}_{index}_{direction}", None)
            collections[current].objects.link(group)
            group["slide"] = direction*.70
            group["side"] = side
            px = x+direction*.36
            y = side*1.47
            box("Door_leaf_bottom", (px,y,1.67), (.704,.065,.90), "shell", .022, group)
            box("Door_leaf_header", (px,y,3.07), (.704,.065,.19), "shell", .014, group)
            for dx in [-.319,.319]:
                box("Door_leaf_stile", (px+dx,y,2.60), (.066,.07,.96), "shell", .011, group)
            frame_window("Door_window",px,y,2.61,.51,.85,group)
            box("Door_livery", (px,y+side*.04,1.84), (.70,.012,.27), "teal", .01, group)
            box("Door_seal", (x+direction*.007,y,2.2), (.016,.08,1.9), "black", .003, group)
            for dy in [-.043,.043]:
                side_text("CAUTION", px,y+dy,2.05,.043,"black",group,inward=dy*side<0)
        rod("Door_request_button", (x+.83,side*1.49,2.19),(x+.83,side*1.52,2.19),.055,"lime")

# Bogies, wheels and brake gear.
current = "05_Undercarriage"
for bogie in [-6.35,6.35]:
    box("Bogie_frame", (bogie,0,.63), (2.63,2.18,.32), "black", .10)
    for axle in [-.82,.82]:
        xx = bogie+axle
        rod("Axle", (xx,-1.05,.44),(xx,1.05,.44),.09,"steel")
        for side in [-1,1]:
            y=side*1.01
            rod("Wheel_tread", (xx,y-.12,.44),(xx,y+.12,.44),.40,"steel",32)
            rod("Wheel_web", (xx,y-side*.15,.44),(xx,y+side*.16,.44),.315,"black",24)
            rod("Wheel_hub", (xx,y+side*.16,.44),(xx,y+side*.20,.44),.13,"steel",20)
            box("Axlebox", (xx,y+side*.19,.49), (.31,.16,.26), "black", .04)
    for side in [-1,1]:
        for xx in [bogie-.6,bogie+.6]:
            rod("Air_spring", (xx,side*.82,.76),(xx,side*.82,.9),.18,"black",20)
for x in [-3.6,0,3.2]:
    box("Underslung_equipment", (x,0,.63), (2.25,1.83,.39), "steel", .06)
    for xx in range(11):
        box("Cooling_rib", (x-1+xx*.20,-.927,.65), (.04,.018,.27), "black", .002)

# Roof is separately addressable, including all overhead fittings.
current = "04_Roof"
box("Roof_shell", (-.8,0,3.49), (16.7,2.96,.25), "shell", .115)
box("Ceiling_liner", (-.8,0,3.345), (16.3,2.68,.07), "white", .03)
for x in [-4.0,2.7]:
    box("HVAC_housing", (x,0,3.75), (2.7,1.74,.31), "shell", .12)
    for side in [-1,1]:
        for j in range(13):
            box("HVAC_grille", (x-1.08+j*.18,side*.57,3.918), (.065,.55,.015), "black", .003)
for y in [-1.12,1.12]:
    box("Ceiling_LED_diffuser", (-.8,y,3.293), (15.85,.09,.022), "light", .009)
for y in [-.77,.77]:
    for xx in range(53):
        box("Ceiling_vent", (-8.65+xx*.30,y,3.303), (.16,.07,.006), "steel", .002)

# Open passenger saloon.
current = "02_Interior"
for side in [-1,1]:
    for bay in [-3.45,1.85]:
        box("Seat_plinth", (bay,side*1.06,1.40), (2.86,.56,.38), "white", .07)
        for i in range(5):
            x=bay+(i-2)*.55
            seat_mat = "priority" if bay < 0 and side > 0 and i < 2 else "seat"
            box("Seat_cushion", (x,side*1.04,1.67), (.53,.57,.11), seat_mat,.07)
            seat=box("Seat_backrest", (x,side*1.28,1.96), (.53,.095,.53), seat_mat,.07)
            seat.rotation_euler.x=side*math.radians(-8)
            box("Seat_grip", (x,side*1.215,2.19), (.21,.015,.033), "black",.01)
        for x in [bay-1.46,bay+1.46]:
            rod("Seat_end_grab", (x,side*.75,1.53),(x,side*.75,2.73),.024,"steel")
            rod("Seat_end_top", (x,side*.75,2.73),(x,side*1.30,2.73),.024,"steel")
            box("Seat_end_partition_Glass", (x,side*1.03,2.24), (.025,.49,.73), "glass",.08)
    for x in [-8.15,6.22]:
        box("Fold_seat", (x,side*1.28,1.84), (.70,.14,.73), "seat",.08)
        box("Fold_seat_hinge", (x,side*1.23,1.47), (.60,.18,.12), "steel")
    for x in door_x:
        rod("Vertical_stanchion", (x,side*.57,1.21),(x,side*.57,3.20),.026,"steel")
        box("Pole_base", (x,side*.57,1.22), (.13,.13,.026),"steel",.045)
    rod("Longitudinal_handrail", (-8.65,side*.58,2.97),(6.85,side*.58,2.97),.023,"steel")
    for i in range(24):
        x=-8.15+i*.635
        rod("Strap", (x,side*.58,2.98),(x,side*.58,2.78),.011,"black")
        a=(x-.085,side*.58,2.77)
        b=(x+.085,side*.58,2.77)
        c=(x+.10,side*.58,2.64)
        d=(x-.10,side*.58,2.64)
        for p,q in [(a,b),(b,c),(c,d),(d,a)]:
            rod("Hanging_handle",p,q,.017,"white")
    for x in door_x:
        box("Interior_route_board", (x,side*1.377,3.13), (1.85,.025,.25), "white", .02)
        side_text("01    HARBOR LINE    /    CENTRAL", x,side*1.36,3.15,.059,"teal",inward=True)
        for n in range(9):
            xx=x-.71+n*.177
            rod("Route_stop", (xx,side*1.355,3.066),(xx,side*1.345,3.066),.017,"teal")
        box("Route_line", (x,side*1.349,3.066), (1.44,.008,.011),"teal",.001)
    side_text("PRIORITY", -8.15,side*1.37,2.70,.065,"teal",inward=True)
    # Emergency intercom is visible from inside, next to the central door.
    box("Emergency_intercom", (.13,side*1.34,2.58), (.20,.07,.34), "steel")
    for j in range(5):
        box("Intercom_grille", (.13,side*1.295,2.64+j*.019), (.12,.008,.006),"black",.001)
    rod("Emergency_button", (.13,side*1.30,2.48),(.13,side*1.28,2.48),.035,"red")
# End wall and rear gangway.
box("Rear_bulkhead", (-9.09,0,2.34), (.12,2.81,2.22), "white")
box("Rear_end_door", (-8.998,0,2.29), (.04,.89,2.0), "shell", .055)
box("Rear_end_Glass", (-8.97,0,2.65), (.024,.64,.69), "glass", .03)
for y in [-.53,.53]:
    rod("Rear_door_grip", (-8.96,y,1.95),(-8.96,y,2.34),.017,"steel")
text("Rear_car_label", "M01", (-8.961,0,3.11),.12,"teal",(math.pi/2,0,math.pi/2))
# Cab bulkhead leaves a real central doorway.
for y in [-.94,.94]:
    box("Cab_bulkhead", (7.14,y,2.27), (.10,.97,2.16), "white", .03)
box("Cab_door_header", (7.14,0,3.21), (.1,2.87,.25), "white")
box("Cab_door_open_parked", (7.23,.93,2.18), (.045,.86,1.90), "shell", .04)
box("Cab_door_Glass", (7.19,.93,2.63), (.018,.60,.66), "glass")
text("Cab_notice", "DRIVER CAB", (7.075,0,3.19), .12,"teal",(math.pi/2,0,-math.pi/2))
text("Cab_notice_small", "AUTHORIZED PERSONNEL", (7.079,-.97,2.73), .053,"black",(math.pi/2,0,-math.pi/2))
box("Passenger_information_display", (7.075,-.97,2.45), (.035,.76,.36), "screen", .025)
text("Next_stop", "NEXT STOP\nCENTRAL", (7.05,-.97,2.47),.083,"cyan",(math.pi/2,0,-math.pi/2))
box("Extinguisher_case", (6.89,1.21,1.58), (.16,.30,.65), "white", .025)
rod("Fire_extinguisher", (6.77,1.21,1.34),(6.77,1.21,1.76),.085,"red",20)

# Cab enclosure with unobstructed front glazing.
current = "01_Shell"
for side in [-1,1]:
    box("Cab_side_lower", (8.18,side*1.40,1.63), (1.90,.115,.86),"shell",.08)
    box("Cab_livery", (8.18,side*1.463,1.84), (1.90,.025,.27),"teal",.01)
    frame_window("Cab_side_window",8.15,side*1.40,2.64,1.55,1.05)
    box("Cab_rear_pillar", (7.29,side*1.41,2.67), (.15,.13,1.21),"teal",.05)
    box("Cab_front_pillar", (9.02,side*1.39,2.63), (.18,.17,1.30),"teal",.06)
    box("Cab_top_side", (8.18,side*1.40,3.29), (1.95,.15,.19),"teal",.06)
# Tapered nose fascia; the windshield remains an actual opening.
mesh("Nose_fascia",
     [(9.18,-1.41,1.08),(9.18,1.41,1.08),(9.48,-1.32,1.27),(9.48,1.32,1.27),
      (9.39,-1.36,2.06),(9.39,1.36,2.06),(9.16,-1.42,2.06),(9.16,1.42,2.06)],
     [(0,1,3,2),(2,3,5,4),(4,5,7,6),(0,2,4,6),(1,7,5,3)],"teal")
box("Front_upper_header",(9.14,0,3.27),(.24,2.81,.30),"teal",.12)
box("Windshield_lower_seal",(9.355,0,2.08),(.10,2.62,.065),"black",.03)
box("Windshield_upper_seal",(9.18,0,3.13),(.10,2.54,.07),"black",.03)
for y in [-1.30,1.30]:
    pillar=box("Windshield_side_seal",(9.27,y,2.60),(.085,.065,1.12),"black",.028)
    pillar.rotation_euler.y=math.radians(-9)
glass=box("Windshield_Glass",(9.27,0,2.60),(.027,2.57,1.045),"glass",.02)
glass.rotation_euler.y=math.radians(-9)
box("Destination_display",(9.278,0,3.29),(.025,1.87,.205),"screen",.04)
front_text("01  CENTRAL",9.30,0,3.29,.13)
for side in [-1,1]:
    box("Headlight_recess",(9.427,side*.90,1.71),(.07,.59,.23),"black",.08)
    box("Headlight_LED",(9.469,side*.90,1.74),(.017,.43,.054),"light",.02)
    box("Tail_light",(9.469,side*1.10,1.64),(.014,.063,.034),"red",.01)
    rod("Windshield_wiper",(9.377,side*.48,2.14),(9.30,side*.32,2.65),.014,"black")
    rod("Wiper_blade",(9.305,side*.32,2.57),(9.255,side*.32,2.98),.016,"black")
box("Front_bumper",(9.39,0,1.15),(.23,2.24,.22),"black",.10)
box("Coupler_housing",(9.68,0,.96),(.61,.38,.21),"steel",.045)
box("Coupler_head",(9.99,0,.96),(.13,.49,.32),"black",.025)
front_text("M01",9.49,0,1.57,.13,"white")
current = "04_Roof"
box("Cab_roof",(8.20,0,3.48),(2.15,2.83,.24),"shell",.11)
rod("Radio_antenna",(8.4,0,3.61),(8.4,0,3.94),.017,"black")

# Driver's desk, angled instrument panel, controls and chair.
current = "03_Cab"
box("Driver_console_base",(8.77,0,1.57),(.73,2.49,.73),"black",.10)
box("Driver_console_top",(8.69,0,1.98),(.95,2.55,.12),"steel",.065)
panel = box("Instrument_panel",(8.88,0,2.13),(.12,2.35,.32),"black",.045)
panel.rotation_euler.y=math.radians(-16)
# Instruments face the driver (-X).
for y in [-.77,0,.77]:
    box("LCD_bezel",(8.796,y,2.15),(.045,.61,.27),"steel",.022)
    box("LCD_display",(8.767,y,2.15),(.008,.56,.225),"screen",.005)
    label="DOORS\nALL CLOSED" if y < -.3 else ("00\nkm/h" if abs(y)<.3 else "ATP   NORMAL\nSIGNAL  CLEAR")
    text("Cab_LCD_text",label,(8.759,y,2.15),.057,"cyan",(math.pi/2,0,-math.pi/2))
    for n in range(4):
        box("LCD_status_bar",(8.753,y-.20+n*.13,2.055),(.004,.08,.012),"cyan",.001)
for y in [-.93,.89]:
    box("Controller_boot",(8.38,y,2.07),(.22,.22,.09),"black",.025)
    rod("Master_controller",(8.38,y,2.10),(8.31,y,2.32),.024,"steel")
    box("Controller_grip",(8.30,y,2.32),(.105,.18,.055),"black",.025)
for j,mat in enumerate(["red","lime","yellow","white","cyan","black"]):
    y=-.48+j*.19
    rod("Console_pushbutton",(8.43,y,2.05),(8.43,y,2.084),.042,mat,20)
text("Console_control_labels","RADIO   LIGHT   HORN   DOORS   EMERG",(8.54,0,2.051),.036,"black",(0,0,-math.pi/2))
box("Radio_unit",(8.51,-1.09,2.08),(.28,.20,.09),"black",.02)
for i in range(5):
    box("Radio_speaker",(8.42+i*.04,-1.09,2.128),(.007,.12,.005),"steel",.001)
rod("Driver_seat_pedestal",(7.83,.37,1.20),(7.83,.37,1.60),.085,"steel",20)
box("Driver_seat_cushion",(7.81,.37,1.67),(.57,.56,.15),"black",.075)
box("Driver_seat_back",(7.53,.37,2.05),(.13,.59,.72),"black",.075)
box("Driver_headrest",(7.51,.37,2.51),(.14,.36,.20),"black",.05)
for y in [.03,.71]:
    rod("Driver_armrest_support",(7.68,y,1.70),(7.68,y,1.94),.02,"steel")
    box("Driver_armrest",(7.80,y,1.95),(.34,.09,.055),"black",.025)
box("Deadman_pedal",(8.31,.35,1.29),(.22,.19,.045),"black",.015)
for side in [-1,1]:
    box("Cab_side_utility",(7.76,side*1.27,1.64),(.59,.17,.80),"white",.03)
    side_text("EQUIPMENT",7.76,side*1.171,1.79,.047,"black",inward=True)

# Rails give scale without obstructing interior inspection.
current = "07_Track"
for x in range(-13,14):
    box("Sleeper",(x,0,-.105),(.23,2.53,.17),"concrete",.025)
for side in [-1,1]:
    y=side*.97
    box("Rail_foot",(0,y,-.025),(27,.17,.045),"steel",.004)
    box("Rail_web",(0,y,.027),(27,.055,.08),"steel",.006)
    box("Rail_head",(0,y,.085),(27,.10,.055),"steel",.01)
box("Trackbed",(0,0,-.235),(27.5,3.23,.14),"concrete",.045)

# Camera rigs and studio lighting are saved in the .blend, excluded from GLB.
current = "08_Studio"
scene=bpy.context.scene
scene.unit_settings.system="METRIC"
scene.render.engine="CYCLES"
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.world.color=(.28,.28,.28)
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(.63,.70,.73,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=.55
box("Studio_ground",(0,0,-.35),(200,200,.10),"white",0)


def camera(name,pos,target,lens=40):
    bpy.ops.object.camera_add(location=pos)
    obj=bpy.context.object
    finish(obj,name,None)
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    obj.data.lens=lens
    obj.data.clip_start=.04
    obj.data.clip_end=500
    return obj


for name,pos,power,size in [
    ("Key softbox",(3,-7,13),2600,9),("Rim softbox",(-5,6,10),2200,8),("Nose softbox",(15,2,8),1600,6)
]:
    bpy.ops.object.light_add(type="AREA",location=pos)
    light=bpy.context.object
    finish(light,name,None)
    light.data.energy=power
    light.data.shape="DISK"
    light.data.size=size
    light.rotation_euler=(Vector((0,0,1.5))-light.location).to_track_quat("-Z","Y").to_euler()
for x in [-7,-3,1,5,8]:
    bpy.ops.object.light_add(type="AREA",location=(x,0,3.23))
    light=bpy.context.object
    finish(light,"Interior soft light",None)
    light.data.energy=65
    light.data.shape="RECTANGLE"
    light.data.size=2.6
    light.data.size_y=1.8
exterior=camera("CAM_Exterior",(21,-23,13),(0,0,1.65),43)
saloon=camera("CAM_Passenger",(-7.5,0,2.72),(5.5,0,2.1),19)
cab=camera("CAM_Driver",(7.57,-.18,2.72),(9.10,0,2.05),18)
scene.camera=exterior
scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
# Ready-to-play 360-degree orbit in the Blender timeline.
rig=bpy.data.objects.new("360_ORBIT",None)
collections[current].objects.link(rig)
exterior.parent=rig
scene.frame_start=1
scene.frame_end=240
scene.render.fps=24
rig.rotation_euler.z=0
rig.keyframe_insert(data_path="rotation_euler",frame=1)
rig.rotation_euler.z=2*math.pi
rig.keyframe_insert(data_path="rotation_euler",frame=241)
if rig.animation_data and rig.animation_data.action:
    action=rig.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for point in curve.keyframe_points:
                        point.interpolation="LINEAR"
scene.frame_set(1)
# Make the saved project open on a clean, framed train view.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=="VIEW_3D":
            area.spaces.active.region_3d.view_distance=27
            area.spaces.active.region_3d.view_location=(0,0,1.7)
            area.spaces.active.region_3d.view_rotation=exterior.rotation_euler.to_quaternion()
            area.spaces.active.shading.type="MATERIAL"
bpy.ops.wm.save_as_mainfile(filepath=str(DELIVERY/"metro-atelier.blend"),compress=True)
# Export only model content. Font objects are converted in-memory after saving
# so labels stay editable in Blender but remain visible in every glTF viewer.
bpy.ops.object.select_all(action="DESELECT")
for obj in list(bpy.data.objects):
    if obj.type=="FONT":
        obj.select_set(True)
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.convert(target="MESH")
        obj.select_set(False)
for col_name,col in collections.items():
    if col_name!="08_Studio":
        for obj in col.objects:
            obj.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=str(ASSETS/"metro.glb"),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_extras=True,
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_yup=True,
)
depsgraph=bpy.context.evaluated_depsgraph_get()
corners=[
    obj.matrix_world @ Vector(corner)
    for name,col in collections.items() if name not in {"07_Track","08_Studio"}
    for obj in col.objects if obj.type=="MESH"
    for corner in obj.evaluated_get(depsgraph).bound_box
]
measured=[round(max(p[axis] for p in corners)-min(p[axis] for p in corners),2) for axis in range(3)]
manifest={
    "name":"Metro Atelier / M01",
    "concept":True,
    "blender":bpy.app.version_string,
    "dimensions_m":dict(zip(["length","width","height"],measured)),
    "seats":24,
    "doors":6,
    "objects":sum(len(c.objects) for k,c in collections.items() if k!="08_Studio"),
    "coordinates":"Blender: X length, Y width, Z up. glTF: X length, Y up, Z = -Blender Y.",
    "features":["full interior","driver controls","sliding door groups","roof collection","240-frame orbit"],
}
(ASSETS/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
if args.render:
    for name,cam in [("exterior",exterior),("interior",saloon),("cab",cab)]:
        scene.camera=cam
        scene.render.filepath=str(DELIVERY/f"{name}.png")
        bpy.ops.render.render(write_still=True)
print("METRO_BUILD_COMPLETE "+json.dumps(manifest))
