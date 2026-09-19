"""Faceted chest, integrated crawler shoulders, heavy arms and long cannon."""
import math
import refinement
from parts import armor, loft, hatch, flange, ladder, scoop


def build_upper(w, assembly, pelvis):
    upper = w.group("Twisted upper-body frame", (0, .05, .52), pelvis, (.085, -.045, -.12))
    torso = assembly("02 Chest bridge and abdomen", (0, 0, 0), upper)
    flange(w, (0, 0, .03), .72, .45, torso, (0, 0, 1))
    for z in [.23, .36, .49]:
        w.ring("Protected waist bearing", (0, 0, z), .64, .060, "recess", torso)
    for sx in [-1, 1]:
        w.piston("Main spinal actuator", (sx*.66, .30, .09), (sx*.84, .30, 2.77), torso, .125)
        w.box("Open torso longitudinal rail", (sx*.86, .37, 1.72), (.24, .32, 2.72), "steel", torso)
        for z in [.89, 1.22, 1.55, 1.88]:
            armor(w, "Overlapping oblique lamella", [(sx*.49, z-.19), (sx*1.17, z-.08),
                  (sx*1.24, z+.14), (sx*.61, z+.18)], lambda x, zz: -.56+.26*abs(x), .18, torso)
        w.hose("Thoracic supply hose", [(sx*1.64, -.08, 2.63), (sx*1.14, -.35, 2.01),
               (sx*.70, -.45, .62)], .063, "recess", torso)
        w.hose("Secondary metallic conduit", [(sx*1.32, -.22, 2.45), (sx*.97, -.50, 1.72),
               (sx*.80, -.53, .65)], .029, "steel", torso)
        w.cyl("Waist accumulator", (sx*.95, .18, .59), .18, .69, "joint", torso)
    loft(w, "Central abdominal transmission", [(.36, 1.08, .95, 0, 0),
         (.91, 1.40, 1.16, 0, -.02), (1.74, 1.51, 1.18, 0, .06),
         (2.44, 1.88, 1.17, 0, .13)], torso, "joint")
    w.vent("Recessed abdominal radiator", (-.04, -.71, 1.16), .82, 1.05, torso, True, 17)
    w.rod("Radiator crash brace", (-.62, -.78, .61), (.47, -.78, 1.70), .036, "edge", torso)
    hatch(w, "Offset abdominal door", (-.73, -.65, .67), .48, .47, torso)
    ladder(w, (.73, -.70, 1.09), 1.05, torso, .25)
    for sx in [-1, 1]:
        armor(w, "Lower waist diagonal gusset", [(sx*.21, .34), (sx*.80, .46),
              (sx*.87, .73), (sx*.34, .69)], -.68, .12, torso)
        w.piston("Front lumbar load cylinder", (sx*.41, -.68, .16), (sx*.56, -.64, .72), torso, .062)
        w.tire("Folded abdominal vehicle wheel", (sx*1.14, .28, 1.92), .36, .20, torso)
        hatch(w, "Thoracic side valve block", (sx*.81, -.68, 1.75), .37, .41, torso, "steel")
        for j in range(3):
            w.cyl("Valve bank socket", (sx*.81, -.73, 1.64+j*.10), .031, .04, "recess",
                  torso, (0, -1, 0), 12)
    for sx in [-1, 1]:
        outline = [(sx*.12, 1.94), (sx*1.74, 2.35), (sx*1.91, 3.32), (sx*.13, 3.22)]
        armor(w, "Deep bridge subframe", outline, lambda x, z: -1.09+.20*abs(x), .65, torso, "joint")
        outline = [(sx*.15, 2.16), (sx*1.68, 2.49), (sx*1.73, 3.20), (sx*.15, 3.12)]
        armor(w, "Folded chest armor", outline, lambda x, z: -1.26+.20*abs(x), .17, torso)
        for dz in [0, .36, .69]:
            w.rod("Chest horizontal rail", (sx*.18, -1.24, 2.30+dz),
                  (sx*1.63, -.95, 2.61+dz*.73), .042, "edge", torso)
        for j in range(3):
            x, z = sx*(.43+j*.47), 2.69+j*.07
            y = -1.30+.20*abs(x)
            armor(w, "Chest inset subpanel", [(x-.17, z-.19), (x+.16, z-.13),
                  (x+.16, z+.17), (x-.17, z+.14)], y, .035, torso, "steel")
            w.box("Subpanel top edge", (x, y-.025, z+.15), (.28, .035, .028), "edge", torso, .004)
            w.bolt((x, y-.032, z-.09), torso, .020)
        w.piston("Chest locking column", (sx*1.56, -.96, 2.25), (sx*1.75, -.93, 3.30), torso, .092)
        w.rod("Lower chest diagonal strut", (sx*.32, -1.13, 1.90),
              (sx*1.51, -.96, 2.26), .065, "steel", torso)
        flange(w, (sx*1.98, .03, 2.90), .47, .54, torso, (sx, 0, 0))
        for j in range(3):
            w.box("Chest hinge knuckle", (sx*(.38+j*.45), -.88, 3.34),
                  (.27, .22, .15), "steel", torso, .012)
    armor(w, "Central chest keystone", [(-.26, 1.90), (.26, 1.90), (.32, 3.39), (-.32, 3.39)],
          -1.34, .22, torso)
    w.vent("Central lock slots", (0, -1.39, 2.34), .32, .59, torso, n=9)
    hatch(w, "Chest crest backing", (0, -1.38, 3.13), .36, .36, torso, "steel")
    for sx in [-1, 1]:
        w.rod("Central locking rod", (sx*.25, -1.46, 1.97), (sx*.25, -1.46, 3.01), .032, "edge", torso)

    head = assembly("03 Recessed helmet", (0, -.30, 3.69), upper, (.03, .03, .16))
    refinement.head(w, head)
    refinement.chest(w, torso)
    build_shoulders(w, assembly, upper)
    build_arms(w, assembly, upper)
    build_back(w, assembly, upper)
    return upper


def build_shoulders(w, assembly, upper):
    for sx in [-1, 1]:
        shoulder = assembly("04 Excavator shoulder" if sx < 0 else "05 Dozer shoulder",
                            (sx*2.54, .14, 2.93), upper, (0, sx*-.13, sx*.06))
        flange(w, (0, 0, -.12), .54, .83, shoulder, (1, 0, 0))
        loft(w, "Sloping shoulder counterweight", [(-.54, 1.35, 1.47, sx*.12, .12),
             (.08, 2.00, 1.72, 0, .16), (.76, 1.76, 1.47, -sx*.16, .20),
             (1.06, 1.20, 1.22, -sx*.29, .25)], shoulder)
        for yy in [-.72, .76]:
            w.track("Folded shoulder crawler", (sx*.14, yy, .13), 2.57, .40, .40,
                    shoulder, (0, -sx*.53, 0))
        armor(w, "Upper folded flank", [(-.78, .19), (.72, .42), (.51, 1.03), (-.64, .94)],
              -.76, .12, shoulder)
        w.vent("Shoulder engine intake", (-sx*.20, -.90, .75), .74, .24, shoulder, n=6)
        w.hose("Shoulder flex bundle", [(-sx*.8, .23, .69), (-sx*.91, -.24, .12),
               (-sx*.59, -.43, -.60)], .066, "recess", shoulder)
        if sx > 0:
            scoop(w, (.06, .28, .87), 2.26, shoulder, (.18, -.12, 0), .98)
        else:
            cab = w.group("Folded excavator cab", (-.20, -.81, .68), shoulder, (0, .25, 0))
            hatch(w, "Cab window gasket", (0, -.03, 0), .79, .40, cab, "recess")
            armor(w, "Cab armored glazing", [(-.32, -.11), (.31, -.16), (.30, .15), (-.33, .17)],
                  -.058, .016, cab, "glass")
            w.box("Cab window rib", (0, -.085, 0), (.034, .04, .32), "steel", cab, .003)
            w.box("Stowed excavator stick", (.10, .72, .60), (.42, .35, 1.90),
                  "joint", shoulder, .02, (0, -.37, 0))
            w.piston("Stowed boom ram", (-.32, .94, -.26), (.26, .94, 1.15), shoulder, .085)
        refinement.shoulder(w, shoulder, sx)


def make_hand(w, parent, pos):
    hand = w.group("Articulated mechanical hand", pos, parent)
    flange(w, (0, 0, .21), .30, .30, hand, (0, 0, 1))
    loft(w, "Faceted palm chassis", [(-.43, .98, .71, 0, -.02),
         (.18, 1.06, .77, 0, 0), (.31, .72, .65, 0, .02)], hand, "joint")
    for i in range(4):
        x = (i-1.5)*.25
        for j in range(3):
            w.box("Stepped finger phalanx", (x, -.26-j*.13, -.24-j*.20),
                  (.224, .25, .26), "armor", hand, .025, (.20+j*.37, 0, 0))
            w.cyl("Finger hinge pin", (x, -.22-j*.13, -.24-j*.20), .065, .235,
                  "steel", hand, (1, 0, 0), 12)
        armor(w, "Individual knuckle shield", [(x-.105, -.06), (x+.105, -.06),
              (x+.095, .20), (x-.085, .23)], -.435, .055, hand)
    w.box("Thumb metacarpal", (-.57, -.13, -.14), (.27, .34, .43), "armor", hand, .03, (0, -.4, 0))
    w.box("Curled thumb tip", (-.47, -.42, -.40), (.26, .31, .29), "steel", hand, .025, (.55, 0, 0))
    refinement.hand(w, hand)
    return hand


def build_arms(w, assembly, upper):
    for sx in [-1, 1]:
        arm = assembly("06 Raised crushing arm" if sx < 0 else "07 Cannon arm",
                       (sx*2.47, -.06, 2.87), upper, (0, -.29*sx, -.02*sx))
        flange(w, (0, 0, -.22), .43, 1.09, arm, (1, 0, 0))
        loft(w, "Tapered upper-arm link", [(-1.39, .86, .90, 0, 0),
             (-.42, 1.13, 1.14, 0, 0), (-.08, .86, .86, 0, .04)], arm, "joint")
        armor(w, "Split biceps shield", [(-.53, -.35), (-.38, -1.24), (.35, -1.33),
              (.56, -.41), (.33, -.23)], -.60, .16, arm)
        for side in [-1, 1]:
            w.piston("Biceps load ram", (side*.43, .17, -.22), (side*.46, .19, -1.38), arm, .09)
        elbow = w.group("Bent elbow", (0, 0, -1.43), arm,
                        (math.radians(-144 if sx < 0 else -18), .06 if sx < 0 else -.09, 0))
        flange(w, (0, 0, 0), .36, 1.31, elbow, (1, 0, 0))
        loft(w, "Forearm actuator cage", [(-1.92, .95, 1.10, 0, -.05),
             (-1.43, 1.36, 1.37, 0, .02), (-.27, 1.48, 1.46, 0, .04),
             (-.08, 1.13, 1.11, 0, .06)], elbow, "joint")
        armor(w, "Forearm sweeping outer plate", [(-.65, -.21), (.62, -.13), (.76, -.48),
              (.62, -1.40), (.38, -1.74), (-.46, -1.71), (-.71, -1.29)],
              lambda x, z: -.77+.11*abs(x)+.04*z, .17, elbow)
        armor(w, "Inset forearm stepped plate", [(-.48, -.36), (.41, -.32), (.49, -.62),
              (.34, -1.19), (-.39, -1.28)], -.81, .065, elbow, "steel")
        hatch(w, "Forearm access", (-.11, -.88, -.80), .55, .56, elbow)
        w.vent("Forearm cooling bank", (.05, -.83, -.35), .76, .19, elbow, n=4)
        for side in [-1, 1]:
            w.cyl("Integrated accumulator", (side*.75, .20, -.85), .21, 1.22, "armor", elbow)
            for z in [-1.34, -.42]:
                w.ring("Accumulator clamp", (side*.75, .20, z), .217, .035, "edge", elbow)
            w.hose("Forearm rigid pipe", [(side*.55, -.74, -.31), (side*.63, -.84, -.62),
                   (side*.45, -.87, -1.40)], .037, "steel", elbow)
            w.box("Forearm edge reinforcement", (side*.61, -.70, -.91),
                  (.11, .15, 1.18), "edge", elbow, .016, (0, side*.12, 0))
        for z in [-1.44, -1.59, -1.74]:
            armor(w, "Overlapping wrist sleeve", [(-.55, z-.06), (.54, z-.06),
                  (.57, z+.07), (-.58, z+.10)], -.70, .15, elbow)
        rear = w.group("Forearm rear panels", (0, .70, -.91), elbow, (0, 0, math.pi))
        hatch(w, "Rear forearm shell", (0, -.03, 0), 1.12, 1.09, rear)
        w.vent("Rear forearm exhaust", (0, -.09, .22), .67, .37, rear, n=8)
        armor(w, "Rear forearm folded upper shield", [(-.52, .53), (.51, .53),
              (.55, .89), (.36, 1.03), (-.48, .98)], -.08, .12, rear)
        for side in [-1, 1]:
            w.rod("Forearm rear cooling pipe", (side*.44, -.18, -.65),
                  (side*.44, -.18, .73), .035, "steel", rear)
            for z in [-.50, -.05, .51]:
                w.box("Rear pipe mounting saddle", (side*.44, -.18, z),
                      (.12, .12, .09), "edge", rear, .008)
        hatch(w, "Forearm dorsal upper cover", (-.12, -.21, .70), .49, .30, rear, "steel")
        w.cyl("Forearm dorsal rotary cover", (.18, -.17, -.39), .19, .08, "steel", rear, (0, -1, 0))
        for z in [-.73, -.87]:
            w.box("Forearm dorsal cuff ridge", (0, -.08, z), (.91, .13, .075), "edge", rear, .012)
        refinement.forearm(w, elbow)
        hand = make_hand(w, elbow, (0, -.04, -2.07))
        if sx > 0:
            build_cannon(w, assembly, hand)


def build_cannon(w, assembly, hand):
    gun = assembly("08 Long armored cannon", (.04, -.17, -.39), hand, (0, -.68, 0))
    loft(w, "Cannon armored receiver", [(-1.12, .66, .75, 0, .04),
         (-.84, .94, .88, 0, .02), (.17, .78, .84, 0, 0)], gun, "joint")
    armor(w, "Receiver folded fairing", [(-.47, .09), (.37, .14), (.46, -.85),
          (.24, -1.16), (-.34, -1.09)], -.46, .12, gun)
    w.vent("Receiver thermal slots", (0, -.59, -.43), .51, .36, gun, n=6)
    w.cyl("Breech collar", (0, 0, -1.12), .39, .28, "steel", gun, n=40)
    for x, y in [(-.16, -.16), (.16, -.16), (-.16, .16), (.16, .16)]:
        w.cyl("Independent cannon bore", (x, y, -2.78), .12, 3.39, "steel", gun)
    for z in [-1.43, -2.29, -3.49, -4.41]:
        w.ring("Cannon barrel lock", (0, 0, z), .37, .055, "joint", gun)
    for side in [-1, 1]:
        armor(w, "Long angular cannon shroud",
              [(side*.24, -1.25), (side*.45, -1.40), (side*.36, -4.33),
               (side*.22, -4.55), (side*.14, -4.27)], -.35, .70, gun)
        w.box("Cannon continuous armor rail", (side*.27, -.46, -2.83),
              (.10, .11, 2.42), "edge", gun, .012)
        for z in [-1.62, -2.02, -2.50, -3.13, -3.84]:
            hatch(w, "Cannon service inset", (side*.29, -.42, z), .13, .25, gun, "steel")
        w.rod("Cannon longitudinal coolant line", (side*.40, .30, -1.49),
              (side*.33, .30, -4.19), .034, "steel", gun)
        for z in [-1.60, -3.88]:
            w.box("Cannon coolant clamp", (side*.39, .30, z), (.15, .17, .12),
                  "joint", gun, .012)
    loft(w, "Faceted muzzle housing", [(-4.70, .70, .71, 0, 0), (-4.51, .79, .80, 0, 0),
         (-3.93, .61, .64, 0, 0)], gun)
    for x, y in [(-.16, -.16), (.16, -.16), (-.16, .16), (.16, .16)]:
        w.cyl("Muzzle bore recess", (x, y, -4.716), .13, .012, "recess", gun)
        w.ring("Muzzle bore edge", (x, y, -4.725), .134, .018, "steel", gun)


def build_back(w, assembly, upper):
    back = assembly("11 Crane and powertrain", (0, .85, 1.73), upper)
    for side in [-1, 1]:
        w.box("Back structural channel", (side*.82, .36, .14), (.24, .32, 2.31), "armor", back, .018)
        for z in [-.66, .02, .83]:
            w.rod("Back powertrain brace", (side*.75, .48, z), (-side*.69, .48, z+.52), .058, "steel", back)
        w.cyl("Exposed powertrain turbine", (side*.55, .57, -.59), .29, .92, "steel", back)
        for z in [-.95, -.67, -.36, -.15]:
            w.ring("Turbine band", (side*.55, .57, z), .302, .045, "joint", back)
        w.cyl("Back exhaust outlet", (side*.85, .54, .27), .14, .35, "edge", back, (0, 1, 0))
        w.cyl("Back exhaust bore", (side*.85, .728, .27), .108, .008, "recess", back, (0, 1, 0))
        w.hose("Back manifold", [(side*.92, .52, .86), (side*.35, .65, .39),
               (side*.45, .64, -.60)], .043, "recess", back)
    crane = w.group("Folded telescopic crane", (0, .94, .15), back, (0, -.15, 0))
    for side in [-1, 1]:
        armor(w, "Crane telescopic channel", [(side*.26, -2.34), (side*.50, -2.15),
              (side*.58, 1.79), (side*.29, 2.04)], -.15, .35, crane)
        w.rod("Crane lifting cable", (side*.16, .24, -2.51), (side*.16, .24, 2.09), .019, "recess", crane)
        for z in [-1.74, -.89, .01, .83, 1.62]:
            w.box("Crane sliding block", (side*.41, -.23, z), (.15, .16, .22), "steel", crane, .012)
    w.box("Crane tip crosshead", (0, .04, 2.12), (1.14, .46, .28), "armor", crane)
    w.box("Crane hook block", (0, .14, -2.65), (.54, .40, .29), "edge", crane)
    w.cyl("Crane hook swivel", (0, .15, -2.86), .09, .16, "joint", crane)
    w.hose("Open forged crane hook", [(0, .15, -2.89), (-.14, .15, -3.03),
           (-.06, .15, -3.18), (.13, .15, -3.15), (.16, .15, -3.03)], .054, "steel", crane)
    ladder(w, (1.04, .59, -.08), 1.73, back, .24)
    refinement.back(w, back, crane)
