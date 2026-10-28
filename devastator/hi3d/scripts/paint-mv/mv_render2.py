#!/usr/bin/env python3
"""Step 4 (RUN ON GPU BOX, Hi3D venv; pyrender EGL): renders for the multi-view color pass.

~/final_mv/:
  mv_inputs.jpg      clay views (Paint camera) -> Qwen-colored views, front/side/back/side
  v1_vs_v2.jpg       same 4 angles: v1 (front concept only) vs v2 (4 colored views)
  turntable_mv.mp4   12 s 360 deg turntable of v2 (1280x720, 24 fps)
"""
import os
os.environ["PYOPENGL_PLATFORM"] = "egl"
import numpy as np, trimesh, pyrender, imageio.v2 as imageio
from PIL import Image, ImageDraw

H = os.path.expanduser("~"); M = f"{H}/mv"; F = f"{H}/final_mv2"; os.makedirs(F, exist_ok=True)


def look_at(eye, target=(0, 0, 0), up=(0, 1, 0)):
    eye, target, up = (np.asarray(x, dtype=float) for x in (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f); s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    m = np.eye(4); m[:3, 0] = s; m[:3, 1] = u; m[:3, 2] = -f; m[:3, 3] = eye
    return m


def load(p):
    tm = trimesh.load(p, force="mesh", process=False)
    c = (tm.bounds[0] + tm.bounds[1]) / 2; tm.apply_translation(-c); tm.apply_scale(1 / (np.max(np.abs(tm.vertices)) + 1e-9))
    return tm


def render(tm, angle, r, eye=(0, 0.3, 4.4), fov=np.pi / 5.2):
    m = tm.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(angle), [0, 1, 0]))
    sc = pyrender.Scene(bg_color=[0.16, 0.16, 0.18, 1], ambient_light=[0.35] * 3)
    sc.add(pyrender.Mesh.from_trimesh(m, smooth=False))
    sc.add(pyrender.PerspectiveCamera(yfov=fov), pose=look_at(eye))
    for e, i in [((2.5, 3, 2.5), 2.6), ((-3, 1, 1.5), 1.2), ((0, 2, -3), 1.0)]:
        sc.add(pyrender.DirectionalLight(intensity=i), pose=look_at(e))
    return Image.fromarray(r.render(sc)[0])


def label(im, text):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, im.width, 26), fill=(20, 20, 22)); d.text((8, 7), text, fill=(235, 235, 235)); return im


T = 480
names = {0: "front", 90: "side", 180: "back", 270: "other side"}
sheet = Image.new("RGB", (T * 4, T * 2), (24, 24, 26))
for i, az in enumerate((0, 90, 180, 270)):
    sheet.paste(label(Image.open(f"{M}/clay_{az}.png").convert("RGB").resize((T, T)), f"clay {names[az]} (Paint camera)"), (i * T, 0))
    sheet.paste(label(Image.open(f"{M}/color_{az}.png").convert("RGB").resize((T, T)), f"Qwen-Image-Edit colored {names[az]}"), (i * T, T))
sheet.save(f"{F}/mv_inputs.jpg", quality=85); print("mv_inputs ok")

r = pyrender.OffscreenRenderer(T, T)
v1 = load(f"{H}/painted/mvB1536_150000.glb"); v2 = load(f"{M}/painted_mv2.glb")
s2 = Image.new("RGB", (T * 4, T * 2))
for i, a in enumerate((0, 90, 180, 270)):
    s2.paste(label(render(v1, a, r), f"v1 front concept only, {a} deg"), (i * T, 0))
    s2.paste(label(render(v2, a, r), f"v2 four colored views, {a} deg"), (i * T, T))
s2.save(f"{F}/v1_vs_v2.jpg", quality=85); print("v1_vs_v2 ok")

vr = pyrender.OffscreenRenderer(1280, 720)
w = imageio.get_writer(f"{F}/turntable_mv.mp4", fps=24, codec="libx264", quality=7, pixelformat="yuv420p", macro_block_size=8)
for k in range(288):
    w.append_data(np.array(render(v2, k * 360 / 288, vr, eye=(0, 0.3, 4.0), fov=np.pi / 6.5)))
w.close(); print("turntable ok")
print("RENDER_DONE")
