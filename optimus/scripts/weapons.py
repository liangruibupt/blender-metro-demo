"""Reference-inspired display accessories with persistent folding carriers."""

import math


def build_weapons(joint, box, cylinder, prism):
    for side, tag, kind in [(-1, "left", "axe"), (1, "right", "rifle")]:
        parked_offset = 1.70 if kind == "axe" else 1.36
        carrier = joint(f"{tag}_weapon_carrier", f"{tag}_forearm",
                        (0, -1.88, .38), (side*parked_offset, -1.88, -1.60),
                        interval=(0, .08), order=7, label=f"{kind.title()} sliding mount",
                        motion={"type": "weapon_carrier", "side": side})
        box("Accessory locking carriage", (0, .25, 0), (.20, .24, .18),
            "dark", carrier, .02)
        cylinder("Accessory hinge", (0, 0, 0), .13, .22,
                 "silver", carrier, (0, 0, 1))
        weapon = joint(f"{tag}_{kind}", carrier, (0, 0, .12),
                       truck_angles=(0, 0, side*math.pi),
                       interval=(.08, .36), order=7, label=kind.title(),
                       motion={"type": "weapon_fold", "side": side})
        # The rear grip sits inside the blue hand; the body clears its fingertips.
        box(f"{kind.title()} grip", (0, 0, -.29), (.10, .10, .42),
            "dark", weapon, .018)
        if kind == "rifle":
            prism("Ion rifle receiver", [(-.22, .28), (.16, .28), (.25, .08),
                  (.20, -.91), (.12, -1.05), (-.17, -1.05), (-.25, -.80)],
                  -.13, .22, "dark", weapon, bevel=.025)
            box("Rifle rear cap", (0, .20, .04), (.34, .13, .29),
                "titanium", weapon, .02)
            cylinder("Rifle barrel", (0, -1.43, .04), .105, .86,
                     "dark", weapon, (0, 1, 0), vertices=32)
            for y in [-1.13, -1.40, -1.77]:
                cylinder("Barrel collar", (0, y, .04), .15, .11,
                         "titanium", weapon, (0, 1, 0))
            cylinder("Rifle muzzle sleeve", (0, -1.93, .04), .145, .20,
                     "dark", weapon, (0, 1, 0), vertices=32, hollow=True)
            cylinder("Recessed muzzle", (0, -1.87, .04), .108, .025,
                     "dark", weapon, (0, 1, 0))
            box("Receiver spine", (0, -.33, .26), (.12, 1.16, .07),
                "titanium", weapon, .014)
            for x in [-.255, .255]:
                cylinder("Rifle side power cell", (x, -.38, .055), .085, .65,
                         "dark", weapon, (0, 1, 0))
                for y in [-.58, -.39, -.20]:
                    box("Rifle cooling ribs", (x, y, .07), (.07, .045, .26),
                        "silver", weapon, .008)
            box("Rifle power indicator", (0, -.12, .301), (.055, .19, .015),
                "eye", weapon, .004)
        else:
            prism("Energon wrist socket", [(-.12, .03), (.12, .03), (.23, -.12),
                  (.24, -.25), (.16, -.44), (.06, -.69), (-.06, -.69),
                  (-.16, -.44), (-.24, -.25), (-.23, -.12)],
                  -.17, .17, "energy_core", weapon, bevel=.035)
            cylinder("Short energon haft", (0, -.66, 0), .068, .67,
                     "energy_core", weapon, (0, 1, 0), vertices=32)
            prism("Energon axe central core", [(-.09, -.85), (.09, -.85),
                  (.13, -1.08), (0, -1.32), (-.13, -1.08)],
                  -.12, .12, "energy_core", weapon, bevel=.015)
            # Broad hooked blades, not a long polearm: the reference's orange silhouette.
            blade = [(.06, -.71), (.24, -.75), (.40, -.75), (.54, -.71),
                     (.62, -.63), (.65, -.51), (.74, -.65), (.81, -.82),
                     (.85, -1.02), (.86, -1.22), (.80, -1.43), (.71, -1.32),
                     (.59, -1.23), (.47, -1.16), (.30, -1.10), (.06, -1.06)]
            edge = [(.65, -.51), (.74, -.65), (.81, -.82), (.85, -1.02),
                    (.86, -1.22), (.80, -1.43), (.78, -1.23), (.78, -1.03),
                    (.75, -.85), (.70, -.68)]
            for sign in [-1, 1]:
                width = 1 if sign < 0 else .65
                outline = [(sign*x*width, y) for x, y in blade]
                rim = [(sign*x*width, y) for x, y in edge]
                if sign < 0:
                    outline.reverse()
                    rim.reverse()
                prism("Amber energon blade", outline, -.09, .09,
                      "energy", weapon, bevel=.015)
                prism("Luminous axe bevel", rim, -.105, .105,
                      "energy_edge", weapon, bevel=.007)


def weapon_links():
    return [dict(id=f"{tag}_weapon_guide", base=f"{tag}_forearm",
                 target=f"{tag}_weapon_carrier",
                 start=[side*.40, -.95, .28], end=[0, .25, 0], radius=.045)
            for side, tag in [(-1, "left"), (1, "right")]]
