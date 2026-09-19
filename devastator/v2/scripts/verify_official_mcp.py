"""Exercise the real official MCP/stdio server against a disposable V2 scene copy."""
import argparse
import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

parser = argparse.ArgumentParser()
parser.add_argument("--project", type=Path, required=True, help="V2 directory containing assets and deliverables")
parser.add_argument("--blend-copy", type=Path, required=True, help="Already-open disposable copy")
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--server", default="/Users/ruiliang/Documents/workspaces/venv/bin/blender-mcp")
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
original = args.project/"deliverables/devastator-v2-assembly.blend"
manifest = json.loads((args.project/"assets/devastator-v2-assembly.json").read_text())
hash_file = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
original_hash = hash_file(original)
assert original_hash == manifest["files"]["deliverables/devastator-v2-assembly.blend"]
assert args.blend_copy.resolve() != original.resolve(), "Never test against the production scene"
assert hash_file(args.blend_copy) == original_hash
calls = []
state_code = """
import bpy, os
s = bpy.context.scene
result = {"file": bpy.data.filepath, "pid": os.getpid(), "frame": s.frame_current,
          "subframe": s.frame_subframe, "resolution": [s.render.resolution_x, s.render.resolution_y],
          "percentage": s.render.resolution_percentage, "samples": s.eevee.taa_render_samples,
          "filepath": s.render.filepath}
"""


async def main():
    params = StdioServerParameters(
        command=args.server, args=["--transport", "stdio"],
        env={"BLENDER_MCP_HOST": "127.0.0.1", "BLENDER_MCP_PORT": "9876",
             "BLENDER_PATH": "/Applications/Blender.app/Contents/MacOS/Blender"})
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=180)) as session:
            initialized = await session.initialize()
            catalog = await session.list_tools()
            (args.output/"official-mcp-tools.json").write_text(
                catalog.model_dump_json(indent=2)+"\n")
            tool_names = {tool.name for tool in catalog.tools}
            required = {"execute_blender_code", "get_blendfile_summary_datablocks",
                        "get_blendfile_summary_missing_files", "render_viewport_to_path"}
            assert required <= tool_names, required-tool_names

            async def call(name, arguments=None):
                start = time.monotonic()
                response = await session.call_tool(name, arguments or {})
                assert not response.isError, response.model_dump()
                payload = response.structuredContent
                if payload is None:
                    payload = json.loads(next(item.text for item in response.content if item.type == "text"))
                assert payload["status"] == "ok", payload
                value = payload["result"]
                if isinstance(value, dict):
                    assert value.get("status", "ok") == "ok", value
                calls.append({"tool": name, "seconds": round(time.monotonic()-start, 3)})
                print(json.dumps({"tool": name, "status": "PASS", "seconds": calls[-1]["seconds"]}), flush=True)
                return value

            before = await call("execute_blender_code", {"code": state_code})
            assert Path(before["file"]).resolve() == args.blend_copy.resolve(), before
            summary = await call("get_blendfile_summary_datablocks")
            missing = await call("get_blendfile_summary_missing_files")
            assert not missing["missing_files"], missing
            code = Path(__file__).with_name("mcp_scene_metrics.py").read_text()
            metrics = await call("execute_blender_code", {"code": code})
            assert metrics["meshCount"] == manifest["animatedMeshes"] == 81
            assert metrics["triangleCount"] == manifest["triangles"] == 610432
            assert metrics["motionControls"] == len(manifest["controls"]) == 14
            assert metrics["frameCount"] == manifest["settings"]["frames"] == 432
            assert metrics["fps"] == 24 and metrics["resolution"] == [1920, 1080]
            assert metrics["renderEngine"] == "BLENDER_EEVEE" and metrics["renderSamples"] == 64
            assert metrics["rayTracing"] and metrics["fastGI"]
            assert not metrics["framingFailures"] and not metrics["missingMaterials"]
            assert metrics["finiteTransforms"] and metrics["maximumScaleError"] < .00001
            assert metrics["minimumMovingBoundingZ"] > -.01
            assert metrics["maximumFinalVertexError"] < .0001
            assert metrics["restoredFrame"] == before["frame"]
            assert metrics["restoredSubframe"] == before["subframe"]
            try:
                await call("execute_blender_code", {"code":
                    "import bpy\nbpy.context.scene.frame_set(432)\nresult={'frame':bpy.context.scene.frame_current}"})
                rendered = await call("render_viewport_to_path",
                                      {"output_path": "devastator-v2-official-mcp.png"})
                preview = args.output/"official-mcp-preview.png"
                shutil.copy2(rendered["filepath"], preview)
            finally:
                await call("execute_blender_code", {"code":
                    f"import bpy\nbpy.context.scene.frame_set({before['frame']}, subframe={before['subframe']!r})\n"
                    "result={'frame':bpy.context.scene.frame_current}"})
            after = await call("execute_blender_code", {"code": state_code})
            assert after == before, {"before": before, "after": after}
            assert hash_file(original) == original_hash
            assert hash_file(args.blend_copy) == original_hash
            report = {
                "status": "PASS", "testedAtUTC": datetime.now(timezone.utc).isoformat(),
                "transport": "MCP over stdio -> official TCP bridge -> live Blender",
                "sourceRepository": "https://projects.blender.org/lab/blender_mcp",
                "sourceCommit": "2cea8d566dde07fbac28a61d698909d69724e853",
                "officialPackageVersion": importlib.metadata.version("blender-mcp"),
                "mcpSDKVersion": importlib.metadata.version("mcp"),
                "serverCommand": args.server, "serverInfo": initialized.serverInfo.model_dump(),
                "availableTools": len(catalog.tools), "calls": calls,
                "originalSHA256": original_hash, "originalUnchanged": True,
                "copyUnchangedOnDisk": True, "sceneStateRestored": True,
                "dataBlocks": summary, "missingFiles": missing, "metrics": metrics,
                "previewSHA256": hash_file(preview),
                "payloadSHA256": hashlib.sha256(code.encode()).hexdigest(),
                "verifierSHA256": hash_file(Path(__file__)),
                "limits": ["MCP connectivity and selected geometry checks, not an exhaustive collision test",
                           "Disposable scene copy is not an operating-system security sandbox",
                           "Native Codex tool discovery still requires a refreshed session"],
            }
            (args.output/"official-mcp-verification.json").write_text(json.dumps(report, indent=2)+"\n")
            print(json.dumps({"status": "PASS", "tools": len(catalog.tools),
                              "triangles": metrics["triangleCount"], "frames": metrics["frameCount"],
                              "output": str(args.output)}, indent=2))


asyncio.run(main())
