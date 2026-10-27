#!/usr/bin/env python3
"""Clay-style multi-view render of meshes for side-by-side comparison (pyrender, EGL).

Usage: render_clay.py OUT.png LABEL1=mesh1.glb [LABEL2=mesh2.glb ...]
Each mesh -> one row of 4 views (0/90/180/270 deg around Y), light-grey matte material
on a dark studio background, similar to the reference turntable.
"""
import os, sys
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw

W = H = 640
ANGLES = [0, 90, 180, 270]
out, specs = sys.argv[1], sys.argv[2:]
r = pyrender.OffscreenRenderer(W, H)
mat = pyrender.MetallicRoughnessMaterial(baseColorFactor=[0.62, 0.61, 0.58, 1.0], metallicFactor=0.0, roughnessFactor=0.7)


def look_at(eye, target=(0, 0, 0), up=(0, 1, 0)):
    eye, target, up = (np.asarray(x, dtype=float) for x in (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f)
    s = np.cross(f, up); s /= np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.eye(4); m[:3, 0] = s; m[:3, 1] = u; m[:3, 2] = -f; m[:3, 3] = eye
    return m

rows = []
for spec in specs:
    label, path = spec.split("=", 1)
    tm = trimesh.load(path, force="mesh", process=False)
    v = tm.vertices - (tm.bounds[0] + tm.bounds[1]) / 2
    tm.vertices = v / (np.max(np.abs(v)) + 1e-9)
    tiles = []
    for a in ANGLES:
        m = tm.copy()
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(a), [0, 1, 0]))
        sc = pyrender.Scene(bg_color=[0.16, 0.16, 0.18, 1], ambient_light=[0.10, 0.10, 0.10])
        sc.add(pyrender.Mesh.from_trimesh(m, material=mat, smooth=False))
        sc.add(pyrender.PerspectiveCamera(yfov=np.pi / 5.2), pose=look_at((0, 0.3, 4.4)))
        sc.add(pyrender.DirectionalLight(intensity=2.6), pose=look_at((2.5, 3, 2.5)))
        sc.add(pyrender.DirectionalLight(intensity=0.9), pose=look_at((-3, 1, 1.5)))
        sc.add(pyrender.DirectionalLight(intensity=0.7), pose=look_at((0, 2, -3)))
        col, _ = r.render(sc)
        tiles.append(Image.fromarray(col))
    row = Image.new("RGB", (W * len(ANGLES), H + 34), (24, 24, 26))
    for i, t in enumerate(tiles):
        row.paste(t, (i * W, 34))
    ImageDraw.Draw(row).text((10, 10), f"{label}   ({len(tm.vertices):,} verts / {len(tm.faces):,} faces)", fill=(235, 235, 235))
    rows.append(row)
    print("rendered", label, len(tm.faces))

sheet = Image.new("RGB", (rows[0].width, sum(x.height for x in rows)))
y = 0
for x in rows:
    sheet.paste(x, (0, y)); y += x.height
sheet.save(out)
print("wrote", out)
