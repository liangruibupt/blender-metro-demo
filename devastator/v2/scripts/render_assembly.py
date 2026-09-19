"""Render the saved assembly scene at the same quality as the V2 turntable."""
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
parser.add_argument("--frames", type=int, nargs="+", default=[1, 73, 121, 169, 217, 265, 313, 361, 432])
parser.add_argument("--width", type=int)
parser.add_argument("--samples", type=int)
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
metadata = json.loads((ROOT/"assets/devastator-v2-assembly.json").read_text())
inputs = {path: digest for path, digest in metadata["files"].items() if not path.endswith(".mp4")}
for path, digest in {**inputs, **metadata["sourceInputs"]}.items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
settings = dict(metadata["settings"])
if args.width:
    settings["width"], settings["height"] = args.width, round(args.width*9/16)
if args.samples:
    settings["samples"] = args.samples
signature = hashlib.sha256(json.dumps({"inputs": inputs, "settings": settings},
                                     sort_keys=True).encode()).hexdigest()
output = ROOT/"work"/("assembly-"+signature[:12])
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/"deliverables/devastator-v2-assembly.blend"))
scene = bpy.context.scene
scene.render.resolution_x, scene.render.resolution_y = settings["width"], settings["height"]
scene.eevee.taa_render_samples = settings["samples"]
frames = list(range(1, settings["frames"]+1)) if args.all else args.frames
assert all(1 <= frame <= settings["frames"] for frame in frames)
report = {"signature": signature, "settings": settings, "inputs": inputs,
          "outputDirectory": str(output), "frames": frames, "complete": False, "frameSHA256": {}}
report_path = ROOT/"qa"/("assembly-render.json" if args.all else "assembly-preview.json")
print(json.dumps({"output": str(output), "frames": len(frames), "settings": settings}), flush=True)
for index, frame in enumerate(frames):
    path = output/f"frame-{frame:04d}.png"
    valid = False
    if path.exists():
        image = path.read_bytes()
        valid = (len(image) >= 36 and image[:8] == b"\x89PNG\r\n\x1a\n" and
                 struct.unpack_from(">II", image, 16) == (settings["width"], settings["height"]) and
                 image[-12:] == b"\0\0\0\0IEND\xaeB`\x82")
    start = time.monotonic()
    if not valid:
        scene.frame_set(frame)
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
    report["frameSHA256"][str(frame)] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"frame": frame, "done": index+1, "total": len(frames),
                      "seconds": round(time.monotonic()-start, 2), "resumed": valid}), flush=True)
    if (index+1) % 12 == 0:
        report_path.write_text(json.dumps(report, indent=2)+"\n")
report["complete"] = args.all
report_path.write_text(json.dumps(report, indent=2)+"\n")
