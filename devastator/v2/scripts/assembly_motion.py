"""Deterministic assembly choreography; all controls return to their bind pose."""
import math

from mathutils import Euler, Matrix, Vector

FPS = 24
FRAMES = 432
SETTINGS = {"width": 1920, "height": 1080, "fps": FPS, "frames": FRAMES,
            "seconds": 18, "engine": "BLENDER_EEVEE", "samples": 64}
COLLECTION = "DEVASTATOR V2 | Assembly animation"
CAMERA = "V2 Assembly camera"
SCHEDULE = {
    "01 Pelvic load frame": ((0, .3, 3.0), (0, 0, -8), 3.3, 5.8),
    "02 Chest bridge and abdomen": ((0, 1.2, 4.4), (8, 0, -9), 4.5, 7.0),
    "03 Recessed helmet": ((0, -.5, 5.1), (0, 0, 24), 11.0, 12.5),
    "04 Excavator shoulder": ((-4.2, .5, 2.4), (0, -18, -12), 6.3, 9.0),
    "05 Dozer shoulder": ((4.2, .7, 2.4), (0, 18, 12), 6.7, 9.4),
    "06 Raised crushing arm": ((-4.6, -.2, .4), (0, -12, -8), 7.5, 10.8),
    "07 Cannon arm": ((4.6, 0, .3), (10, 14, 12), 7.8, 10.8),
    "08 Long armored cannon": ((4.5, -1.2, 2.0), (0, 25, -10), 12.5, 14.8),
    "09 Loader leg": ((-3.6, -.4, 1.9), (0, -12, -8), 1.0, 4.2),
    "10 Mixer leg": ((3.6, -.6, 2.1), (0, 12, 8), 1.5, 4.8),
    "11 Crane and powertrain": ((0, 4.0, 1.2), (0, 0, 0), 9.0, 12.8),
}
SECONDARY = {
    "06 Raised crushing arm / elbow": ("06 Raised crushing arm", (95, 0, 0), 8.0, 10.7),
    "07 Cannon arm / elbow": ("07 Cannon arm", (22, 0, 0), 8.4, 10.7),
    "11 Crane and powertrain / boom": ("11 Crane and powertrain", (-28, 0, 0), 10.0, 12.7),
}
BEATS = [(1, "Separated modules"), (25, "Loader approach"), (101, "Loader grounded"),
         (116, "Mixer grounded"), (140, "Pelvis locked"), (169, "Torso locked"),
         (226, "Shoulders locked"), (261, "Arms locked"), (308, "Head and back locked"),
         (357, "Cannon locked"), (361, "Completed sculpture"), (432, "Hero finish")]


def smooth(start, end, time):
    x = max(0.0, min(1.0, (time-start)/(end-start)))
    return x*x*x*(x*(x*6-15)+10)


def remaining(start, end, time):
    # Approach to a small gap, brief alignment pause, then a short locking move.
    duration = end-start
    approach = start+duration*.74
    latch = start+duration*.83
    if time <= approach:
        return 1-.955*smooth(start, approach, time)
    return .045*(1-smooth(latch, end, time))


def rotation(degrees, weight):
    return Euler(tuple(math.radians(v)*weight for v in degrees), "XYZ").to_matrix().to_4x4()


def control_matrix(key, rest, time):
    if key in SECONDARY:
        _, angles, start, end = SECONDARY[key]
        return rest @ rotation(angles, remaining(start, end, time))
    offset, angles, start, end = SCHEDULE[key]
    weight = remaining(start, end, time)
    return Matrix.Translation(Vector(offset)*weight) @ rest @ rotation(angles, weight)


def camera_matrix(time, distance_scale=1.0):
    approach = smooth(9, 16, time)
    target = Vector((.6, 0, 7.45-2.15*approach))
    radius = (61-21*approach)*distance_scale
    angle = math.radians(22+20*smooth(0, 18, time))
    offset = Vector((math.sin(angle), -math.cos(angle), .075))*radius
    orientation = (-offset).to_track_quat("-Z", "Y").to_matrix().to_4x4()
    return Matrix.Translation(target+offset) @ orientation


def linear_keys(obj):
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation = "LINEAR"
