"""Endpoint-defined loaded legs and integrated loader/mixer feet."""
import math
import refinement
from mathutils import Vector
from parts import armor, loft, hatch, flange, ladder, scoop


def build_pelvis(w, assembly):
    pelvis = assembly("01 Pelvic load frame", (0, 0, 5.56), rot=(0, .035, .02))
    loft(w, "Tapered pelvic crossframe", [(-.30, 1.82, 1.25, 0, 0),
         (.18, 2.30, 1.43, 0, .08), (.47, 1.80, 1.24, 0, .10)], pelvis, "joint")
    for sx in [-1, 1]:
        side = w.group("Floating hip armor", (sx*.92, -.77, .01), pelvis, (0, sx*-.15, sx*-.07))
        armor(w, "Sloping hip skirt", [(-.51, -.42), (.37, -.56), (.57, .20),
              (.39, .39), (-.49, .33)], -.05, .17, side)
        w.vent("Pelvic intake bank", (-.03, -.09, .10), .58, .25, side, n=7)
        w.piston("Hip skirt linkage", (sx*.72, .05, .20), (sx*1.04, -.18, -.34), pelvis, .06)
        w.tire("Folded chassis hip wheel", (sx*1.21, .22, -.07), .53, .27, pelvis)
    armor(w, "Split pelvic apron", [(-.34, .18), (.34, .18), (.28, -.91),
          (.12, -1.12), (-.29, -.96)], -.78, .17, pelvis)
    hatch(w, "Apron lock plate", (0, -.82, -.46), .33, .71, pelvis, "steel")
    return pelvis


def build_legs(w, assembly):
    specifications = [
        (-1, (-.94, 0, 5.40), (-1.48, -.15, 3.44), (-1.84, .20, .43), -.045, 0),
        (1, (.99, .03, 5.37), (1.73, -.82, 3.46), (2.16, -.94, .63), .06, .20),
    ]
    soles = []
    for sx, hip, knee, ankle, yaw, ground in specifications:
        leg = assembly("09 Loader leg" if sx < 0 else "10 Mixer leg", hip)
        a, b, c = Vector(hip), Vector(knee), Vector(ankle)
        thigh = w.group("Angled thigh", (0, 0, 0), leg)
        thigh.rotation_mode = "QUATERNION"
        thigh.rotation_quaternion = Vector((0, 0, -1)).rotation_difference((b-a).normalized())
        length = (b-a).length
        flange(w, (0, 0, 0), .42, 1.25, thigh, (1, 0, 0))
        loft(w, "Thigh vehicle crossmember", [(-length+.13, .87, .84, 0, .03),
             (-.66, 1.16, 1.08, 0, .04), (-.18, 1.08, .98, 0, .04)], thigh, "joint")
        armor(w, "Tapered split thigh", [(-.54, -.27), (.47, -.21), (.57, -.65),
              (.39, -length+.27), (-.40, -length+.22)], lambda x, z: -.61+.05*abs(x), .14, thigh)
        armor(w, "Thigh recessed center", [(-.23, -.39), (.24, -.35),
              (.19, -1.38), (-.28, -1.51)], -.655, .040, thigh, "joint")
        hatch(w, "Thigh upper latch", (-.08, -.72, -.60), .41, .28, thigh, "steel")
        w.vent("Thigh narrow intake", (.07, -.71, -1.08), .28, .30, thigh, n=6)
        for side in [-1, 1]:
            armor(w, "Thigh edge folded rail", [(side*.35, -.35), (side*.47, -.39),
                  (side*.36, -1.55), (side*.25, -1.49)], -.71, .09, thigh, "edge")
        for side in [-1, 1]:
            w.piston("Thigh side actuator", (side*.44, -.22, -.27),
                     (side*.34, -.25, -length+.14), thigh, .072)
            w.rod("Thigh exposed conduit", (side*.31, -.71, -.55),
                  (side*.29, -.71, -1.48), .028, "steel", thigh)
        w.tire("Large folded thigh wheel", (sx*.68, .25, -.73), .51, .26, thigh)
        rear_thigh = w.group("Rear articulated thigh drive", (0, .61, -.88), thigh, (0, 0, math.pi))
        flange(w, (0, -.06, .29), .24, .10, rear_thigh)
        hatch(w, "Thigh transmission bracket", (0, -.07, -.28), .55, .46, rear_thigh, "steel")
        for side in [-1, 1]:
            w.piston("Rear thigh guide", (side*.38, -.03, -.67),
                     (side*.40, -.03, .57), rear_thigh, .05)
            w.hose("Rear thigh bent line", [(side*.21, -.21, -.48),
                   (side*.28, -.25, -.04), (side*.17, -.22, .40)], .024, "recess", rear_thigh)
        flange(w, (0, 0, -length), .35, 1.24, thigh, (1, 0, 0))
        armor(w, "Angled knee shield", [(-.47, -length+.28), (.43, -length+.24),
              (.52, -length-.10), (.31, -length-.40), (-.38, -length-.34)], -.59, .20, thigh)
        for j in range(3):
            w.box("Knee forged reinforcement", (0, -.82, -length+.08-j*.10),
                  (.67-j*.04, .08, .045), "edge", thigh, .008)
        shin = w.group("Lower vehicle frame", b-a, leg)
        shin.rotation_mode = "QUATERNION"
        shin.rotation_quaternion = Vector((0, 0, -1)).rotation_difference((c-b).normalized())
        length = (c-b).length
        for side in [-1, 1]:
            w.box("Longitudinal chassis rail", (side*.55, .41, -length*.48),
                  (.19, .24, length*.97), "steel", shin, .016)
            for z in [-.58, -1.86]:
                w.tire("Tandem road wheel", (side*.81, .22, z), .45, .29, shin)
            w.piston("Long ankle suspension", (side*.57, .05, -.44),
                     (side*.53, .06, -length+.12), shin, .094)
        for z in [-.30, -1.29, -2.35]:
            w.box("Open chassis crossbeam", (0, .49, z), (1.27, .26, .17), "joint", shin, .014)
        if sx < 0:
            loft(w, "Loader folded engine structure", [(-2.74, .93, 1.11, 0, .10),
                 (-2.22, 1.29, 1.29, 0, .08), (-.67, 1.42, 1.21, .02, .08),
                 (-.12, 1.09, .96, .02, .10)], shin)
            armor(w, "Loader split front armor", [(-.61, -.38), (.58, -.29), (.62, -1.46),
                  (.38, -1.60), (.45, -2.45), (-.45, -2.64), (-.56, -1.59)], -.68, .12, shin)
            armor(w, "Loader central undercut", [(-.26, -.67), (.25, -.64),
                  (.26, -2.37), (-.30, -2.31)], -.82, .045, shin, "joint")
            w.vent("Loader engine radiator", (0, -.87, -.64), .59, .32, shin, n=8)
            hatch(w, "Offset engine access", (-.05, -.89, -1.28), .50, .56, shin)
            w.vent("Engine access ventilation", (-.05, -.95, -1.23), .32, .24, shin, n=5)
            hatch(w, "Loader inspection door", (-.05, -.87, -2.03), .46, .40, shin, "steel")
            for j in range(3):
                w.box("Loader lower step reinforcement", (-.04, -.91, -2.15-j*.13),
                      (.53-j*.06, .16, .068), "edge", shin, .011)
            for side in [-1, 1]:
                w.box("Loader structural rib", (side*.45, -.79, -1.42), (.13, .16, 2.03),
                      "edge", shin, .015, (0, side*-.025, 0))
            w.cyl("Loader exhaust", (-.61, .40, -.27), .083, 1.25, "steel", shin)
            w.cyl("Exhaust heat shield", (-.61, .40, -.51), .122, .63, "armor", shin)
            ladder(w, (.47, -.85, -1.61), 1.28, shin, .23)
        else:
            drum = w.group("Mixer drum axis", (0, -.43, -1.18), shin, (.06, 0, 0))
            w.barrel("Full concrete mixer vessel", (0, 0, 0), [(-1.04, .39), (-.84, .65),
                     (-.48, .82), (.37, .82), (.69, .58), (.98, .34)], drum)
            for z, r in [(-.84, .66), (-.45, .833), (.30, .833), (.67, .60)]:
                w.ring("Mixer load bearing band", (0, 0, z), r, .043, "edge", drum)
            for i in range(12):
                a0, a1 = i*math.tau/12, i*math.tau/12+math.tau/25
                points = [(.825*math.cos(a), .825*math.sin(a), z)
                          for z in [-.44, .28] for a in [a0, a1]]
                w.mesh("Mixer hazard belt", points, [(0, 1, 3, 2)], "recess", drum)
            flange(w, (0, 0, .98), .34, .21, drum, (0, 0, 1))
            ladder(w, (.86, -.19, -1.28), 1.84, shin, .26)
            w.hose("Mixer discharge line", [(-.69, .03, -.37), (-.91, .05, -1.33),
                   (-.72, -.13, -2.30)], .075, "rubber", shin)
        rear = w.group("Rear vehicle face", (0, .68, -1.40), shin, (0, 0, math.pi))
        for side in [-1, 1]:
            hatch(w, "Rear chassis guard", (side*.43, -.06, .12), .27, 1.82, rear)
        w.vent("Open rear radiator bank", (0, -.04, .24), .45, .80, rear, True, 9)
        w.piston("Rear central damper", (-.09, -.18, -.91), (-.09, -.18, -.19), rear, .073)
        w.rod("Rear diagonal tie", (-.57, -.08, -.72), (.58, -.08, .96), .035, "steel", rear)
        refinement.lower_shell(w, shin, sx < 0)
        foot = w.group("Planted vehicle foot", c-a, leg, (0, 0, yaw))
        sole = w.box("Foot contact sole", (0, -.43, -.33), (1.94, 2.62, .20), "joint", foot, .028)
        soles.append((sole, ground))
        loft(w, "Load-spreading foot", [(-.24, 2.06, 2.55, 0, -.46),
             (-.02, 1.90, 2.35, 0, -.40), (.19, 1.56, 1.79, 0, -.17)], foot)
        for i in [-1, 0, 1]:
            armor(w, "Separate toe impact shoe", [(i*.59-.23, -.20), (i*.59+.23, -.20),
                  (i*.59+.20, .09), (i*.59-.18, .13)], -1.78, .49, foot, "edge")
        if sx < 0:
            scoop(w, (0, -.67, .15), 1.92, foot, (.12, 0, 0), .58)
            for side in [-1, 1]:
                w.piston("Foot bucket ram", (side*.65, .36, .64), (side*.73, -.93, .20), foot, .095)
        else:
            build_cab(w, foot)
    return soles


def build_cab(w, foot):
    loft(w, "Mixer truck cab shell", [(0, 1.71, 1.18, 0, -.57),
         (.62, 1.69, 1.27, 0, -.52), (1.16, 1.49, .99, 0, -.42)], foot)
    armor(w, "Cab windscreen inset", [(-.70, .62), (.70, .62), (.63, 1.04), (-.64, 1.04)],
          lambda x, z: -1.25+.32*(z-.62), .035, foot, "recess")
    for side in [-1, 1]:
        armor(w, "Laminated cab glass", [(side*.05, .66), (side*.63, .66),
              (side*.58, 1.00), (side*.05, 1.00)],
              lambda x, z: -1.269+.32*(z-.62), .018, foot, "glass")
        w.rod("Windshield wiper", (side*.51, -1.28, .67), (side*.16, -1.205, .87), .012, "steel", foot)
        hatch(w, "Cab front panel", (side*.59, -1.25, .40), .34, .22, foot)
        for j in [-1, 1]:
            w.cyl("Twin truck headlight", (side*.67+j*.051, -1.27, .18), .044, .035,
                  "optic", foot, (0, -1, 0))
        w.rod("Mirror bracket", (side*.68, -.93, 1.02), (side*.91, -.96, .97), .023, "steel", foot)
        w.box("Rear-view mirror", (side*.93, -.96, .88), (.12, .07, .22), "joint", foot, .015)
    w.vent("Truck lower radiator", (0, -1.25, .20), .99, .21, foot, n=5)
    w.box("Truck crash bumper", (0, -1.40, -.01), (1.76, .22, .16), "edge", foot, .018)
    for sx in [-1, 1]:
        hatch(w, "Cab front hood quarter", (sx*.31, -1.27, .43), .40, .18, foot)
        w.box("Cab bumper mounting cleat", (sx*.49, -1.54, .03), (.14, .12, .19), "joint", foot, .012)
    refinement.cab(w, foot)
