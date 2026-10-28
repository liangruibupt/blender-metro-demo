#!/usr/bin/env python3
"""Step 3b (RUN ON GPU BOX, Hi3D venv): masked + registered bake of the Qwen-colored views.

v1 of mv_bake.py back-projected the edited views as-is; the edit model drifts the outline a few percent, so
background white and edge pixels were baked onto arms / barrels as white streaks. This version:
  1. registers each edited view to the mesh silhouette (best of identity / bbox, then ECC affine on the masks);
  2. bakes only pixels that are foreground in BOTH the edit and the silhouette, eroded ~1% inward, by
     back-projecting that mask too and multiplying it into the per-view weight;
  3. fills what the edits do not cover with Hunyuan3D-Paint's own 6 multiview images (rendered from the same
     normal/position maps, so pixel-aligned) at low weight.
Writes ~/mv/painted_mv2.glb, ~/mv/albedo_mv2.png.
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


def fg(a):
    return ~np.all(a > 238, axis=-1)


def iou(a, b):
    return (a & b).sum() / max((a | b).sum(), 1)


def warp(im, A):
    return cv2.warpAffine(im, A, (R, R), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))


texs, coss = [], []
for az, w in [(0, 1.0), (90, 0.7), (180, 0.9), (270, 0.7)]:
    im = np.array(Image.open(f"{O}/color_{az}.png").convert("RGB").resize((R, R), Image.LANCZOS))
    n = np.array(rend.render_normal(0, az, use_abs_coor=False, resolution=R, return_type='np'))
    sil = ~np.all(n > 0.995, axis=-1)
    e = fg(im)
    ys, xs = np.where(e); sy, sx = np.where(sil)
    Ab = np.float32([[np.ptp(sx) / max(np.ptp(xs), 1), 0, 0], [0, np.ptp(sy) / max(np.ptp(ys), 1), 0]])
    Ab[0, 2] = sx.min() - Ab[0, 0] * xs.min(); Ab[1, 2] = sy.min() - Ab[1, 1] * ys.min()
    I = np.float32([[1, 0, 0], [0, 1, 0]])
    cands = {"identity": I, "bbox": Ab}
    best = max(cands, key=lambda k: iou(sil, fg(warp(im, cands[k]))))
    A = cands[best].copy()
    try:  # ECC refines the affine on blurred masks (template = silhouette, input = edit)
        small = 512; s = small / R
        t = cv2.GaussianBlur(cv2.resize(sil.astype(np.float32), (small, small)), (0, 0), 3)
        i = cv2.GaussianBlur(cv2.resize(e.astype(np.float32), (small, small)), (0, 0), 3)
        W = A.copy(); W[:, 2] *= s
        # ECC maps template coords -> input coords, so start from the inverse
        Winv = cv2.invertAffineTransform(W)
        _, Winv = cv2.findTransformECC(t, i, Winv.astype(np.float32), cv2.MOTION_AFFINE,
                                       (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
        W = cv2.invertAffineTransform(Winv); W[:, 2] /= s
        if iou(sil, fg(warp(im, W))) > iou(sil, fg(warp(im, A))):
            A, best = W.astype(np.float32), best + "+ecc"
    except cv2.error as ex:
        print("ECC failed", az, str(ex)[:80])
    im = warp(im, A)
    e = fg(im)
    k = int(0.01 * R) * 2 + 1
    ok = cv2.erode((e & sil).astype(np.uint8), np.ones((k, k), np.uint8))
    print(f"azim {az}: IoU {iou(sil, fg(np.array(Image.open(f'{O}/color_{az}.png').convert('RGB').resize((R, R))))):.3f}"
          f" -> {iou(sil, e):.3f} via {best}; baked {ok.sum()/sil.sum():.0%} of silhouette", flush=True)
    Image.fromarray(im).save(f"{O}/bakein2_{az}.png")
    tex, cos, _ = rend.back_project(Image.fromarray(im), 0, az)
    mtex, _, _ = rend.back_project(torch.tensor(ok[..., None].astype(np.float32)), 0, az)
    texs.append(tex); coss.append(w * (cos ** 4) * (mtex[..., :1] > 0.5).float())

# Paint's own aligned multiview as low-weight fill: azim 0/90/180/270 at elev 0, then top / bottom
for i, (el, az, w) in enumerate([(0, 0, .04), (0, 90, .04), (0, 180, .04), (0, 270, .04), (90, 0, .05), (-90, 180, .05)]):
    v = Image.open(f"{O}/paint_{i}.png").convert("RGB").resize((R, R))
    tex, cos, _ = rend.back_project(v, el, az)
    texs.append(tex); coss.append(w * (cos ** 4))

# weighted average (fast_bake_texture skips mostly-overlapping views, which would drop the fill pass)
num = sum(t * c for t, c in zip(texs, coss)); den = sum(coss)
tex = num / torch.clamp(den, min=1e-8)
mask = ((den > 1e-8).squeeze(-1).cpu().numpy() * 255).astype(np.uint8)
print(f"texels covered {mask.mean()/255:.1%}", flush=True)
tex = torch.tensor(rend.uv_inpaint(tex, mask) / 255).float().to(tex.device)
rend.set_texture(tex)
out = rend.save_mesh()
out.export(f"{O}/painted_mv2.glb")
out.visual.material.image.save(f"{O}/albedo_mv2.png")
print("BAKE2_DONE", flush=True)
