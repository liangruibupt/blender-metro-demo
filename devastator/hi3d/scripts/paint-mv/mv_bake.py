#!/usr/bin/env python3
"""Step 3 (RUN ON GPU BOX, Hi3D venv): bake the 4 Qwen-colored views (+ Paint's top/bottom) into one UV texture.

Uses the exact mesh + UVs saved by mv_prepare.py and Hunyuan3D-Paint's own MeshRender back-projection, so the
colored views land on the same camera frame they were rendered from. Before baking, each edited view is checked
against the rendered silhouette (IoU printed) and any background-white pixels that fall inside the mesh silhouette
(slight edge drift from the edit model) are filled from their neighbours, so no white seams get baked in.
Writes ~/mv/painted_mv.glb and ~/mv/albedo_mv.png.
"""
import os, numpy as np, cv2, torch, trimesh
from PIL import Image
from hy3dgen.texgen.differentiable_renderer.mesh_render import MeshRender

O = os.path.expanduser("~/mv"); R = 2048
d = np.load(f"{O}/mesh.npz")
mesh = trimesh.Trimesh(d["v"], d["f"], process=False)
mesh.visual = trimesh.visual.TextureVisuals(uv=d["uv"])
rend = MeshRender(default_resolution=R, texture_size=R)
rend.load_mesh(mesh)

views, elevs, azims, weights = [], [], [], []
for az, w in [(0, 1.0), (90, 0.6), (180, 0.8), (270, 0.6)]:
    im = np.array(Image.open(f"{O}/color_{az}.png").convert("RGB").resize((R, R), Image.LANCZOS))
    n = np.array(rend.render_normal(0, az, use_abs_coor=False, resolution=R, return_type='np'))
    sil = ~np.all(n > 0.995, axis=-1)
    # The edit model re-frames the subject (scale / offset drift), so map the edited foreground bbox onto the
    # mesh-silhouette bbox (independent x/y scale + shift) before measuring overlap and baking.
    def fg_mask(a):
        return ~np.all(a > 238, axis=-1)
    def bbox(mk):
        ys, xs = np.where(mk); return xs.min(), ys.min(), xs.max(), ys.max()
    ex0, ey0, ex1, ey1 = bbox(fg_mask(im)); sx0, sy0, sx1, sy1 = bbox(sil)
    iou0 = (sil & fg_mask(im)).sum() / max((sil | fg_mask(im)).sum(), 1)
    A = np.float32([[(sx1 - sx0) / max(ex1 - ex0, 1), 0, 0], [0, (sy1 - sy0) / max(ey1 - ey0, 1), 0]])
    A[0, 2] = sx0 - A[0, 0] * ex0; A[1, 2] = sy0 - A[1, 1] * ey0
    im = cv2.warpAffine(im, A, (R, R), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))
    edit_fg = fg_mask(im)
    iou = (sil & edit_fg).sum() / max((sil | edit_fg).sum(), 1)
    hole = (sil & ~edit_fg).astype(np.uint8) * 255
    im = cv2.inpaint(im, hole, 5, cv2.INPAINT_TELEA)
    print(f"azim {az}: silhouette IoU {iou0:.3f} -> {iou:.3f} after bbox align "
          f"(scale x{A[0,0]:.2f} y{A[1,1]:.2f}), filled {int(hole.sum()/255):,} px", flush=True)
    Image.fromarray(im).save(f"{O}/bakein_{az}.png")
    views.append(Image.fromarray(im)); elevs.append(0); azims.append(az); weights.append(w)
for i, e in [(4, 90), (5, -90)]:  # Paint's own top / bottom views
    views.append(Image.open(f"{O}/paint_{i}.png").convert("RGB").resize((R, R))); elevs.append(e); azims.append(0 if i == 4 else 180); weights.append(0.05)

texs, coss = [], []
for v, e, a, w in zip(views, elevs, azims, weights):
    t, c, _ = rend.back_project(v, e, a)
    texs.append(t); coss.append(w * (c ** 4))
tex, trust = rend.fast_bake_texture(texs, coss)
mask = ((trust > 1e-8).squeeze(-1).cpu().numpy() * 255).astype(np.uint8)
print(f"texels covered {mask.mean()/255:.1%}", flush=True)
tex = torch.tensor(rend.uv_inpaint(tex, mask) / 255).float().to(tex.device)
rend.set_texture(tex)
out = rend.save_mesh()
out.export(f"{O}/painted_mv.glb")
out.visual.material.image.save(f"{O}/albedo_mv.png")
print("BAKE_DONE", flush=True)
