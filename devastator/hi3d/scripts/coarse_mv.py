#!/usr/bin/env python3
"""Coarse mesh from multiple turntable views with Hunyuan3D-2mv.

Usage: coarse_mv.py OUT.glb front.png left.png back.png right.png [seed]
Images must already be RGBA cut-outs (prepared by prep_inputs.py).
"""
import sys, time, torch
from PIL import Image
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

out, f, l, b, r = sys.argv[1:6]
seed = int(sys.argv[6]) if len(sys.argv) > 6 else 0
imgs = {k: Image.open(p).convert("RGBA") for k, p in
        {"front": f, "left": l, "back": b, "right": r}.items()}
pipe = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
    "tencent/Hunyuan3D-2mv", subfolder="hunyuan3d-dit-v2-mv", variant="fp16")
t = time.time()
mesh = pipe(image=imgs, num_inference_steps=50, octree_resolution=380,
            num_chunks=20000, generator=torch.manual_seed(seed), output_type="trimesh")[0]
print(f"mv coarse {time.time()-t:.1f}s verts={len(mesh.vertices)} faces={len(mesh.faces)}")
mesh.export(out)
print("wrote", out)
