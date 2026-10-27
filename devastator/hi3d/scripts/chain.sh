#!/usr/bin/env bash
# Devastator Hi3D geometry run: env install chain (Hi3D + Hunyuan3D-2 mini/mv shapegen).
# Logs to ~/chain.log. Writes ~/CHAIN_DONE on success.
set -uo pipefail
exec > >(tee -a "$HOME/chain.log") 2>&1
echo "=== chain start $(date -u) ==="
bash "$HOME/hi3d_env.sh" || { echo CHAIN_FAIL_hi3d; exit 1; }
bash "$HOME/hunyuan_env.sh" || { echo CHAIN_FAIL_hunyuan; exit 1; }
cd "$HOME/Hi3Dv1.0" && . .venv/bin/activate
# verified dependency fixes (see oss-image-models-lab docs/HI3D_eval.md)
pip install -q "diffusers==0.31.0" "huggingface-hub==0.28.1" xatlas rembg onnxruntime trimesh pyrender
echo "$HOME/Hunyuan3D-2" > "$(python -c 'import site;print(site.getsitepackages()[0])')/hunyuan.pth"
python -c "from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline; print('shapegen OK')" || { echo CHAIN_FAIL_shapegen; exit 1; }
python -c "from sparc3d import Sparc3DPipeline; print('sparc3d OK')" || { echo CHAIN_FAIL_sparc3d; exit 1; }
# pre-download weights without symlinks (Hi3D loader rejects symlinks)
export HF_HUB_DISABLE_SYMLINKS=1 HF_HUB_ENABLE_HF_TRANSFER=0
python - <<'PY'
from huggingface_hub import snapshot_download
for rid in ["hi3d-official/Hi3Dv1.0", "tencent/Hunyuan3D-2mini", "tencent/Hunyuan3D-2mv"]:
    try:
        p = snapshot_download(rid); print("downloaded", rid, p)
    except Exception as e:
        print("DL_WARN", rid, e)
PY
# belt and braces: dereference any symlinks left in the HF cache snapshots
find "$HOME/.cache/huggingface/hub" -path '*snapshots*' -type l | while read -r l; do
  t=$(readlink -f "$l"); rm "$l"; cp "$t" "$l"; done
echo "symlinks left: $(find "$HOME/.cache/huggingface/hub" -path '*snapshots*' -type l | wc -l)"
touch "$HOME/CHAIN_DONE"; echo "CHAIN_DONE $(date -u)"
