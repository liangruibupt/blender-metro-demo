#!/usr/bin/env python3
"""Renders for the painted Devastator (RUN ON GPU BOX, Hi3D venv; pyrender EGL).

Writes to ~/final_color/:
  color_views.jpg  - row 1: reference frame | colored concept (Qwen-Image-Edit); rows 2: painted mesh at 0/90/180/270
  color_vs_clay.jpg - same 4 angles: Hi3D 1536 clay vs painted 150k
  turntable_color.mp4 - 12 s 360 deg turntable of the painted mesh (1280x720, 24 fps)
"""
import os
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender, imageio.v2 as imageio
from PIL import Image, ImageDraw

H = os.path.expanduser("~"); F = f"{H}/final_color"; os.makedirs(F, exist_ok=True)
clay = pyrender.MetallicRoughnessMaterial(baseColorFactor=[0.62, 0.61, 0.58, 1], metallicFactor=0.0, roughnessFactor=0.7)


def look_at(eye, target=(0, 0, 0), up=(0, 1, 0)):
    eye, target, up = (np.asarray(x, dtype=float) for x in (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f); s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    m = np.eye(4); m[:3, 0] = s; m[:3, 1] = u; m[:3, 2] = -f; m[:3, 3] = eye
    return m


def load(p, textured):
    tm = trimesh.load(p, force="mesh", process=False)
    c = (tm.bounds[0] + tm.bounds[1]) / 2; s = np.max(np.abs(tm.vertices - c)) + 1e-9
    tm.apply_translation(-c); tm.apply_scale(1 / s)
    return tm


def render(tm, angle, r, textured, eye=(0, 0.3, 4.4), fov=np.pi / 5.2):
    m = tm.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(angle), [0, 1, 0]))
    sc = pyrender.Scene(bg_color=[0.16, 0.16, 0.18, 1], ambient_light=[0.35] * 3 if textured else [0.1] * 3)
    sc.add(pyrender.Mesh.from_trimesh(m, smooth=False) if textured else pyrender.Mesh.from_trimesh(m, material=clay, smooth=False))
    sc.add(pyrender.PerspectiveCamera(yfov=fov), pose=look_at(eye))
    for e, i in [((2.5, 3, 2.5), 2.6), ((-3, 1, 1.5), 1.2), ((0, 2, -3), 1.0)]:
        sc.add(pyrender.DirectionalLight(intensity=i), pose=look_at(e))
    return Image.fromarray(r.render(sc)[0])


def label(im, text):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, im.width, 26), fill=(20, 20, 22)); d.text((8, 7), text, fill=(235, 235, 235)); return im


T = 480; r = pyrender.OffscreenRenderer(T, T)
painted = load(f"{H}/painted/mvB1536_150000.glb", True)
cl = load(f"{H}/out/mvB_refined_1536.glb", False)
ANG = [0, 90, 180, 270]

# reference + concept row
top = Image.new("RGB", (T * 4, T), (24, 24, 26))
ref = Image.open(f"{H}/inputs/rgba_frame_00.png"); bg = Image.new("RGB", ref.size, (41, 41, 46)); bg.paste(ref, (0, 0), ref)
top.paste(label(bg.resize((T, T)), "reference frame_00 (grey)"), (0, 0))
cond = Image.open(f"{H}/painted/mvB1536_150000_cond.png").convert("RGBA"); bg2 = Image.new("RGB", cond.size, (41, 41, 46)); bg2.paste(cond, (0, 0), cond)
top.paste(label(bg2.resize((T, T)), "colored concept (Qwen-Image-Edit-2511)"), (T, 0))
alb = Image.open(f"{H}/painted/mvB1536_150000_albedo.png").convert("RGB").resize((T, T))
top.paste(label(alb, "baked albedo 2048x2048 (UV)"), (T * 2, 0))
top.paste(label(render(painted, 30, r, True, eye=(0.15, 0.55, 1.7), fov=np.pi / 5), "painted close-up"), (T * 3, 0))
row_p = Image.new("RGB", (T * 4, T)); row_c = Image.new("RGB", (T * 4, T))
for i, a in enumerate(ANG):
    row_p.paste(label(render(painted, a, r, True), f"painted {a} deg"), (i * T, 0))
    row_c.paste(label(render(cl, a, r, False), f"Hi3D 1536 clay {a} deg"), (i * T, 0))
sheet = Image.new("RGB", (T * 4, T * 2)); sheet.paste(top, (0, 0)); sheet.paste(row_p, (0, T))
sheet.save(f"{F}/color_views.jpg", quality=85); print("color_views ok")
s2 = Image.new("RGB", (T * 4, T * 2)); s2.paste(row_c, (0, 0)); s2.paste(row_p, (0, T))
s2.save(f"{F}/color_vs_clay.jpg", quality=85); print("color_vs_clay ok")

vr = pyrender.OffscreenRenderer(1280, 720)
w = imageio.get_writer(f"{F}/turntable_color.mp4", fps=24, codec="libx264", quality=7, pixelformat="yuv420p", macro_block_size=8)
for k in range(288):
    w.append_data(np.array(render(painted, k * 360 / 288, vr, True, eye=(0, 0.3, 4.0), fov=np.pi / 6.5)))
w.close(); print("turntable ok")
print("RENDER_DONE")
