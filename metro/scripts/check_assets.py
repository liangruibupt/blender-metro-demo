"""Validate exported GLB structure using only Python's standard library."""

import json
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[1]
asset = root / "assets/metro.glb"
data = asset.read_bytes()
magic, version, length = struct.unpack_from("<4sII", data)
assert magic == b"glTF" and version == 2, "Expected glTF 2.0"
assert length == len(data), "Truncated GLB"
json_length, json_type = struct.unpack_from("<II", data, 12)
assert json_type == 0x4E4F534A, "Missing JSON chunk"
document = json.loads(data[20:20+json_length])
nodes = document["nodes"]
doors = [node for node in nodes if "slide" in node.get("extras", {})]
roof = [node for node in nodes if node.get("extras", {}).get("zone") == "04_Roof"]
assert len(doors) == 12, f"Expected 12 sliding leaves, found {len(doors)}"
assert len(roof) > 100, "Roof and ceiling must be independently addressable"
for name in ["Windshield_Glass", "Driver_console_top", "Driver_seat_cushion", "Main chassis"]:
    assert any(node.get("name") == name for node in nodes), f"Missing {name}"
blend = root / "deliverables/metro-atelier.blend"
assert blend.is_file() and blend.stat().st_size > 10000, "Missing Blender original"
for name in ["exterior", "interior", "cab"]:
    image = root / f"deliverables/{name}.png"
    assert image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), f"Missing {name} render"
station_data = (root / "assets/station.glb").read_bytes()
station_magic, station_version, station_length = struct.unpack_from("<4sII", station_data)
assert station_magic == b"glTF" and station_version == 2
assert station_length == len(station_data), "Truncated station GLB"
station_json_length = struct.unpack_from("<I", station_data, 12)[0]
station = json.loads(station_data[20:20+station_json_length])
station_nodes = station["nodes"]
station_cover = [n for n in station_nodes if n.get("extras", {}).get("zone") == "10_Station_Cover"]
assert len(station_cover) > 700, "Missing vaulted ceiling or removable facade"
assert sum(n.get("name", "").split(".")[0] == "Station_column" for n in station_nodes) == 5
for name in ["Platform_structure", "Departure_board", "Information_monolith", "Exit_stair"]:
    assert any(n.get("name") == name for n in station_nodes), f"Missing station object: {name}"
assert (root / "deliverables/central-station.blend").stat().st_size > 10000
for name in ["station-platform", "station-overview"]:
    assert (root / f"deliverables/{name}.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
print(json.dumps({
    "result": "PASS",
    "nodes": len(nodes),
    "meshes": len(document["meshes"]),
    "door_leaves": len(doors),
    "roof_objects": len(roof),
    "glb_bytes": len(data),
    "blend_bytes": blend.stat().st_size,
    "station_nodes": len(station_nodes),
    "station_cover_objects": len(station_cover),
    "station_glb_bytes": len(station_data),
}, indent=2))
