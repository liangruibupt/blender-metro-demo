"""Add an original island-platform station around the existing editable train."""

import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--render", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(ROOT/"deliverables/metro-atelier.blend"))
random.seed(21)
cols = {}
for name in ["09_Station", "10_Station_Cover", "11_Station_Lighting"]:
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    cols[name] = col
current = "09_Station"


def mat(name, color, metal=0, rough=.6, emission=0):
    result = bpy.data.materials.new("Station / "+name)
    result.diffuse_color = (*color, 1)
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    if emission:
        shader.inputs["Emission Color"].default_value = (*color, 1)
        shader.inputs["Emission Strength"].default_value = emission
    return result


M = {
    "concrete": mat("Concrete", (.34,.38,.38)),
    "grout": mat("Tile grout", (.32,.37,.36)),
    "ivory": mat("Glazed ceramic", (.73,.77,.72), .05, .3),
    "roof": mat("Vault panels", (.49,.54,.52), .15, .5),
    "dark": mat("Basalt trim", (.025,.045,.045), .25, .45),
    "jade": mat("Central jade", (.014,.24,.19), .22, .35),
    "yellow": mat("Tactile ochre", (.90,.66,.06), .05, .7),
    "white": mat("Sign white", (.91,.94,.88)),
    "steel": mat("Stainless fittings", (.42,.49,.49), .8, .28),
    "light": mat("Linear luminaires", (1,.93,.73), 0,.4,3),
    "amber": mat("Departure display", (1,.60,.13), 0,.4,1.1),
    "screen": mat("Information LCD", (.004,.018,.018), .1,.3),
    "red": mat("Terracotta accent", (.60,.20,.10), .1,.6),
    "mint": mat("Map mint", (.25,.64,.48)),
    "blue": mat("Map blue", (.14,.32,.48)),
}
for i,color in enumerate([(.59,.63,.59),(.64,.68,.64),(.68,.71,.67),(.61,.66,.63)]):
    M[f"floor{i}"] = mat(f"Limestone {i}",color,0,.58)


def finish(obj,name,material):
    obj.name = name
    obj["zone"] = current
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    cols[current].objects.link(obj)
    if material:
        obj.data.materials.append(M[material])
    return obj


def box(name,pos,size,material,bevel=.012):
    x,y,z=(v/2 for v in size)
    data=bpy.data.meshes.new(name)
    data.from_pydata(
        [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)],
        [],
        [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],
    )
    data.update()
    obj=bpy.data.objects.new(name,data)
    obj.location=pos
    finish(obj,name,material)
    if bevel:
        b=obj.modifiers.new("Edge radius","BEVEL")
        b.width=bevel
        b.segments=2
        obj.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return obj


def rod(name,a,b,radius,material,vertices=12):
    a,b=Vector(a),Vector(b)
    vec=b-a
    points=[(radius*math.cos(i*2*math.pi/vertices),radius*math.sin(i*2*math.pi/vertices),z)
            for z in [-vec.length/2,vec.length/2] for i in range(vertices)]
    faces=[(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    faces.extend([tuple(reversed(range(vertices))),tuple(range(vertices,vertices*2))])
    data=bpy.data.meshes.new(name)
    data.from_pydata(points,[],faces)
    data.update()
    obj=bpy.data.objects.new(name,data)
    obj.location=(a+b)/2
    obj.rotation_euler=vec.to_track_quat("Z","Y").to_euler()
    finish(obj,name,material)
    for poly in obj.data.polygons:
        poly.use_smooth=poly.index<vertices
    return obj


def text(name,value,pos,size,material,rotation=(math.pi/2,0,0),align="CENTER"):
    data=bpy.data.curves.new(name,type="FONT")
    obj=bpy.data.objects.new(name,data)
    obj.location=pos
    obj.rotation_euler=rotation
    obj.data.body=value
    obj.data.size=size
    obj.data.align_x=align
    obj.data.align_y="CENTER"
    obj.data.extrude=.0008
    obj.data.resolution_u=4
    return finish(obj,name,material)


def ytext(name,value,x,y,z,size,material,normal=1):
    return text(name,value,(x,y,z),size,material,(math.pi/2,0,math.pi if normal>0 else 0))


def xtext(name,value,x,y,z,size,material,normal=-1):
    return text(name,value,(x,y,z),size,material,(math.pi/2,0,math.pi/2 if normal>0 else -math.pi/2))


def quad(name,points,material):
    data=bpy.data.meshes.new(name)
    data.from_pydata(points,[],[(0,1,2,3)])
    data.update()
    obj=bpy.data.objects.new(name,data)
    cols[current].objects.link(obj)
    obj["zone"]=current
    data.materials.append(M[material])
    return obj


# Rail level is unchanged. The raised platform aligns with the train threshold.
print("STATION: building platform and tracks",flush=True)
box("Station_foundation",(0,-4.80,-.43),(43,16.0,.24),"dark",.08)
box("Platform_structure",(0,-4.79,.43),(36,6.22,1.47),"concrete",.025)
box("Platform_grout_bed",(0,-4.79,1.185),(36,6.22,.05),"grout",.003)
for i in range(45):
    for j in range(8):
        box("Platform_floor_tile",(-17.6+i*.8,-2.04-j*.773,1.221),(.791,.764,.023),f"floor{random.randrange(4)}",.003)
for y in [-1.75,-7.83]:
    box("Platform_edge_coping",(0,y,1.24),(36,.17,.045),"ivory",.005)
    box("Platform_tactile_strip",(0,y+(-.24 if y>-3 else .24),1.244),(36,.37,.025),"yellow",.003)
    for i in range(240):
        # Raised bars keep the warning strip legible in both glTF and Cycles.
        box("Tactile_rib",(-17.9+i*.15,y+(-.24 if y>-3 else .24),1.261),(.034,.27,.011),"yellow",.003)
    box("Edge_warning_line",(0,y+(-.49 if y>-3 else .49),1.24),(36,.047,.012),"dark",.002)
for x in [-12,-6,0,6,12]:
    text("Floor_mind_gap","MIND THE GAP",(x,-2.42,1.241),.12,"dark",(0,0,0))
for x in [-6.1,-.8,4.5]:
    for dx in [-.84,.84]:
        box("Boarding_lane",(x+dx,-2.55,1.24),(.052,1.02,.015),"jade",.002)
    text("Boarding_number","01",(x,-2.71,1.242),.21,"jade",(0,0,0))

# Extend the existing rails and add the opposite track.
for center in [0,-9.68]:
    box("Station_ballast",(0,center,-.19),(43,3.17,.13),"grout",.02)
    for x in range(-21,22):
        if center==0 and -13<=x<=13:
            continue
        box("Station_sleeper",(x,center,-.09),(.24,2.56,.16),"concrete",.018)
    for offset in [-.97,.97]:
        y=center+offset
        for start,end in ([(-23,-13.5),(13.5,23)] if center==0 else [(-23,23)]):
            box("Station_rail_foot",((start+end)/2,y,-.02),(end-start,.17,.044),"steel",.003)
            box("Station_rail_web",((start+end)/2,y,.032),(end-start,.055,.08),"steel",.003)
            box("Station_rail_head",((start+end)/2,y,.085),(end-start,.10,.055),"steel",.006)
    for x in [-20.5,20.5]:
        box("Tunnel_shadow",(x,center,2.28),(.15,3.18,4.75),"dark",0)
        for y in [center-1.60,center+1.60]:
            box("Tunnel_jamb",(x,y,2.4),(.8,.20,5.1),"concrete")
        box("Tunnel_lintel",(x,center,4.84),(.8,3.4,.32),"concrete")

# Far track wall stays visible in the open architectural overview.
print("STATION: building walls and furniture",flush=True)
box("Far_wall_backing",(0,2.32,2.52),(41,.20,5.48),"grout",.02)
for row in range(10):
    for i in range(50):
        box("Far_wall_subway_tile",(-19.6+i*.80,2.201,.30+row*.41),(.789,.021,.396),"ivory",.004)
box("Far_wall_jade_band",(0,2.17,2.96),(40,.04,.67),"jade",.005)
for x in [-13,-3,8,16]:
    ytext("Far_wall_station_name","CENTRAL",x,2.141,2.97,.31,"white",normal=-1)
    ytext("Far_wall_line","HARBOR LINE  /  01",x,2.139,2.70,.068,"mint",normal=-1)
box("Far_wall_service_plinth",(0,2.14,.54),(40,.23,.63),"dark",.02)
for z in [4.30,4.46,4.62]:
    rod("Far_wall_cable",(-20,2.09,z),(20,2.09,z),.025,"steel")

# Repeated square piers, seating and central wayfinding furniture.
column_x=[-13,-6.5,0,6.5,13]
for x in column_x:
    box("Station_column",(x,-4.88,3.64),(.60,.60,4.81),"ivory",.025)
    box("Column_base",(x,-4.88,1.48),(.72,.72,.48),"dark",.015)
    box("Column_capital",(x,-4.88,5.95),(.85,.85,.19),"concrete",.025)
    for z in [2.4,3.6,4.8]:
        box("Column_horizontal_joint",(x,-4.88,z),(.608,.608,.012),"grout",.001)
    box("Column_name_plate",(x,-4.562,3.04),(.59,.025,.47),"jade",.005)
    ytext("Column_name","CENTRAL",x,-4.542,3.10,.085,"white")
    ytext("Column_number","01",x,-4.540,2.93,.095,"mint")

for x in [-9.75,3.25,10.0]:
    box("Station_bench_base",(x,-5.03,1.53),(2.67,.47,.18),"steel",.04)
    for end in [-1,1]:
        box("Bench_leg",(x+end*.98,-5.03,1.42),(.10,.43,.37),"steel",.015)
    for i in range(4):
        xx=x+(i-1.5)*.66
        box("Station_bench_seat",(xx,-4.95,1.73),(.62,.55,.09),"jade",.045)
        box("Station_bench_back",(xx,-5.18,2.0),(.62,.08,.50),"jade",.045)
    for end in [-1,1]:
        rod("Bench_arm",(x+end*1.30,-4.77,1.80),(x+end*1.30,-4.77,2.0),.019,"steel")
        rod("Bench_arm_top",(x+end*1.30,-4.77,2.0),(x+end*1.30,-5.15,2.0),.022,"steel")

for x in [-9.75,3.25]:
    box("Information_monolith",(x,-5.61,2.9),(2.80,.16,2.64),"dark",.035)
    box("Map_lightbox",(x,-5.51,3.08),(2.59,.035,2.03),"white",.015)
    ytext("Map_heading","CENTRAL / NETWORK",x,-5.483,3.88,.13,"jade")
    # Original diagram built from geometric lines and editable station labels.
    for row,(material,z) in enumerate([("jade",3.48),("blue",3.06),("red",2.66)]):
        rod("Network_line",(x-1.06,-5.47,z),(x+1.06,-5.47,z),.018,material)
        for n in range(6):
            xx=x-1.02+n*.405
            rod("Network_node",(xx,-5.476,z),(xx,-5.452,z),.043,material,16)
            ytext("Network_station",["PIER","MUSEUM","CENTRAL","GARDEN","PARK","AIRPORT"][n],xx,-5.444,z-.12,.041,"dark")
    rod("Network_interchange",(x-.21,-5.445,2.66),(x-.21,-5.445,3.48),.018,"dark")
    ytext("Map_footer","HARBOR LINE 01      YOU ARE HERE",x,-5.475,2.29,.063,"jade")
    ytext("Reverse_poster","CITY\nIN MOTION",x,-5.704,3.13,.28,"white",normal=-1)
    ytext("Reverse_poster_caption","CENTRAL  /  M01",x,-5.705,2.43,.10,"mint",normal=-1)
    for xx in [x-.6,x+.6]:
        rod("Poster_graphic",(xx,-5.709,3.91),(xx+.35,-5.709,3.72),.026,"mint")

# Suspended arrival boards face both approaches along the platform.
for x in [-7.25,6.0]:
    box("Departure_board",(x,-3.27,4.28),(.16,2.50,.73),"dark",.03)
    for y in [-4.25,-2.30]:
        rod("Board_hanger",(x,y,4.64),(x,y,5.86),.020,"steel")
    for normal in [-1,1]:
        xx=x+normal*.086
        xtext("Departure_header","01   HARBOR LINE",xx,-3.27,4.51,.10,"white",normal)
        xtext("Departure_row_1","CENTRAL     ARRIVED",xx,-3.27,4.30,.087,"amber",normal)
        xtext("Departure_row_2","AIRPORT        04 MIN",xx,-3.27,4.11,.078,"amber",normal)
    box("Exit_sign",(x,-6.46,4.19),(.13,1.85,.44),"jade",.02)
    for normal in [-1,1]:
        xtext("Exit_sign_text","<  EXIT    A1",x+normal*.076,-6.46,4.20,.15,"white",normal)

for x in [-15.4,15.4]:
    for y in [-6.77]:
        box("Waste_bin",(x,y,1.70),(.48,.48,.91),"steel",.075)
        box("Bin_lid",(x,y,2.16),(.50,.50,.07),"dark",.025)
        box("Bin_opening",(x,y+.247,1.96),(.31,.02,.18),"dark",.015)
        ytext("Bin_label","RECYCLE",x,y+.269,1.63,.066,"jade")
box("Help_point",(-2.20,-5.52,2.30),(.52,.26,2.16),"ivory",.035)
box("Help_screen",(-2.20,-5.37,2.71),(.35,.024,.40),"screen",.015)
ytext("Help_title","i", -2.2,-5.35,3.16,.22,"jade")
rod("Help_button",(-2.2,-5.345,2.20),(-2.2,-5.32,2.20),.056,"red",20)

# A stair entrance at the end of the platform gives the station a readable exit.
for step in range(13):
    x=-16.0-step*.27
    top=1.24+(step+1)*.17
    box("Exit_stair",(x,-4.87,(1.24+top)/2),(.275,2.30,top-1.24),"floor2",.004)
    box("Stair_nosing",(x+.115,-4.87,top+.005),(.035,2.29,.011),"yellow",.002)
for y in [-3.70,-6.04]:
    rod("Stair_handrail",(-15.8,y,2.15),(-19.2,y,4.30),.026,"steel")
    for x,z in [(-16.1,1.60),(-17.6,2.48),(-19.0,3.34)]:
        rod("Stair_rail_post",(x,y,z),(x,y,z+.83),.021,"steel")
box("Stair_landing",(-19.7,-4.87,3.37),(1.05,2.30,.16),"floor2")
box("Exit_portal",(-20.10,-4.87,4.52),(.20,2.60,2.56),"dark",.015)
xtext("Exit_portal_sign","EXIT  A1", -19.978,-4.87,5.62,.20,"white",normal=1)

# Vault and near facade are removable for an unobstructed architectural overview.
print("STATION: building vault",flush=True)
current="10_Station_Cover"
center_y=-4.80
radius=7.12
def arc(theta):
    return center_y+radius*math.cos(theta),4.83+2.15*math.sin(theta)
for j in range(28):
    a=j*math.pi/28
    b=(j+1)*math.pi/28
    ya,za=arc(a)
    yb,zb=arc(b)
    for i in range(24):
        x=-20+i*(40/24)
        quad("Vault_panel",[(x+.014,ya,za),(x+40/24-.014,ya,za),(x+40/24-.014,yb,zb),(x+.014,yb,zb)],"roof")
for x in [-19.5,-13,-6.5,0,6.5,13,19.5]:
    for j in range(28):
        ya,za=arc(j*math.pi/28)
        yb,zb=arc((j+1)*math.pi/28)
        rod("Vault_structural_rib",(x,ya,za-.06),(x,yb,zb-.06),.056,"ivory")
for y in [-.70,-2.75,-6.80,-9.1]:
    theta=math.acos((y-center_y)/radius)
    z=arc(theta)[1]-.10
    box("Station_luminaire_channel",(0,y,z),(39.4,.14,.10),"dark",.012)
    for x in [-16,-8,0,8,16]:
        box("Station_LED_strip",(x,y,z-.057),(7.77,.085,.019),"light",.005)
box("Near_wall",(0,-11.96,2.34),(41,.2,5.10),"ivory",.02)
box("Near_wall_band",(0,-11.837,3.0),(40,.03,.65),"jade")
for x in [-13,-3,8,16]:
    ytext("Near_wall_name","CENTRAL",x,-11.813,3.0,.31,"white",normal=1)

current="11_Station_Lighting"
print("STATION: preparing cameras and export",flush=True)
scene=bpy.context.scene
for obj in bpy.data.collections["08_Studio"].objects:
    if obj.type=="LIGHT":
        obj.data.energy=0
for x in [-15,-8,0,8,15]:
    for y in [-2.75,-6.8]:
        bpy.ops.object.light_add(type="AREA",location=(x,y,5.88))
        light=bpy.context.object
        finish(light,"Station_area_light",None)
        light.data.energy=170
        light.data.shape="RECTANGLE"
        light.data.size=5.7
        light.data.size_y=2.6


def camera(name,pos,target,lens):
    bpy.ops.object.camera_add(location=pos)
    obj=bpy.context.object
    finish(obj,name,None)
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    obj.data.lens=lens
    obj.data.clip_start=.035
    obj.data.clip_end=500
    return obj


platform=camera("CAM_Station_Platform",(12.4,-3.75,2.90),(-5,-1.05,2.45),22)
overview=camera("CAM_Station_Overview",(29,-36,27),(0,-4.25,1.7),35)
scene.camera=platform
for obj in bpy.data.objects:
    if obj.get("slide") is not None and obj.get("side")==-1:
        obj.location.x=obj["slide"]
        obj.location.y=-.075
scene.cycles.samples=32
scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.world.node_tree.nodes["Background"].inputs[1].default_value=.30
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=="VIEW_3D":
            area.spaces.active.region_3d.view_perspective="CAMERA"
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.shading.type="MATERIAL"
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"deliverables/central-station.blend"),compress=True)

# Station-only GLB composes with the original train GLB in the viewer.
bpy.ops.object.select_all(action="DESELECT")
for name in ["09_Station","10_Station_Cover"]:
    for obj in list(cols[name].objects):
        if obj.type=="FONT":
            obj.select_set(True)
            bpy.context.view_layer.objects.active=obj
            bpy.ops.object.convert(target="MESH")
            obj.select_set(False)
for name in ["09_Station","10_Station_Cover"]:
    for obj in cols[name].objects:
        obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/"assets/station.glb"),
    export_format="GLB",use_selection=True,export_apply=True,export_extras=True,
    export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
manifest={
    "name":"Central / Harbor Line 01",
    "original_model":True,
    "reference_url":"https://sketchfab.com/3d-models/subway-station-bb68e4b3ac6646d2a59bffa7fa7818aa",
    "reference_usage":"Visual layout inspiration only. No downloaded model, texture or image is redistributed.",
    "platform":{"length_m":36,"width_m":6.22,"top_m":1.24,"near_edge_z":1.68,"far_edge_z":7.90},
    "tracks":2,
    "columns":column_x,
    "column_z":4.88,
    "door_x":[-6.1,-.8,4.5],
    "static_arrival_display":True,
}
(ROOT/"assets/station-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
if args.render:
    scene.camera=platform
    scene.render.filepath=str(ROOT/"deliverables/station-platform.png")
    bpy.ops.render.render(write_still=True)
    scene.camera=overview
    cols["10_Station_Cover"].hide_render=True
    scene.world.node_tree.nodes["Background"].inputs[1].default_value=.6
    scene.render.filepath=str(ROOT/"deliverables/station-overview.png")
    bpy.ops.render.render(write_still=True)
print("STATION_BUILD_COMPLETE "+json.dumps(manifest))
