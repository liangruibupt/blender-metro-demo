# Official Blender MCP / Verified 2026-09-15

## Installed Components

- Official project: https://projects.blender.org/lab/blender_mcp
- Official documentation: https://www.blender.org/lab/mcp-server/
- Server and add-on version: 1.0.3.
- Source commit: `2cea8d566dde07fbac28a61d698909d69724e853`.
- Source checkout: `/Users/ruiliang/.local/share/blender-official-mcp/source`.
- User-requested environment: `/Users/ruiliang/Documents/workspaces/venv`.
- Executable: `/Users/ruiliang/Documents/workspaces/venv/bin/blender-mcp`.
- Added dependencies: official `blender-mcp==1.0.3` from local verified source,
  and `docutils==0.23`. Existing `mcp==1.28.0` and `PyYAML==6.0.2` were retained.
- Installed add-on: `bl_ext.lab_blender_org.mcp`, enabled with auto-start.
- Native Blender: 5.2.1 LTS, `/Applications/Blender.app/Contents/MacOS/Blender`.

The official and third-party distributions use the same package name.
The installed server was built from the official pinned Git source, not
downloaded as `blender-mcp` from PyPI.

## Codex Connection

Global server name: `blender-official`.

```toml
[mcp_servers.blender-official]
command = "/Users/ruiliang/Documents/workspaces/venv/bin/blender-mcp"
args = ["--transport", "stdio"]

[mcp_servers.blender-official.env]
BLENDER_MCP_HOST = "127.0.0.1"
BLENDER_MCP_PORT = "9876"
BLENDER_PATH = "/Applications/Blender.app/Contents/MacOS/Blender"
```

This section was added using `codex mcp add`, preserving other servers. The
prior config was backed up to
`/Users/ruiliang/.codex/config.toml.before-blender-official-20260915`.

Start Blender with the installed add-on enabled before using live MCP tools.
The bridge was verified listening only on `127.0.0.1:9876`. A new Codex
conversation or app restart may be needed to discover the newly registered
tools. This installation session used a real MCP SDK client for its protocol
test; it did not pretend a newly added native tool was already in the session.

The `blender-official-mcp` personal skill records the user's preference for
using official MCP in subsequent native Blender projects.

## Actual MCP Verification

The test used this chain:

`MCP ClientSession -> official server over stdio -> official TCP add-on -> live Blender`

It called the real server tools, not a replacement server or a direct socket
script masquerading as MCP. The scene was an exact disposable copy of the
committed `deliverables/devastator-v2-assembly.blend`.

Results:

- 26 official tools discovered through `tools/list`.
- Scene and missing-file queries succeeded; no missing external files.
- 81 animated meshes, 610,432 triangles, 14 controls.
- 432 frames at 24 fps; 1920 x 1080, Eevee 64 samples, ray tracing and fast GI.
- All 432 frames pass the selected framing, floor and unit-scale checks.
- Final vertex error from bind geometry: approximately 0.0000016093 model units.
- A full-resolution terminal-pose PNG was rendered by `render_viewport_to_path`.
- Original and copied `.blend` hashes are unchanged on disk.
- Current frame, subframe, resolution, samples and output path were restored.

Artifacts:

- `qa/official-mcp-verification.json`: results and provenance.
- `qa/official-mcp-tools.json`: actual tool schemas returned by the server.
- `qa/official-mcp-preview.png`: MCP-generated full-resolution render.
- `scripts/mcp_scene_metrics.py`: payload executed inside Blender.
- `scripts/verify_official_mcp.py`: real MCP protocol verification client.

To repeat, first make and open a disposable scene copy in Blender. Then run:

```sh
/Users/ruiliang/Documents/workspaces/venv/bin/python3 \
  devastator/v2/scripts/verify_official_mcp.py \
  --project /Users/ruiliang/Documents/workspaces/blender-metro-demo/devastator/v2 \
  --blend-copy /private/tmp/blender-official-mcp-validation/devastator-v2-assembly-validation.blend \
  --output /private/tmp/blender-official-mcp-validation/results
```

The test refuses to operate on a different connected file and verifies that
the copy matches the accepted source hash. It leaves the scene state restored.
Its temporary files are not required to use the installed MCP server.

## Security and Limits

Blender's official add-on has no strong security sandbox. Its weak guard
prevents a few problematic operations, not arbitrary filesystem access or
data transfer. A disposable project copy protects the accepted project, not
the host. Use only trusted, task-scoped commands and keep the bridge local.

The MCP checks here are selected geometry and integration tests, not a full
collision, physical-transformation or artistic-quality certification.
The generated image was visually inspected. No Computer Use clicks were used
to collect the Blender metrics or initiate the test render.

No model, animation or existing delivered video was changed by this setup.
