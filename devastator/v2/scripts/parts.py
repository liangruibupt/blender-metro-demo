"""Shaped structural components for the second reference study."""
import math
from mathutils import Vector


def loft(w, name, sections, parent, mat="armor"):
    contour = [(-.36, -.5), (.36, -.5), (.5, -.36), (.5, .36),
               (.36, .5), (-.36, .5), (-.5, .36), (-.5, -.36)]
    vertices = [(cx+x*width, cy+y*depth, z)
                for z, width, depth, cx, cy in sections for x, y in contour]
    faces = [tuple(reversed(range(8)))]
    for j in range(len(sections)-1):
        faces += [(j*8+i, j*8+(i+1) % 8, (j+1)*8+(i+1) % 8, (j+1)*8+i) for i in range(8)]
    faces.append(tuple(range((len(sections)-1)*8, len(sections)*8)))
    return w.mesh(name, vertices, faces, mat, parent, .018)


def armor(w, name, outline, front, depth, parent, mat="armor"):
    points = [(x, front(x, z) if callable(front) else front, z) for x, z in outline]
    n = len(points)
    vertices = points+[(x, y+depth, z) for x, y, z in points]
    faces = [tuple(range(n)), tuple(reversed(range(n, 2*n)))]
    faces += [(i, i+n, (i+1) % n+n, (i+1) % n) for i in range(n)]
    return w.mesh(name, vertices, faces, mat, parent, .014)


def hatch(w, name, pos, width, height, parent, mat="armor"):
    x, y, z = pos
    outline = [(x-width*.5, z-height*.43), (x+width*.38, z-height*.5),
               (x+width*.5, z-height*.32), (x+width*.5, z+height*.5),
               (x-width*.43, z+height*.5), (x-width*.5, z+height*.38)]
    armor(w, name+" seam", outline, y+.018, .065, parent, "recess")
    armor(w, name, [(x+(a-x)*.95, z+(b-z)*.94) for a, b in outline], y, .042, parent, mat)
    for sx, sz in [(-.34, -.31), (.33, .31)]:
        w.bolt((x+width*sx, y-.018, z+height*sz), parent, .018)


def flange(w, pos, radius, depth, parent, axis=(0, -1, 0)):
    w.cyl("Slew bearing housing", pos, radius, depth, "joint", parent, axis, 40)
    w.cyl("Slew bearing rim", Vector(pos)+Vector(axis)*depth*.52,
          radius*.85, .045, "steel", parent, axis, 40)
    w.cyl("Bearing dust cap", Vector(pos)+Vector(axis)*(depth*.52+.032),
          radius*.55, .055, "armor", parent, axis)
    group = w.group("Flange bolt circle", Vector(pos)+Vector(axis)*(depth*.52+.07), parent)
    group.rotation_mode = "QUATERNION"
    group.rotation_quaternion = Vector(axis).to_track_quat("Z", "Y")
    for i in range(10):
        a = i*math.tau/10
        w.bolt((math.cos(a)*radius*.7, math.sin(a)*radius*.7, 0), group, .022, (0, 0, 1))


def ladder(w, pos, height, parent, width=.34):
    x, y, z = pos
    for sx in [-1, 1]:
        w.rod("Access ladder rail", (x+sx*width/2, y, z-height/2),
              (x+sx*width/2, y, z+height/2), .021, "steel", parent)
    count = max(2, round(height/.17))
    for i in range(count):
        zz = z-height/2+(i+.5)*height/count
        w.rod("Ladder rung", (x-width/2, y, zz), (x+width/2, y, zz), .021, "edge", parent)


def scoop(w, pos, width, parent, rot=(0, 0, 0), height=.95):
    group = w.group("Integral bent bucket", pos, parent, rot)
    stations = [(-.62, -.22), (-.35, -.11), (-.12, .17), (.03, height*.70), (-.04, height)]
    for j in range(len(stations)-1):
        ya, za = stations[j]
        yb, zb = stations[j+1]
        obj = w.mesh("Curved bucket sheet",
                     [(-width/2, ya, za), (width/2, ya, za), (width/2, yb, zb), (-width/2, yb, zb)],
                     [(0, 1, 2, 3)], "armor", group)
        obj.modifiers.new("Blade thickness", "SOLIDIFY").thickness = .085
    for side in [-1, 1]:
        obj = w.mesh("Bucket end cheek", [(side*width/2, -.67, -.23),
                     (side*width/2, .12, -.17), (side*width/2, .14, height),
                     (side*width/2, -.12, height*.96)], [(0, 1, 2, 3)], "steel", group)
        obj.modifiers.new("Cheek thickness", "SOLIDIFY").thickness = .07
        w.piston("Bucket lift ram", (side*width*.33, .37, -.22),
                 (side*width*.38, .14, height*.71), group, .078)
    for x in [-width*.38, -width*.13, width*.13, width*.38]:
        w.box("Blade welded rib", (x, .15, height*.4), (.065, .10, height*.85), "steel", group, .009)
    for i in range(7):
        x = (i-3)*width/7.4
        loft(w, "Replaceable forged tooth", [(-.30, width/10, .29, x, -.71),
             (-.22, width/8, .32, x, -.69)], group, "edge")
    return group
