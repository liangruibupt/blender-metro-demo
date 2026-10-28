#!/usr/bin/env python3
"""Final comparison assets for the Devastator Hi3D experiment (run on the GPU box).

Writes to ~/final/:
  ref_vs_hi3d.jpg   - rows: reference turntable frame | Hi3D multi-view 1536 | Hi3D single-view 1536,
                      at four matching angles (0/90/180/270).
  closeups.jpg      - upper-body close-ups: coarse vs 1024 vs 1536 (multi-view).
  turntable.mp4     - 12 s 360-degree clay turntable of the multi-view 1536 mesh (1280x720, 24 fps).
  devastator-hi3d-mv1536-200k.glb - decimated (200k faces) mesh for the repo / web viewing.
"""
import os
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender, imageio.v2 as imageio
from PIL import Image, ImageDraw

H = os.path.expanduser("~"); O = f"{H}/out"; F = f"{H}/final"; os.makedirs(F, exist_ok=True)
mat = pyrender.MetallicRoughnessMaterial(baseColorFactor=[0.62, 0.61, 0.58, 1], metallicFactor=0.0, roughnessFactor=0.7)


def look_at(eye, target=(0, 0, 0), up=(0, 1, 0)):
    eye, target, up = (np.asarray(x, dtype=float) for x in (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f); s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    m = np.eye(4); m[:3, 0] = s; m[:3, 1] = u; m[:3, 2] = -f; m[:3, 3] = eye
    return m


def load(p):
    tm = trimesh.load(p, force="mesh", process=False)
    v = tm.vertices - (tm.bounds[0] + tm.bounds[1]) / 2
    tm.vertices = v / (np.max(np.abs(v)) + 1e-9)
    return tm


def render(tm, angle, r, eye=(0, 0.3, 4.4), target=(0, 0, 0), fov=np.pi / 5.2):
    m = tm.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(angle), [0, 1, 0]))
    sc = pyrender.Scene(bg_color=[0.16, 0.16, 0.18, 1], ambient_light=[0.1] * 3)
    sc.add(pyrender.Mesh.from_trimesh(m, material=mat, smooth=False))
    sc.add(pyrender.PerspectiveCamera(yfov=fov), pose=look_at(eye, target))
    for e, i in [((2.5, 3, 2.5), 2.6), ((-3, 1, 1.5), 0.9), ((0, 2, -3), 0.7)]:
        sc.add(pyrender.DirectionalLight(intensity=i), pose=look_at(e))
    return Image.fromarray(r.render(sc)[0])


def label(im, text):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, im.width, 26), fill=(20, 20, 22)); d.text((8, 7), text, fill=(235, 235, 235)); return im

T = 480; r = pyrender.OffscreenRenderer(T, T)
mv = load(f"{O}/mvB_refined_1536.glb"); sv = load(f"{O}/sv_refined_1536.glb")
# Reference turntable frames 00/06/12/18 are ~90 degrees apart (see prep_inputs.py).
# mvB used front=00, left=18, back=12, right=06; our render angles 0/90/180/270 map to those.
pairs = [("frame_00", 0), ("frame_06", 270), ("frame_12", 180), ("frame_18", 90)]
rows = []
for name, src in [("Reference turntable (video frame, bg removed)", None), ("Hi3D 1536 / multi-view coarse (4 frames)", mv), ("Hi3D 1536 / single-view coarse (rex-hsu-b-0001)", sv)]:
    row = Image.new("RGB", (T * 4, T), (24, 24, 26))
    for i, (fr, ang) in enumerate(pairs):
        if src is None:
            ref = Image.open(f"{H}/inputs/rgba_{fr}.png"); bg = Image.new("RGB", ref.size, (41, 41, 46)); bg.paste(ref, (0, 0), ref)
            tile = bg.resize((T, T))
        else:
            tile = render(src, ang, r)
        row.paste(tile, (i * T, 0))
    rows.append(label(row, name))
sheet = Image.new("RGB", (T * 4, T * len(rows)))
for i, x in enumerate(rows): sheet.paste(x, (0, i * T))
sheet.save(f"{F}/ref_vs_hi3d.jpg", quality=85); print("ref_vs_hi3d ok")

# Close-ups of the upper body: coarse vs 1024 vs 1536
cr = pyrender.OffscreenRenderer(640, 640)
tiles = []
for nm, p in [("coarse (Hunyuan3D-2mv)", "mvB_coarse.glb"), ("Hi3D 1024", "mvB_refined_1024.glb"), ("Hi3D 1536", "mvB_refined_1536.glb")]:
    tiles.append(label(render(load(f"{O}/{p}"), 20, cr, eye=(0.15, 0.55, 1.7), target=(0.05, 0.4, 0), fov=np.pi / 5), nm))
cl = Image.new("RGB", (640 * 3, 640))
for i, t in enumerate(tiles): cl.paste(t, (i * 640, 0))
cl.save(f"{F}/closeups.jpg", quality=85); print("closeups ok")

# 12 s turntable of the multi-view 1536 mesh
vr = pyrender.OffscreenRenderer(1280, 720)
w = imageio.get_writer(f"{F}/turntable.mp4", fps=24, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=8)
for k in range(288):
    w.append_data(np.array(render(mv, k * 360 / 288, vr, eye=(0, 0.3, 4.0), fov=np.pi / 6.5)))
w.close(); print("turntable ok")

# Decimated GLB for the repo (full-res outputs are 50-100 MB)
full = trimesh.load(f"{O}/mvB_refined_1536.glb", force="mesh", process=False)
print("full faces", len(full.faces))
try:
    import pymeshlab
    ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(full.vertices, full.faces))
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=200000, preservenormal=True)
    m = ms.current_mesh(); dec = trimesh.Trimesh(m.vertex_matrix(), m.face_matrix(), process=False)
except Exception as e:
    print("pymeshlab decimation failed", e); dec = full.simplify_quadric_decimation(face_count=200000)
dec.export(f"{F}/devastator-hi3d-mv1536-200k.glb"); print("decimated faces", len(dec.faces))
print("FINAL_DONE")
