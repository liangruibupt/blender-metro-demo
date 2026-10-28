#!/usr/bin/env bash
# Resume the mv chain after the edit step (envs + prepare already done). Usage: chain_mv2.sh "180,90,270,0"
set -uo pipefail
exec > >(tee -a "$HOME/mv.log") 2>&1
echo "=== mv chain2 start $(date -u) views=$1 ==="
export HF_HUB_DISABLE_SYMLINKS=1
cd "$HOME" && . .venv/bin/activate
python "$HOME/mv_edit.py" "$HOME/concept/concept_s0.png" 0 "$1" || { echo MV_FAIL_edit; exit 1; }
deactivate
for a in 0 90 180 270; do test -f "$HOME/mv/color_$a.png" || { echo "EDIT_PARTIAL missing $a"; exit 0; }; done
touch "$HOME/EDIT_OK"
cd "$HOME/Hunyuan3D-2" && . "$HOME/Hi3Dv1.0/.venv/bin/activate"
python "$HOME/mv_bake.py" && touch "$HOME/BAKE_OK" || { echo MV_FAIL_bake; exit 1; }
cd "$HOME" && python "$HOME/mv_render.py" || echo MV_WARN_render
touch "$HOME/MV_DONE"; echo "MV_DONE $(date -u)"
