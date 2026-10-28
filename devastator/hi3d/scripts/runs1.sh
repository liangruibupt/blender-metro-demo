#!/usr/bin/env bash
# Devastator geometry runs, phase 1 (1024). Logs ~/runs.log, outputs ~/out/. Marker RUNS1_DONE.
set -uo pipefail
exec > >(tee -a "$HOME/runs.log") 2>&1
cd "$HOME/Hi3Dv1.0" && . .venv/bin/activate
export HF_HUB_DISABLE_SYMLINKS=1
I="$HOME/inputs"; O="$HOME/out"; mkdir -p "$O"
( while true; do echo "VRAM $(date +%H:%M:%S) $(nvidia-smi --query-gpu=memory.used --format=csv,noheader)"; sleep 30; done ) &
SAMP=$!
step() { local name=$1; shift; local t=$(date +%s); echo "=== $name start $(date -u) ==="; "$@"; local rc=$?; echo "=== $name rc=$rc elapsed=$(( $(date +%s)-t ))s ==="; }

# A) single view: ArtStation full-body front render -> mini coarse -> Hi3D 1024
step sv_1024 python demo/image_to_mesh.py --model hi3d-official/Hi3Dv1.0 \
  --image "$I/rgba_rex-hsu-b-0001.png" --output "$O/sv_refined_1024.glb" --coarse-output "$O/sv_coarse.glb" \
  --resolution 1024 --seed 0 --sequential-cpu-offload
# B) multi view coarse from turntable frames 00/06/12/18 (90 deg apart). Turntable direction is
#    not documented, so try both left/right assignments and keep whichever is coherent.
step mvA_coarse python "$HOME/coarse_mv.py" "$O/mvA_coarse.glb" "$I/rgba_frame_00.png" "$I/rgba_frame_06.png" "$I/rgba_frame_12.png" "$I/rgba_frame_18.png"
step mvB_coarse python "$HOME/coarse_mv.py" "$O/mvB_coarse.glb" "$I/rgba_frame_00.png" "$I/rgba_frame_18.png" "$I/rgba_frame_12.png" "$I/rgba_frame_06.png"
for v in mvA mvB; do
  step ${v}_1024 python demo/refine_mesh.py --model hi3d-official/Hi3Dv1.0 --image "$I/rgba_frame_00.png" \
    --coarse-mesh "$O/${v}_coarse.glb" --output "$O/${v}_refined_1024.glb" --resolution 1024 --seed 0 --sequential-cpu-offload
done
kill $SAMP 2>/dev/null
ls -la "$O"
echo "RUNS1_DONE $(date -u)"
