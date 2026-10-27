#!/usr/bin/env python3
"""Extract evenly spaced frames from the reference turntable and prepare background-removed
inputs (RGBA, square, centered) for Hunyuan3D single-view and multi-view shape generation.

Outputs in ~/inputs/: frame_XX.png (raw), and prepared rgba_*.png.
"""
import os, cv2, numpy as np
from PIL import Image
from rembg import remove, new_session

H = os.path.expanduser("~")
OUT = f"{H}/inputs"; os.makedirs(OUT, exist_ok=True)
cap = cv2.VideoCapture(f"{H}/2-00x-3840x2160-alq-8-1.mp4")
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps = cap.get(cv2.CAP_PROP_FPS)
print("frames", n, "fps", fps)
# 24 evenly spaced samples over the turntable for picking front/left/back/right views
for k in range(24):
    idx = int(k * n / 24)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx); ok, fr = cap.read()
    if ok:
        cv2.imwrite(f"{OUT}/frame_{k:02d}.png", fr)
sess = new_session("u2net")

def prep(src, dst, size=1024, pad=0.08):
    im = Image.open(src).convert("RGB")
    rgba = remove(im, session=sess)
    a = np.array(rgba)[..., 3]
    ys, xs = np.where(a > 16)
    box = rgba.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    s = int(max(box.size) * (1 + 2 * pad))
    canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    canvas.paste(box, ((s - box.size[0]) // 2, (s - box.size[1]) // 2), box)
    canvas.resize((size, size), Image.LANCZOS).save(dst)
    print("prepared", dst, box.size)

for f in sorted(os.listdir(OUT)):
    if f.startswith("frame_"):
        prep(f"{OUT}/{f}", f"{OUT}/rgba_{f}")
for f in ["rex-hsu-b-0001.jpg", "rex-hsu-b-0002.jpg", "rex-hsu-b-0003.jpg"]:
    prep(f"{H}/{f}", f"{OUT}/rgba_{f[:-4]}.png")
print("INPUTS_DONE")
