"""Reusable hard-surface primitives for the Devastator clay study (Z-up)."""

import math
import bpy
from mathutils import Vector


class Workshop:
    def __init__(self, collection):
        self.collection = collection
        self.materials = {}
        self.cache = {}
        self.groups = []

    def material(self, name, value, metal=0.0, rough=.45):
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = (value, value, value, 1)
        mat.use_nodes = True
        node = mat.node_tree.nodes.get("Principled BSDF")
        node.inputs["Base Color"].default_value = mat.diffuse_color
        node.inputs["Metallic"].default_value = metal
        node.inputs["Roughness"].default_value = rough
        self.materials[name] = mat
        return mat

    def group(self, name, pos=(0, 0, 0), parent=None, rot=(0, 0, 0), assembly=None):
        obj = bpy.data.objects.new(name, None)
        self.collection.objects.link(obj)
        obj.parent = parent
        obj.location = pos
        obj.rotation_euler = rot
        obj.empty_display_size = .15
        obj["assembly"] = assembly or (parent.get("assembly", name) if parent else name)
        self.groups.append(obj)
        return obj

    def mesh(self, name, vertices, faces, material, parent, bevel=0):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        self.collection.objects.link(obj)
        obj.parent = parent
        mesh.materials.append(self.materials[material])
        if bevel:
            edge = obj.modifiers.new("Machined chamfer", "BEVEL")
            edge.width = min(bevel, .025) if material == "armor" else bevel
            edge.segments = 1 if material == "armor" else 2
            obj.modifiers.new("Weighted panel normals", "WEIGHTED_NORMAL")
        return obj

    def instance(self, name, key, factory, pos, mat, parent, rot=(0, 0, 0)):
        if key not in self.cache:
            factory()
            obj = bpy.context.object
            mesh = obj.data
            self.cache[key] = mesh
            bpy.data.objects.remove(obj, do_unlink=True)
        obj = bpy.data.objects.new(name, self.cache[key])
        self.collection.objects.link(obj)
        obj.parent = parent
        obj.location = pos
        obj.rotation_euler = rot
        if not obj.data.materials:
            obj.data.materials.append(self.materials[mat])
        obj.material_slots[0].link = "OBJECT"
        obj.material_slots[0].material = self.materials[mat]
        return obj

    def box(self, name, pos, size, mat, parent, bevel=.035, rot=(0, 0, 0)):
        x, y, z = (v / 2 for v in size)
        vertices = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
                    (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
        faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
                 (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        obj = self.mesh(name, vertices, faces, mat, parent, min(bevel, min(size)*.2))
        obj.location, obj.rotation_euler = pos, rot
        return obj

    def cyl(self, name, pos, radius, depth, mat, parent, axis=(0, 0, 1), n=24):
        key = ("cyl", radius, depth, n)
        obj = self.instance(name, key, lambda: bpy.ops.mesh.primitive_cylinder_add(
            vertices=n, radius=radius, depth=depth), pos, mat, parent)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = Vector(axis).to_track_quat("Z", "Y")
        edge = obj.modifiers.new("Turned edge", "BEVEL")
        edge.width, edge.segments = min(.016, radius*.12, depth*.12), 2
        obj.modifiers.new("Turned normals", "WEIGHTED_NORMAL")
        return obj

    def ring(self, name, pos, radius, minor, mat, parent, axis=(0, 0, 1)):
        key = ("torus", radius, minor)
        obj = self.instance(name, key, lambda: bpy.ops.mesh.primitive_torus_add(
            major_segments=32, minor_segments=8, major_radius=radius,
            minor_radius=minor), pos, mat, parent)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = Vector(axis).to_track_quat("Z", "Y")
        for poly in obj.data.polygons:
            poly.use_smooth = True
        return obj

    def rod(self, name, start, end, radius, mat, parent):
        a, b = Vector(start), Vector(end)
        return self.cyl(name, (a+b)/2, radius, (b-a).length, mat, parent, b-a, 12)

    def hose(self, name, points, radius, mat, parent):
        data = bpy.data.curves.new(name, "CURVE")
        data.dimensions = "3D"
        data.resolution_u = 8
        data.bevel_depth, data.bevel_resolution = radius, 2
        spline = data.splines.new("BEZIER")
        spline.bezier_points.add(len(points)-1)
        for point, co in zip(spline.bezier_points, points):
            point.co = co
            point.handle_left_type = point.handle_right_type = "AUTO"
        obj = bpy.data.objects.new(name, data)
        self.collection.objects.link(obj)
        obj.parent = parent
        data.materials.append(self.materials[mat])
        return obj

    def plate(self, name, outline, y, depth, mat, parent, bevel=.025):
        """Extrude a closed X/Z profile; visible front is negative Y."""
        n = len(outline)
        vertices = [(x, yy, z) for yy in (y-depth/2, y+depth/2) for x, z in outline]
        faces = [tuple(range(n)), tuple(reversed(range(n, 2*n)))]
        faces += [(i, (i+n) % (2*n), (i+1) % n+n, (i+1) % n) for i in range(n)]
        return self.mesh(name, vertices, faces, mat, parent, bevel)

    def panel(self, name, pos, w, h, parent, mat="armor", bevel=.055):
        x, y, z = pos
        cut = min(.12, w*.12, h*.12)
        outline = [(x-w/2+cut, z-h/2), (x+w/2-cut, z-h/2),
                   (x+w/2, z-h/2+cut), (x+w/2, z+h/2-cut),
                   (x+w/2-cut, z+h/2), (x-w/2+cut, z+h/2),
                   (x-w/2, z+h/2-cut), (x-w/2, z-h/2+cut)]
        self.plate(name+" recessed gasket", outline, y+.025, .10, "recess", parent, .018)
        inset = [(x+(xx-x)*.94, z+(zz-z)*.94) for xx, zz in outline]
        self.plate(name, inset, y-.042, .095, mat, parent, bevel)
        if min(w, h) > .28:
            for dx in [-w*.36, w*.36]:
                for dz in [-h*.35, h*.35]:
                    self.bolt((x+dx, y-.10, z+dz), parent)

    def bolt(self, pos, parent, radius=.025, axis=(0, -1, 0)):
        self.cyl("Hex fastener", pos, radius, .02, "steel", parent, axis, 6)

    def vent(self, name, pos, width, height, parent, vertical=False, n=8):
        x, y, z = pos
        self.box(name+" recess", pos, (width, .05, height), "recess", parent, .015)
        for i in range(n):
            t = (i+.5)/n-.5
            p = (x+t*width, y-.045, z) if vertical else (x, y-.045, z+t*height)
            size = (width/n*.38, .075, height*.88) if vertical else (width*.88, .07, height/n*.35)
            self.box(name+" louver", p, size, "steel", parent, .008)

    def piston(self, name, start, end, parent, radius=.11):
        a, b = Vector(start), Vector(end)
        d = b-a
        self.rod(name+" barrel", a, a+d*.62, radius, "armor", parent)
        self.rod(name+" polished ram", a+d*.60, b, radius*.54, "steel", parent)
        for t in [.08, .53, .62]:
            self.cyl(name+" gland", a+d*t, radius*1.17, .075, "edge", parent, d)
        for p in [a, b]:
            self.cyl(name+" clevis", p, radius*1.55, radius*2.4, "joint", parent, (0, 1, 0))
            self.bolt(p+Vector((0, -radius*1.25, 0)), parent, radius*.5)

    def tire(self, name, pos, radius, width, parent, axis=(1, 0, 0)):
        group = self.group(name, pos, parent)
        group.rotation_mode = "QUATERNION"
        group.rotation_quaternion = Vector(axis).to_track_quat("Z", "Y")
        self.cyl("Rubber carcass", (0, 0, 0), radius*.92, width, "rubber", group, n=40)
        for side in [-1, 1]:
            z = side*width*.52
            self.ring("Reinforced sidewall", (0, 0, z), radius*.76, radius*.065, "rubber", group)
            self.cyl("Wheel rim", (0, 0, z), radius*.53, .04, "edge", group, n=32)
            self.cyl("Recessed hub", (0, 0, z+side*.024), radius*.34, .035, "joint", group)
            self.cyl("Axle cap", (0, 0, z+side*.05), radius*.18, .045, "steel", group)
            for i in range(8):
                angle = i*math.tau/8
                self.bolt((math.cos(angle)*radius*.25, math.sin(angle)*radius*.25,
                           z+side*.055), group, radius*.035, (0, 0, 1))
        for i in range(28):
            a = i*math.tau/28
            for side in [-1, 1]:
                self.box("Chevron tread", (math.cos(a)*radius*.94, math.sin(a)*radius*.94, side*width*.24),
                         (radius*.15, radius*.15, width*.53), "rubber", group, .012,
                         (0, side*.13, a))
        return group

    def track(self, name, pos, length, radius, width, parent, rot=(0, 0, 0)):
        group = self.group(name, pos, parent, rot)
        half = length/2-radius
        self.box("Crawler frame", (0, 0, 0), (length-radius, width*.80, radius*1.30), "joint", group)
        for x in [-half, half]:
            self.cyl("Drive sprocket", (x, 0, 0), radius*.83, width, "steel", group, (0, 1, 0), 32)
            self.cyl("Sprocket recess", (x, -width*.54, 0), radius*.58, .025, "joint", group, (0, 1, 0))
            self.cyl("Sprocket cap", (x, -width*.57, 0), radius*.30, .045, "armor", group, (0, 1, 0))
            for i in range(8):
                a = i*math.tau/8
                self.bolt((x+math.cos(a)*radius*.44, -width*.58, math.sin(a)*radius*.44), group)
            self.cyl("Rear sprocket recess", (x, width*.54, 0), radius*.58, .025,
                     "joint", group, (0, 1, 0))
            self.cyl("Rear sprocket cap", (x, width*.57, 0), radius*.30, .045,
                     "armor", group, (0, 1, 0))
            for i in range(8):
                a = i*math.tau/8
                self.bolt((x+math.cos(a)*radius*.44, width*.58, math.sin(a)*radius*.44),
                          group, axis=(0, 1, 0))
        for i in range(4):
            x = -half+(i+1)*2*half/5
            self.cyl("Road wheel", (x, 0, -.09), radius*.52, width*.94, "joint", group, (0, 1, 0))
        path = []
        straight = max(3, round(2*half/.16))
        for i in range(straight):
            x = -half+(i+.5)*2*half/straight
            path.extend([(x, radius, 0), (x, -radius, 0)])
        for side in [-1, 1]:
            for i in range(9):
                a = -math.pi/2+(i+.5)*math.pi/9
                x = side*(half+math.cos(a)*radius)
                z = math.sin(a)*radius
                path.append((x, z, side*(math.pi/2-a)))
        for x, z, a in path:
            self.box("Individual track shoe", (x, 0, z), (.15, width*1.13, .115),
                     "track", group, .015, (0, a, 0))
            self.box("Track grouser", (x, -width*.04, z+.046*math.cos(a)), (.065, width*1.22, .09),
                     "edge", group, .012, (0, a, 0))
        self.panel("Crawler guard", (0, -width*.60, .04), half*1.55, radius*.88, group)
        self.hazard((0, -width*.60-.11, .04), half*1.30, radius*.60, group)
        return group

    def hazard(self, pos, width, height, parent):
        x, y, z = pos
        count = max(2, round(width/.27))
        cell = width/count
        for i in range(count):
            left = x-width/2+i*cell
            self.plate("Inset hazard stripe", [(left, z-height/2), (left+cell*.44, z-height/2),
                       (left+cell*.84, z+height/2), (left+cell*.40, z+height/2)],
                       y, .008, "recess", parent, 0)

    def barrel(self, name, pos, profile, parent, mat="armor"):
        """Surface of revolution about local Z, including capped ends."""
        n = 48
        vertices = [(pos[0]+r*math.cos(i*math.tau/n), pos[1]+r*math.sin(i*math.tau/n), pos[2]+z)
                    for z, r in profile for i in range(n)]
        faces = [tuple(reversed(range(n)))]
        for row in range(len(profile)-1):
            for i in range(n):
                j = (i+1) % n
                faces.append((row*n+i, row*n+j, (row+1)*n+j, (row+1)*n+i))
        faces.append(tuple(range((len(profile)-1)*n, len(profile)*n)))
        obj = self.mesh(name, vertices, faces, mat, parent, .018)
        for poly in obj.data.polygons:
            poly.use_smooth = len(poly.vertices) == 4
        return obj
