#!/usr/bin/env python3
"""Step 2 (RUN ON GPU BOX, ~/.venv with diffusers>=0.41): color each clay view with Qwen-Image-Edit-2511.

Two input images per call: image 1 = clay render of the mesh from Paint's camera (front/left/back/right),
image 2 = the front colored concept (concept_s0). The model repaints image 1 using image 2's scheme while keeping
image 1's geometry, so every side now has a real colored reference instead of being guessed by Paint.
Writes ~/mv/color_<az>.png (1024x1024). Usage: mv_edit.py CONCEPT.png [seed=0]
"""
import os, sys, time, torch
from PIL import Image

concept = Image.open(sys.argv[1]).convert("RGB")
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
O = os.path.expanduser("~/mv")
SIDE = {0: "front", 90: "side", 180: "back", 270: "other side"}

from diffusers import QwenImageEditPlusPipeline
t = time.time()
pipe = QwenImageEditPlusPipeline.from_pretrained("Qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()
print(f"loaded {time.time()-t:.0f}s", flush=True)

for az in [int(a) for a in (sys.argv[3] if len(sys.argv) > 3 else "180,90,270,0").split(",")]:
    clay = Image.open(f"{O}/clay_{az}.png").convert("RGB")
    # Single-image edit: with [clay, concept] the model copied the concept's FRONT pose onto the back view
    # (tested 2026-10-28), so the scheme is given in words only and the clay view is the sole image.
    prompt = (
        f"Repaint this grey clay robot (seen from the {SIDE[az]}) in the classic Generation 1 Transformers Devastator "
        "color scheme: bright lime-green armor plates and panels, purple / violet accents on the torso, shoulders, inner "
        "joints and hips, dark gunmetal grey mechanical parts, silver metallic pistons and cannon barrels, small red and "
        "amber lights. Painted metal with slight wear. Keep exactly the same pose, silhouette, camera angle, proportions "
        "and every mechanical part unchanged; only change the colors and materials. Rock base in natural grey stone. "
        "Plain pure white background, even studio lighting."
    )
    t = time.time()
    g = torch.Generator(device="cuda").manual_seed(seed)
    im = pipe(image=[clay], prompt=prompt, negative_prompt=" ", true_cfg_scale=4.0,
              num_inference_steps=40, generator=g, height=1024, width=1024).images[0]
    im.save(f"{O}/color_{az}.png")
    print(f"color_{az} {im.size} {time.time()-t:.0f}s peak {torch.cuda.max_memory_allocated()/2**30:.1f}GB", flush=True)
print("EDIT_DONE", flush=True)
