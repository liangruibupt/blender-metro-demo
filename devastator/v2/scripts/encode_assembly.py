"""Encode the full assembly sequence and inspect every decoded frame."""
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
path = ROOT/"assets/devastator-v2-assembly.json"
metadata = json.loads(path.read_text())
render = json.loads((ROOT/"qa/assembly-render.json").read_text())
settings = metadata["settings"]
assert render["complete"] and render["settings"] == settings
assert render["frames"] == list(range(1, settings["frames"]+1))
for relative, digest in {**render["inputs"], **metadata["sourceInputs"]}.items():
    assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest, relative
folder = Path(render["outputDirectory"])
for frame in render["frames"]:
    image = folder/f"frame-{frame:04d}.png"
    assert hashlib.sha256(image.read_bytes()).hexdigest() == render["frameSHA256"][str(frame)]
video = ROOT/"deliverables/devastator-v2-assembly.mp4"
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-framerate", str(settings["fps"]), "-start_number", "1", "-i", str(folder/"frame-%04d.png"),
                "-frames:v", str(settings["frames"]), "-c:v", "libx264", "-crf", "18",
                "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(video)],
               check=True)
probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames",
                                           "-show_streams", "-show_format", "-of", "json", str(video)]))
assert len(probe["streams"]) == 1
stream = probe["streams"][0]
assert stream["codec_name"] == "h264"
assert (stream["width"], stream["height"]) == (settings["width"], settings["height"])
assert stream["avg_frame_rate"] == f'{settings["fps"]}/1'
assert int(stream["nb_read_frames"]) == settings["frames"]
assert abs(float(probe["format"]["duration"])-settings["seconds"]) < .05
pixels = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(video), "-vf",
                                  "scale=160:90,format=gray", "-f", "rawvideo", "-pix_fmt", "gray", "-"])
size = 160*90
assert len(pixels) == size*settings["frames"]
decoded = [pixels[i:i+size] for i in range(0, len(pixels), size)]
deviation = min(statistics.pstdev(frame) for frame in decoded)
assert deviation > 10, deviation
differences = [sum(abs(a-b) for a, b in zip(x, y))/size for x, y in zip(decoded, decoded[1:])]
assert max(differences) > .2, "Animation is static"
assert max(differences) < 10, "Large unexpected frame discontinuity"
frozen = [i+1 for i, delta in enumerate(differences) if delta < .002]
assert not any(all(j in frozen for j in range(i, i+12)) for i in frozen), "Half-second freeze"
digest = hashlib.sha256(video.read_bytes()).hexdigest()
metadata["files"][str(video.relative_to(ROOT))] = digest
metadata["rendered"] = True
path.write_text(json.dumps(metadata, indent=2)+"\n")
report = {"status": "PASS", "video": str(video.relative_to(ROOT)), "sha256": digest,
          "settings": settings, "decodedFrames": len(decoded),
          "minimumGrayscaleStdDev": deviation, "maximumAdjacentDifference": max(differences),
          "nearIdenticalTransitions": frozen, "renderSignature": render["signature"],
          "limits": ["One-way assembly, intentionally not a loop",
                     "Pixel tests do not certify mechanical plausibility or visual quality"]}
(ROOT/"qa/assembly-video-audit.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2))
