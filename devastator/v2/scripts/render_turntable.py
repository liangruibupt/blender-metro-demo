"""Render a resumable full turn from the evaluated, independently checked GLB."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import time

import bpy

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--all", action="store_true")
parser.add_argument("--frames", type=int, nargs="+", default=[1, 73, 145, 217])
parser.add_argument("--engine", choices=["CYCLES", "BLENDER_EEVEE"])
parser.add_argument("--width", type=int)
parser.add_argument("--samples", type=int)
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
metadata = json.loads((ROOT/"assets/devastator-v2.json").read_text())
settings = dict(metadata["turntableSettings"])
if args.engine:
    settings["engine"] = args.engine
if args.width:
    settings["width"], settings["height"] = args.width, round(args.width*9/16)
if args.samples:
    settings["samples"] = args.samples
inputs = {}
for path in ["deliverables/devastator-v2.blend", "assets/devastator-v2.glb"]:
    digest = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    assert digest == metadata["files"][path], f"Stale input: {path}"
    inputs[path] = digest
signature = hashlib.sha256(json.dumps({"inputs": inputs, "settings": settings,
    "script": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}, sort_keys=True).encode()).hexdigest()
output = ROOT/"work"/("turntable-"+signature[:12])
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/"deliverables/devastator-v2.blend"))
scene = bpy.context.scene
scene.collection.children.unlink(bpy.data.collections[metadata["collection"]])
bpy.ops.import_scene.gltf(filepath=str(ROOT/"assets/devastator-v2.glb"))
scene.camera = bpy.data.objects[metadata["orbitCamera"]]
scene.render.engine = settings["engine"]
scene.render.resolution_x, scene.render.resolution_y = settings["width"], settings["height"]
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"
scene.render.fps = settings["fps"]
scene.render.use_persistent_data = True
if settings["engine"] == "CYCLES":
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "METAL"
    preferences.get_devices()
    for device in preferences.devices:
        device.use = device.type == "METAL"
    assert any(device.use for device in preferences.devices), "Metal GPU is required for this video preset"
    scene.cycles.device = "GPU"
    scene.cycles.samples = settings["samples"]
    scene.cycles.use_denoising = True
    scene.cycles.adaptive_threshold = .04
    scene.cycles.max_bounces = 6
else:
    scene.eevee.taa_render_samples = settings["samples"]
    scene.eevee.use_raytracing = True
    scene.eevee.use_fast_gi = True
    scene.eevee.shadow_ray_count = 2
    scene.eevee.shadow_step_count = 8

frames = list(range(1, settings["frames"]+1)) if args.all else args.frames
assert all(1 <= frame <= settings["loopFrame"] for frame in frames)
print(json.dumps({"output": str(output), "settings": settings}), flush=True)
for index, frame in enumerate(frames):
    path = output/f"frame-{frame:04d}.png"
    if path.exists():
        header = path.read_bytes()[:24]
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack_from(">II", header, 16) == (settings["width"], settings["height"])
        continue
    start = time.monotonic()
    scene.frame_set(frame)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(json.dumps({"frame": frame, "completed": index+1, "requested": len(frames),
                      "seconds": round(time.monotonic()-start, 2)}), flush=True)
report = {"signature": signature, "settings": settings, "inputs": inputs,
          "outputDirectory": str(output), "frames": frames, "complete": args.all,
          "rendererScriptSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
if args.all:
    report["frameSHA256"] = {
        str(frame): hashlib.sha256((output/f"frame-{frame:04d}.png").read_bytes()).hexdigest()
        for frame in frames}
(ROOT/"qa").mkdir(exist_ok=True)
(ROOT/"qa"/("turntable-render.json" if args.all else "turntable-preview.json")).write_text(
    json.dumps(report, indent=2)+"\n")
