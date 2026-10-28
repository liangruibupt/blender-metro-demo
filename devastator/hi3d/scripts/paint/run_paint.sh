#!/usr/bin/env bash
# Paint the mvB 1536 mesh conditioned on concept_s0. Marker ~/PAINT_RUN_DONE.
set -uo pipefail
exec > >(tee -a "$HOME/paint.log") 2>&1
cd "$HOME/Hunyuan3D-2" && . "$HOME/Hi3Dv1.0/.venv/bin/activate"
export HF_HUB_DISABLE_SYMLINKS=1
mkdir -p "$HOME/painted"
( while true; do echo "VRAM $(date +%H:%M:%S) $(nvidia-smi --query-gpu=memory.used --format=csv,noheader)"; sleep 30; done ) &
SAMP=$!
t=$(date +%s)
python "$HOME/paint_devastator.py" "$HOME/out/mvB_refined_1536.glb" "$HOME/concept/concept_s0.png" "$HOME/painted/mvB1536" 150000
echo "paint rc=$? elapsed=$(( $(date +%s)-t ))s"
kill $SAMP 2>/dev/null
touch "$HOME/PAINT_RUN_DONE"; echo "PAINT_RUN_DONE $(date -u)"
