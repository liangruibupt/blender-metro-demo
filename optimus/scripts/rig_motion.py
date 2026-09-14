"""Shared Blender-side pose evaluation for asset creation and collision audits."""

import math

from mathutils import Euler, Matrix, Vector

C = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))


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
    if motion.get("type") == "weapon_fold":
        # Half turns have two equally short quaternion paths; choose the outward arc.
        orient = Euler((0, 0, motion["side"]*math.pi*t), "XYZ").to_quaternion()
    if motion.get("type") == "weapon_carrier":
        position.z = .38+.48*ramp(transform, 0, .08)-2.46*ramp(transform, .30, .55)
        position.x += motion["side"]*1.20*ramp(transform, .38, .50)*(1-ramp(transform, .92, 1))
    if motion.get("type") == "bogie":
        # Extend outside the calf before crossing its depth, then close the carriage.
        position.x = motion["side"]*(ramp(transform, .04, .14)-.42*ramp(transform, .28, .40))
        position.z = 2*ramp(transform, .14, .28)
    if motion.get("type") == "roof":
        position.x += motion["side"]*.84*ramp(transform, .02, .12)*(1-ramp(transform, .38, .53))
    if motion.get("type") == "shoulder":
        slide = ramp(transform, .66, .90)
        position.x = entry["robot"][0]*(1-slide)+entry["truck"][0]*slide
        position.x += motion["side"]*.43*ramp(transform, .12, .24)*(1-ramp(transform, .66, .90))
        lower = ramp(transform, .46, .65)
        position.y = entry["robot"][1]*(1-lower)+entry["truck"][1]*lower
    if motion.get("type") == "axle":
        position.x += motion["side"]*.55*ramp(transform, .66, .80)*(1-ramp(transform, .92, 1))
    if motion.get("type") == "lift":
        position.y += .30*ramp(transform, .02, .10)*(1-ramp(transform, .35, .50))
    if motion.get("type") == "grounded":
        curve = motion["heightCurve"]
        cursor = min(1, max(0, transform))*(len(curve)-1)
        index = min(len(curve)-2, int(cursor))
        fraction = cursor-index
        position.y = curve[index]*(1-fraction)+curve[index+1]*fraction
    amount = explosion
    if assembly is not None:
        amount = 1-ramp(assembly, entry["order"]*.075, entry["order"]*.075+.36)
    position += Vector(entry["explode"])*amount
    return C @ position, (C @ orient.to_matrix() @ C.inverted()).to_quaternion()


def matrices(joints, transform):
    result = {}
    for entry in joints:
        position, quaternion = pose(entry, transform)
        local = Matrix.LocRotScale(position, quaternion, Vector((1, 1, 1)))
        result[entry["id"]] = result[entry["parent"]] @ local if entry["parent"] else local
    return result
