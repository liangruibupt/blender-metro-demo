#!/usr/bin/env bash
# Phase 2: 1536 refine for the single-view and the multi-view (mvB) coarse meshes. Marker RUNS2_DONE.
set -uo pipefail
exec > >(tee -a "$HOME/runs.log") 2>&1
cd "$HOME/Hi3Dv1.0" && . .venv/bin/activate
export HF_HUB_DISABLE_SYMLINKS=1
I="$HOME/inputs"; O="$HOME/out"
( while true; do echo "VRAM $(date +%H:%M:%S) $(nvidia-smi --query-gpu=memory.used --format=csv,noheader)"; sleep 30; done ) &
SAMP=$!
step() { local name=$1; shift; local t=$(date +%s); echo "=== $name start $(date -u) ==="; "$@"; local rc=$?; echo "=== $name rc=$rc elapsed=$(( $(date +%s)-t ))s ==="; }
step mvB_1536 python demo/refine_mesh.py --model hi3d-official/Hi3Dv1.0 --image "$I/rgba_frame_00.png" \
  --coarse-mesh "$O/mvB_coarse.glb" --output "$O/mvB_refined_1536.glb" --resolution 1536 --seed 0 --sequential-cpu-offload
step sv_1536 python demo/refine_mesh.py --model hi3d-official/Hi3Dv1.0 --image "$I/rgba_rex-hsu-b-0001.png" \
  --coarse-mesh "$O/sv_coarse.glb" --output "$O/sv_refined_1536.glb" --resolution 1536 --seed 0 --sequential-cpu-offload
kill $SAMP 2>/dev/null
echo "RUNS2_DONE $(date -u)"
