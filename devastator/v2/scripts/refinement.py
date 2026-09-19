"""Video-guided shell segmentation and visible mechanical transitions."""
import math

from parts import armor, flange, hatch, loft


def head(w, parent):
    loft(w, "Swept helmet shell", [(-.18, .76, .67, 0, .12), (.29, 1.00, .81, 0, .12),
         (.52, .88, .72, 0, .14), (.64, .58, .56, 0, .16)], parent)
    flange(w, (0, .10, -.20), .25, .23, parent, (0, 0, 1))
    armor(w, "Dark recessed facial opening", [(-.31, -.19), (.31, -.19), (.38, .31),
          (.22, .39), (-.24, .39), (-.38, .29)], -.365, .045, parent, "recess")
    for sx in [-1, 1]:
        armor(w, "Swept temple armor", [(sx*.29, -.15), (sx*.47, -.06), (sx*.52, .34),
              (sx*.34, .48), (sx*.24, .36)], lambda x, z: -.47+.25*abs(x), .22, parent)
        armor(w, "Separated brow blade", [(sx*.025, .30), (sx*.35, .34),
              (sx*.34, .405), (sx*.045, .39)], -.485, .11, parent, "edge")
        armor(w, "Narrow inset visor", [(sx*.065, .22), (sx*.285, .245),
              (sx*.305, .29), (sx*.06, .275)], -.515, .022, parent, "optic")
        armor(w, "Cheekbone wedge", [(sx*.07, -.075), (sx*.245, -.10),
              (sx*.30, .11), (sx*.21, .16)], lambda x, z: -.54+.20*abs(x), .07, parent, "steel")
        armor(w, "Jaw side articulated plate", [(sx*.11, -.29), (sx*.31, -.19),
              (sx*.33, -.04), (sx*.25, .035), (sx*.14, -.09)], -.425, .16, parent)
        w.cyl("Recessed temple pivot", (sx*.50, .12, .22), .095, .045,
              "joint", parent, (sx, 0, 0))
        w.cyl("Temple pivot pin", (sx*.525, .12, .22), .043, .025,
              "steel", parent, (sx, 0, 0), 12)
        side = w.group("Helmet side vent", (sx*.48, .14, .02), parent,
                       (0, 0, sx*math.pi/2))
        w.vent("Temple cooling slots", (0, 0, 0), .20, .12, side, n=3)
    armor(w, "Nasal bridge", [(-.065, .015), (.065, .015), (.047, .29), (-.047, .29)],
          lambda x, z: -.55+.12*z, .085, parent, "edge")
    armor(w, "Angular chin", [(-.15, -.12), (.15, -.12), (.13, -.26), (0, -.32),
          (-.13, -.26)], -.49, .105, parent, "steel")
    w.box("Mouth shadow", (0, -.505, -.105), (.22, .022, .036), "recess", parent, .003)
    for z in [-.075, -.143]:
        w.box("Facial lip ridge", (0, -.518, z), (.22, .04, .020), "edge", parent, .003)
    armor(w, "Raised helmet central crest", [(-.11, .43), (.11, .43), (.095, .61),
          (-.10, .61)], -.215, .095, parent, "steel")
    for sx in [-1, 1]:
        w.rod("Crown seam", (sx*.21, -.23, .52), (sx*.27, .24, .60), .015, "joint", parent)
    rear = w.group("Rear helmet service plate", (0, .54, .14), parent, (0, 0, math.pi))
    hatch(w, "Occipital service cover", (0, 0, 0), .44, .37, rear)
    w.vent("Helmet rear slots", (0, -.055, .04), .28, .14, rear, n=3)


def chest(w, parent):
    for sx in [-1, 1]:
        side = w.group("Chest bridge return wall", (sx*1.79, -.26, 2.75), parent,
                       (0, 0, sx*math.pi/2))
        armor(w, "Chest return folded shell", [(-.45, -.39), (.35, -.30), (.41, .37),
              (-.31, .43)], -.045, .13, side)
        w.vent("Bridge side recessed radiator", (0, -.09, .08), .51, .30, side, True, 7)
        w.rod("Return wall lower seam", (-.34, -.12, -.24), (.27, -.12, -.19), .018, "joint", side)
        w.piston("Chest return lock", (-.29, -.12, -.26), (-.26, -.10, .30), side, .037)
        for j in range(3):
            x = sx*(.42+j*.43)
            y = -1.32+.20*abs(x)
            armor(w, "Chest lower segmented skirt", [(x-.16, 2.20+.20*abs(x)),
                  (x+.15, 2.20+.20*abs(x)), (x+.17, 2.39+.20*abs(x)),
                  (x-.15, 2.40+.20*abs(x))], y, .06, parent, "steel")
        equipment = w.group("Side abdominal equipment", (sx*1.01, .07, 1.15), parent,
                            (0, 0, sx*math.pi/2))
        hatch(w, "Abdominal transmission case", (0, 0, 0), .72, .71, equipment, "joint")
        flange(w, (0, -.095, -.06), .19, .075, equipment)
        w.vent("Transmission upper radiator", (0, -.06, .24), .41, .14, equipment, n=3)
        for offset in [-.25, .25]:
            w.hose("Abdominal return line", [(offset, -.03, -.34), (offset, -.13, -.49),
                   (offset*.68, -.14, -.65)], .025, "steel", equipment)
    hatch(w, "Chest center recessed lock", (0, -1.39, 2.78), .32, .25, parent, "joint")
    w.cyl("Central quarter-turn latch", (0, -1.455, 2.78), .066, .03,
          "steel", parent, (0, -1, 0), 6)


def shoulder(w, parent, sx):
    side = w.group("Shoulder outer vehicle face", (sx*.86, .16, .47), parent,
                   (0, 0, sx*math.pi/2))
    armor(w, "Counterweight segmented flank", [(-.49, -.22), (.51, -.15),
          (.41, .32), (-.28, .49), (-.50, .24)], -.06, .12, side)
    hatch(w, "Counterweight service hatch", (.03, -.10, .10), .53, .36, side)
    w.vent("Shoulder side cooling slots", (.04, -.17, .10), .34, .18, side, n=4)
    top = w.group("Shoulder machinery deck", (-sx*.19, .17, 1.035), parent,
                  (-math.pi/2, 0, 0))
    hatch(w, "Engine deck recessed access", (0, 0, 0), .89, .62, top, "steel")
    w.vent("Top deck engine louvers", (0, -.06, .03), .62, .38, top, n=7)
    for x in [-.43, .43]:
        w.rod("Deck grab rail", (x, -.10, -.22), (x, -.10, .24), .021, "steel", top)
    rear = w.group("Shoulder rear articulation", (0, 1.01, .54), parent, (0, 0, math.pi))
    for x in [-.36, .36]:
        hatch(w, "Rear shoulder hinged cover", (x, 0, .05), .50, .42, rear)
        w.rod("Shoulder cover hinge", (x-.17, -.06, -.18), (x+.17, -.06, -.18), .028, "joint", rear)
    w.hose("Shoulder external return pipe", [(-.61, -.05, -.15), (-.61, -.20, .31),
           (-.34, -.15, .39)], .027, "steel", rear)


def forearm(w, parent):
    for sx in [-1, 1]:
        side = w.group("Forearm lateral mechanism", (sx*.77, -.10, -.89), parent,
                       (0, 0, sx*math.pi/2))
        armor(w, "Segmented side cheek", [(-.45, -.46), (.25, -.55), (.40, -.27),
              (.39, .44), (.18, .59), (-.42, .47)], -.025, .10, side)
        hatch(w, "Forearm lateral inset", (-.06, -.06, .05), .54, .58, side, "steel")
        w.vent("Lateral oil cooler", (-.06, -.115, .17), .32, .18, side, n=4)
        w.piston("Forearm side linkage", (-.29, -.16, -.38), (-.29, -.16, .43), side, .045)
        for z in [-.32, .34]:
            w.cyl("Side plate latch", (.20, -.13, z), .06, .045,
                  "joint", side, (0, -1, 0), 12)
    for x in [-.32, .17]:
        hatch(w, "Forearm front split field", (x, -.855, -1.16), .28, .27, parent)
    w.rod("Wrist rim lower rail", (-.46, -.82, -1.64), (.45, -.82, -1.64), .033, "joint", parent)


def hand(w, parent):
    dorsal = w.group("Hand dorsal armor", (0, .39, 0), parent, (0, 0, math.pi))
    for i in range(4):
        x = (i-1.5)*.25
        armor(w, "Separate hand dorsal plate", [(x-.107, -.34), (x+.103, -.34),
              (x+.109, .11), (x+.06, .22), (x-.08, .18)], -.025, .065, dorsal)
        w.rod("Dorsal finger drive rail", (x, -.105, -.22), (x, -.105, .06),
              .022, "steel", dorsal)
        w.cyl("Dorsal knuckle bearing", (x, -.09, -.33), .070, .04,
              "joint", dorsal, (0, -1, 0), 12)
    for i in range(4):
        x = (i-1.5)*.25
        armor(w, "Dorsal metacarpal armor", [(x-.10, -.37), (x+.105, -.35),
              (x+.095, -.03), (x-.085, .04)], -.40, .07, parent, "armor")
        w.rod("Finger tendon", (x, -.455, -.08), (x, -.455, -.30), .022, "steel", parent)
        w.cyl("Knuckle pivot cap", (x, -.435, -.35), .072, .028,
              "joint", parent, (0, -1, 0), 12)
        for j in range(2):
            w.box("Finger joint crease", (x, -.47-j*.13, -.39-j*.20),
                  (.18, .035, .035), "recess", parent, .004)
    w.box("Thumb dorsal shield", (-.58, -.30, -.12), (.20, .12, .29),
          "edge", parent, .018, (0, -.4, 0))


def lower_shell(w, parent, loader):
    for sx in [-1, 1]:
        side = w.group("Leg vehicle lateral shell", (sx*.63, .01, -1.25), parent,
                       (0, 0, sx*math.pi/2))
        for z, width, height in [(.69, .86, .39), (.02, .82, .63), (-.76, .70, .48)]:
            hatch(w, "Loader side service door" if loader else "Mixer side hydraulic cover",
                  (0, -.015, z), width, height, side)
        w.vent("Vehicle lateral engine louvers", (0, -.08, .09), .47, .25, side, n=5)
        w.piston("External leg steering cylinder", (-.36, -.12, -.66), (-.38, -.12, .41), side, .061)
        w.rod("Chassis side pipe", (.31, -.10, -.86), (.31, -.10, .83), .024, "steel", side)
        for z in [-.62, .62]:
            w.box("Pipe mounting saddle", (.31, -.10, z), (.10, .11, .075),
                  "joint", side, .009)
        hatch(w, "Upper chassis transition plate", (sx*.38, -.71, -.34), .28, .37, parent)
    rear = w.group("Rear leg brake manifold", (0, .91, -1.60), parent, (0, 0, math.pi))
    for sx in [-1, 1]:
        w.cyl("Air brake reservoir", (sx*.40, .02, -.46), .125, .48, "steel", rear)
        w.hose("Brake reservoir line", [(sx*.40, -.13, -.47), (sx*.39, -.15, -.02),
               (sx*.12, -.16, .15)], .026, "recess", rear)
    hatch(w, "Rear drivetrain inspection door", (0, -.04, .55), .50, .41, rear)


def cab(w, parent):
    for sx in [-1, 1]:
        side = w.group("Cab door side", (sx*.78, -.53, .61), parent,
                       (0, 0, sx*math.pi/2))
        armor(w, "Cab side door seam", [(-.48, -.46), (.42, -.43), (.43, .28),
              (.28, .50), (-.28, .47)], -.025, .05, side, "recess")
        armor(w, "Cab separate door", [(-.43, -.41), (.38, -.38), (.38, .26),
              (.26, .45), (-.25, .43)], -.053, .035, side)
        armor(w, "Cab side glazed opening", [(-.28, .09), (.27, .09), (.28, .28),
              (.18, .39), (-.20, .38)], -.093, .016, side, "glass")
        w.box("Cab door handle recess", (.17, -.11, -.055), (.18, .018, .07), "recess", side, .006)
        w.rod("Cab door handle", (.10, -.135, -.04), (.23, -.135, -.04), .013, "steel", side)
        for z in [-.26, -.38]:
            w.box("Cab access step", (.02, -.18, z), (.49, .27, .05), "steel", side, .009)
        w.tire("Folded cab front wheel", (sx*.86, -.05, .23), .30, .18, parent)
    for sx in [-1, 1]:
        w.rod("Windscreen lower gasket", (sx*.04, -1.287, .62), (sx*.71, -1.287, .62),
              .021, "joint", parent)
    w.rod("Cab roof lip", (-.65, -1.13, 1.09), (.65, -1.13, 1.09), .029, "edge", parent)
    for x in [-.43, 0, .43]:
        w.box("Cab roof marker housing", (x, -1.07, 1.12), (.12, .085, .055),
              "steel", parent, .009)


def back(w, parent, crane):
    for sx in [-1, 1]:
        rear = w.group("Back radiator housing", (sx*.77, .80, .22), parent, (0, 0, math.pi))
        hatch(w, "Back segmented radiator case", (0, 0, .15), .69, 1.24, rear, "joint")
        w.vent("Back stacked cooler", (0, -.06, .27), .43, .78, rear, n=12)
        w.hose("Back cooler hard line", [(sx*.30, -.08, -.39), (sx*.38, -.20, .07),
               (sx*.29, -.20, .71)], .033, "steel", rear)
    rear = w.group("Crane rear-facing shells", (0, .31, 0), crane, (0, 0, math.pi))
    armor(w, "Telescopic boom outer sleeve", [(-.30, -1.02), (.30, -1.02), (.35, 1.84),
          (-.35, 1.84)], 0, .19, rear, "armor")
    armor(w, "Telescopic sliding inner sleeve", [(-.22, -2.40), (.22, -2.40),
          (.25, -.66), (-.25, -.66)], -.035, .16, rear, "steel")
    for sx in [-1, 1]:
        w.box("Boom longitudinal guide recess", (sx*.24, -.028, .42),
              (.059, .035, 2.55), "joint", rear, .008)
        w.rod("Boom guide rail", (sx*.24, -.055, -.68), (sx*.24, -.055, 1.64),
              .018, "steel", rear)
        w.rod("Inner sleeve guide", (sx*.14, -.085, -2.21), (sx*.14, -.085, -.91),
              .023, "joint", rear)
    hatch(w, "Boom upper inspection access", (0, -.05, .98), .32, .43, rear, "steel")
    w.vent("Boom service cooling slots", (0, -.11, .99), .18, .22, rear, n=5)
    for z in [-.88, .26, 1.48]:
        w.box("Telescopic sleeve collar", (0, -.055, z), (.78, .16, .16), "joint", rear, .016)
        for sx in [-1, 1]:
            w.bolt((sx*.29, -.15, z), rear, .032)
    w.cyl("Crane cable winch", (0, .12, 1.65), .24, 1.05, "joint", crane, (1, 0, 0), 40)
    for x in [-.48, .48]:
        w.cyl("Winch cheek plate", (x, .12, 1.65), .32, .075, "steel", crane, (1, 0, 0), 40)
    for i in range(14):
        w.ring("Winch wound cable", (-.34+i*.052, .12, 1.65), .25, .020,
               "steel", crane, (1, 0, 0))
    w.piston("Crane telescoping cylinder", (-.67, .08, -1.91), (-.67, .08, .96), crane, .073)
    w.hose("Crane supply loop", [(.65, .09, -1.32), (.77, .08, -.34),
           (.63, .09, 1.08)], .041, "recess", crane)


def rubble(w, parent):
    for k, (x, y, r, height) in enumerate([
        (-3.0, -.72, .43, .38), (-2.78, -1.86, .42, .29), (-.55, -2.35, .39, .33),
        (.16, 1.76, .52, .31), (2.86, 1.12, .44, .39), (-2.66, 1.31, .38, .26),
    ]):
        n = 7
        outline = [(x+r*(1+.15*math.sin(i*4+k))*math.cos(i*math.tau/n+k),
                    y+r*(1+.12*math.cos(i*3))*math.sin(i*math.tau/n+k)) for i in range(n)]
        vertices = [(a, b, .01) for a, b in outline]
        vertices += [(x+(a-x)*.64, y+(b-y)*.64, height*(.78+.22*math.sin(i*2+k)))
                     for i, (a, b) in enumerate(outline)]
        faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
        faces += [(i, (i+1) % n, (i+1) % n+n, i+n) for i in range(n)]
        w.mesh("Angular fractured concrete", vertices, faces, "concrete", parent, .012)
    for x in [-1.15, -.45, .31]:
        w.hose("Bent exposed foundation rebar", [(x, -2.50, -.18), (x+.15, -2.73, -.06),
               (x+.33, -2.75, .16)], .028, "steel", parent)
    debris = w.group("Damaged industrial panel", (-.62, 1.12, .11), parent, (.14, -.09, .27))
    hatch(w, "Discarded hatch", (0, 0, 0), .59, .70, debris, "steel")
