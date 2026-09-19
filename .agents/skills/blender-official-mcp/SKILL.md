---
name: blender-official-mcp
description: Create, edit, inspect, and validate native Blender models, scenes, and animations using the user's installed official Blender Lab MCP. Prefer it for Blender project work; this does not apply to Three.js-only web projects.
---

# Official Blender MCP

## User Preference

Use the official Blender Lab MCP as the preferred interface for Blender project
development and scene verification. Use its structured queries and Python API
instead of clicking through the UI for measurable data.

## Installed Connection

- Codex server: `blender-official`, registered globally.
- Executable: `/Users/ruiliang/Documents/workspaces/venv/bin/blender-mcp`.
- Transport: stdio. Bridge: `127.0.0.1:9876`.
- Native Blender: `/Applications/Blender.app/Contents/MacOS/Blender`.
- Add-on: `bl_ext.lab_blender_org.mcp`, auto-start enabled.
- Official source: https://projects.blender.org/lab/blender_mcp
- Installed release: `v1.0.3`, commit `2cea8d566dde07fbac28a61d698909d69724e853`.
- Reference documentation: https://www.blender.org/lab/mcp-server/

The official and third-party projects share the distribution name `blender-mcp`.
Do not replace this installation using a bare `uvx blender-mcp` or a PyPI upgrade.
An upgrade must come from the verified official repository and be coordinated
with the add-on version. Use the user's existing workspace venv; do not create
a replacement environment without authorization.

## Working Pattern

1. Discover the tools exposed by `blender-official`. Check the connected file
   before editing. Do not replace another open project or discard unsaved work.
2. Use scene/object summary tools for inventory and missing dependencies.
   Use `execute_blender_code` for task-specific metrics and authorized edits.
   Return structured results by assigning a JSON-serializable dict to `result`.
3. For animation QA, save and restore the current frame and subframe. Check the
   evaluated geometry and render settings, not only viewport modifier settings.
   Run regression checks against the accepted model or manifest.
4. Use `render_viewport_to_path` for a render with current scene settings.
   Its output is redirected into Blender's scratch directory; use the returned
   filepath. `render_thumbnail_to_path` is preview-only, not final-quality QA.
5. Keep visual inspection alongside numerical checks. A passed geometry check
   does not establish visual likeness, physical plausibility or artistic quality.

For read-only setup tests, use a disposable scene copy and verify the original
file hash before and after. A copy is not an operating-system security sandbox.
The server executes Python with Blender's permissions. Keep it on loopback;
do not expose it remotely or send project data to unrelated services.

## Availability and Long Jobs

Blender must be running with its bridge started for live tools. CLI-suffixed
official tools can inspect saved files using the configured native Blender.
Do not silently substitute a third-party server when this connection fails.

A newly registered server may require a new Codex session or app restart before
its tools appear. For installation diagnostics, a real MCP SDK stdio client is
acceptable; distinguish that protocol test from native tool discovery in the
current conversation.

Keep long renders resumable and avoid waiting synchronously beyond tool
timeouts. Existing batch scripts remain valid where needed for long rendering
or independent validation; explain that choice rather than claiming they are
MCP calls. Prefer MCP for live edits, queries and render initiation when suitable.

## Verified Example

The Devastator V2 project contains a reproducible real-protocol verification:

`/Users/ruiliang/Documents/workspaces/blender-metro-demo/devastator/v2/MCP_SETUP.md`

It verifies scene queries, all 432 animation frames, a full-resolution render,
state restoration and unchanged source hashes. Read it when reproducing setup
or adapting its validation harness, not for unrelated Blender tasks.
