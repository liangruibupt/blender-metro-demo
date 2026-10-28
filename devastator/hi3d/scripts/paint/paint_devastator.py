#!/usr/bin/env python3
"""Paint the Hi3D Devastator mesh with Hunyuan3D-2 Paint (RUN ON GPU BOX, Hi3D venv with hy3dgen.texgen).

Hi3D output is 2M faces; Paint UV-unwraps with xatlas and bakes multi-view diffusion into one texture,
so decimate first. Conditioned on the rembg'd colored concept image.

Usage: paint_devastator.py MESH.glb CONCEPT.png OUT_PREFIX [faces=150000]
Writes OUT_PREFIX_<faces>.glb (textured) and OUT_PREFIX_<faces>_albedo.png.
"""
import sys, time, numpy as np, trimesh, pymeshlab
from PIL import Image

inp, ref, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
faces = int(sys.argv[4]) if len(sys.argv) > 4 else 150000

full = trimesh.load(inp, force="mesh", process=False)
print(f"input faces {len(full.faces):,}", flush=True)
ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(full.vertices, full.faces))
ms.meshing_remove_duplicate_vertices(); ms.meshing_remove_unreferenced_vertices()
ms.meshing_decimation_quadric_edge_collapse(targetfacenum=faces, preservenormal=True, qualitythr=0.5)
m = ms.current_mesh()
mesh = trimesh.Trimesh(m.vertex_matrix(), m.face_matrix(), process=True)
print(f"decimated faces {len(mesh.faces):,}", flush=True)

from rembg import remove
im = Image.open(ref).convert("RGB")
cond = remove(im)
cond.save(f"{prefix}_{faces}_cond.png")

from hy3dgen.texgen import Hunyuan3DPaintPipeline
t = time.time()
pipe = Hunyuan3DPaintPipeline.from_pretrained("tencent/Hunyuan3D-2")
print(f"paint pipeline loaded {time.time()-t:.0f}s", flush=True)
t = time.time()
painted = pipe(mesh, image=cond)
print(f"paint elapsed {time.time()-t:.0f}s", flush=True)
painted.export(f"{prefix}_{faces}.glb")
tex = getattr(painted.visual.material, "baseColorTexture", None) or getattr(painted.visual.material, "image", None)
if tex is not None:
    tex.save(f"{prefix}_{faces}_albedo.png"); print("albedo", tex.size)
import torch
print(f"peak VRAM {torch.cuda.max_memory_allocated()/2**30:.1f}GB")
print("PAINT_DONE", flush=True)
