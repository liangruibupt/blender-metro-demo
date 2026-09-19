"""Encode checked frames and validate every decoded video frame with FFmpeg."""
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT/"assets/devastator-v2.json"
metadata = json.loads(manifest_path.read_text())
render = json.loads((ROOT/"qa/turntable-render.json").read_text())
assert render["complete"]
settings = render["settings"]
assert settings == metadata["turntableSettings"], "Video settings differ from the saved build"
assert render["frames"] == list(range(1, settings["frames"]+1))
for path, digest in render["inputs"].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
assert hashlib.sha256((ROOT/"scripts/render_turntable.py").read_bytes()).hexdigest() == render["rendererScriptSHA256"]
frames_dir = Path(render["outputDirectory"])
for frame in render["frames"]:
    path = frames_dir/f"frame-{frame:04d}.png"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == render["frameSHA256"][str(frame)], path
video = ROOT/"deliverables/devastator-v2-360.mp4"
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-framerate", str(settings["fps"]), "-start_number", "1",
    "-i", str(frames_dir/"frame-%04d.png"), "-frames:v", str(settings["frames"]),
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", "-an", str(video)], check=True)
probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames",
    "-show_streams", "-show_format", "-of", "json", str(video)]))
assert len(probe["streams"]) == 1, "Unexpected audio or additional stream"
stream = probe["streams"][0]
assert stream["codec_name"] == "h264"
assert (stream["width"], stream["height"]) == (settings["width"], settings["height"])
assert int(stream["nb_read_frames"]) == settings["frames"]
assert stream["avg_frame_rate"] == f'{settings["fps"]}/1'
assert abs(float(probe["format"]["duration"])-settings["seconds"]) < .05
pixels = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(video),
    "-vf", "scale=160:90,format=gray", "-f", "rawvideo", "-pix_fmt", "gray", "-"])
size = 160*90
assert len(pixels) == size*settings["frames"], "Incomplete decoded video"
frames = [pixels[i:i+size] for i in range(0, len(pixels), size)]
deviations = [statistics.pstdev(frame) for frame in frames]
assert min(deviations) > 10, "Blank or near-uniform rendered frame"


def difference(a, b):
    return sum(abs(x-y) for x, y in zip(a, b))/len(a)


transitions = [difference(a, b) for a, b in zip(frames, frames[1:])]
assert all(value > .02 for value in transitions), "Frozen or repeated frames"
loop_difference = difference(frames[-1], frames[0])
assert loop_difference < max(max(transitions)*2.5, 1), "Abrupt loop boundary"
relative_video = str(video.relative_to(ROOT))
video_hash = hashlib.sha256(video.read_bytes()).hexdigest()
metadata["files"][relative_video] = video_hash
metadata["renderedTurntable"] = True
manifest_path.write_text(json.dumps(metadata, indent=2)+"\n")
report = {
    "status": "PASS", "video": relative_video, "sha256": video_hash,
    "settings": settings, "sourceInputs": render["inputs"], "renderSignature": render["signature"],
    "decodedFrames": len(frames), "movingTransitions": len(transitions),
    "minimumGrayscaleStdDev": min(deviations),
    "maximumAdjacentFrameDifference": max(transitions), "loopFrameDifference": loop_difference,
    "limits": ["Pixel tests do not replace visual inspection or certify reference likeness"],
}
(ROOT/"qa/video-audit.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2))
