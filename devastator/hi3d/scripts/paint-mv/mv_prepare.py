#!/usr/bin/env python3
"""Step 1 of the multi-view color pass (RUN ON GPU BOX, Hi3D venv with hy3dgen.texgen).

Decimates the Hi3D mesh, UV-unwraps it once, and writes everything the later steps need, all in
Hunyuan3D-Paint's OWN camera frame so the colored views bake back without any alignment step:
  ~/mv/mesh.npz          vertices / faces / uv after xatlas (shared by every bake)
  ~/mv/clay_<az>.png     shaded clay renders at azim 0/90/180/270 (input for Qwen-Image-Edit)
  ~/mv/paint_<i>.png     Paint's own 6 multiview outputs (azim 0/90/180/270 + top/bottom) for fallback
Usage: mv_prepare.py MESH.glb COND_RGBA.png [faces=150000]
"""
import os, sys, numpy as np, torch, trimesh, pymeshlab
from PIL import Image

inp, cond_path = sys.argv[1], sys.argv[2]
faces = int(sys.argv[3]) if len(sys.argv) > 3 else 150000
O = os.path.expanduser("~/mv"); os.makedirs(O, exist_ok=True)

full = trimesh.load(inp, force="mesh", process=False)
ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(full.vertices, full.faces))
ms.meshing_remove_duplicate_vertices(); ms.meshing_remove_unreferenced_vertices()
ms.meshing_decimation_quadric_edge_collapse(targetfacenum=faces, preservenormal=True, qualitythr=0.5)
m = ms.current_mesh()
mesh = trimesh.Trimesh(m.vertex_matrix(), m.face_matrix(), process=True)
print(f"decimated faces {len(mesh.faces):,}", flush=True)

from hy3dgen.texgen import Hunyuan3DPaintPipeline
from hy3dgen.texgen.utils.uv_warp_utils import mesh_uv_wrap
pipe = Hunyuan3DPaintPipeline.from_pretrained("tencent/Hunyuan3D-2")
cfg = pipe.config

mesh = mesh_uv_wrap(mesh)
np.savez(f"{O}/mesh.npz", v=mesh.vertices, f=mesh.faces, uv=mesh.visual.uv)
pipe.render.load_mesh(mesh)

# shaded clay renders in Paint's camera (camera-space normals -> two-light Lambert)
for az in (0, 90, 180, 270):
    n = np.array(pipe.render.render_normal(0, az, use_abs_coor=False, resolution=1024, return_type='np'))
    bg = np.all(n > 0.995, axis=-1)
    nv = n * 2 - 1
    L1 = np.array([0.35, 0.55, 0.75]); L1 /= np.linalg.norm(L1)
    L2 = np.array([-0.6, 0.1, 0.5]); L2 /= np.linalg.norm(L2)
    sh = 0.22 + 0.62 * np.clip(np.abs(nv @ L1), 0, 1) + 0.18 * np.clip(np.abs(nv @ L2), 0, 1)
    img = np.clip(np.stack([sh * 0.80, sh * 0.80, sh * 0.78], -1), 0, 1)
    img[bg] = 1.0
    Image.fromarray((img * 255).astype(np.uint8)).save(f"{O}/clay_{az}.png")
print("clay views ok", flush=True)

# Paint's own multiview (same as the v1 run) for the top/bottom views and for an A/B bake
cond = pipe.recenter_image(Image.open(cond_path))
cond = pipe.models['delight_model'](cond)
elevs, azims = cfg.candidate_camera_elevs, cfg.candidate_camera_azims
normal_maps = pipe.render_normal_multiview(elevs, azims, use_abs_coor=True)
position_maps = pipe.render_position_multiview(elevs, azims)
camera_info = [(((a // 30) + 9) % 12) // {-20: 1, 0: 1, 20: 1, -90: 3, 90: 3}[e] + {-20: 0, 0: 12, 20: 24, -90: 36, 90: 40}[e]
               for a, e in zip(azims, elevs)]
views = pipe.models['multiview_model']([cond], normal_maps + position_maps, camera_info)
for i, v in enumerate(views):
    v.save(f"{O}/paint_{i}.png")
print(f"paint multiview ok, peak VRAM {torch.cuda.max_memory_allocated()/2**30:.1f}GB")
print("PREPARE_DONE", flush=True)
