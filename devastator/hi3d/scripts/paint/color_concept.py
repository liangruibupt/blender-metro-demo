#!/usr/bin/env python3
"""Make a COLORED concept image of the Devastator from the grey reference frame (RUN ON GPU BOX, ~/.venv).

The references are grey clay, so Hunyuan3D-Paint conditioned on them would paint grey. Qwen-Image-Edit-2511
recolors the front turntable frame (frame_00, the same view the mesh was refined against) while keeping
the pose/silhouette, giving Paint a color reference that lines up with the mesh.

Usage: color_concept.py IN_RGBA.png OUT_DIR [seeds=0,1,2]
"""
import os, sys, time, torch
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
seeds = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "0,1,2").split(",")]
os.makedirs(out, exist_ok=True)

PROMPT = (
    "Repaint this robot in the classic Generation 1 Transformers Devastator color scheme: bright lime-green "
    "armor plates and panels, purple / violet accents on the chest, shoulders, and joints, dark gunmetal grey "
    "mechanical parts, silver metallic pistons and cannon barrels, small red eyes and amber lights. "
    "Painted metal with slight wear. Keep exactly the same pose, silhouette, camera angle, proportions and "
    "every mechanical part unchanged; only change the colors and materials. Plain pure white background."
)

rgba = Image.open(src).convert("RGBA")
img = Image.new("RGB", rgba.size, (255, 255, 255)); img.paste(rgba, (0, 0), rgba)
img.save(f"{out}/input_white.png")

from diffusers import QwenImageEditPlusPipeline
t = time.time()
pipe = QwenImageEditPlusPipeline.from_pretrained("Qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()  # 20B transformer (~41 GB bf16) fits the 48 GB L40S on its own
print(f"loaded in {time.time()-t:.0f}s", flush=True)


def run(s):
    g = torch.Generator(device="cuda").manual_seed(s)
    return pipe(image=[img], prompt=PROMPT, negative_prompt=" ", true_cfg_scale=4.0, guidance_scale=1.0,
                num_inference_steps=40, generator=g, num_images_per_prompt=1).images[0]


for s in seeds:
    t = time.time()
    try:
        im = run(s)
    except torch.OutOfMemoryError:
        print("OOM with model offload -> sequential offload", flush=True)
        pipe.remove_all_hooks(); torch.cuda.empty_cache(); pipe.enable_sequential_cpu_offload()
        im = run(s)
    im.save(f"{out}/concept_s{s}.png")
    print(f"concept_s{s} {im.size} {time.time()-t:.0f}s peakVRAM {torch.cuda.max_memory_allocated()/2**30:.1f}GB", flush=True)
print("CONCEPT_DONE")
