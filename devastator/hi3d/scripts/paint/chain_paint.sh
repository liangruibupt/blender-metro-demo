#!/usr/bin/env bash
# Devastator Hi3D paint chain (runs on the GPU box under nohup). Markers in ~/: CONCEPT_ENV_DONE, PAINT_ENV_DONE, CHAIN_DONE.
# Track A (background): Qwen-Image-Edit env in ~/.venv -> colored concept images (GPU).
# Track B (foreground): Hi3D venv + hy3dgen + texgen CUDA extensions (CPU compile), then Paint weights.
set -uo pipefail
exec > >(tee -a "$HOME/chain.log") 2>&1
echo "=== paint chain start $(date -u) ==="
bash "$HOME/prelude.sh" || { echo CHAIN_FAIL_prelude; exit 1; }

(
  set -uo pipefail
  exec > "$HOME/concept.log" 2>&1
  # inline copy of oss-image-models-lab box_env.sh minus apt (prelude did it; avoids dpkg lock race with hi3d_env.sh)
  cd "$HOME" && python3 -m venv .venv && . .venv/bin/activate && pip install -q --upgrade pip wheel \
    && pip install -q "torch==2.7.*" "torchvision==0.22.*" \
    && pip install -q -U diffusers transformers accelerate safetensors sentencepiece \
    && python -c "import diffusers; from diffusers import QwenImageEditPlusPipeline; print('diffusers', diffusers.__version__)" \
    && touch "$HOME/CONCEPT_ENV_DONE" || { echo CONCEPT_FAIL_env; exit 1; }
  python color_concept.py "$HOME/inputs/rgba_frame_00.png" "$HOME/concept" 0,1,2 || echo CONCEPT_FAIL_run
) &

export MAX_JOBS=2
bash "$HOME/hi3d_env.sh" || { echo CHAIN_FAIL_hi3d; exit 1; }
bash "$HOME/hunyuan_env.sh" || { echo CHAIN_FAIL_hunyuan; exit 1; }
cd "$HOME/Hi3Dv1.0" && . .venv/bin/activate
pip install -q "diffusers==0.31.0" "huggingface-hub==0.28.1" xatlas rembg onnxruntime trimesh pyrender pymeshlab omegaconf pygltflib
echo "$HOME/Hunyuan3D-2" > "$(python -c 'import site;print(site.getsitepackages()[0])')/hunyuan.pth"
bash "$HOME/paint_env.sh"
python -c "from hy3dgen.texgen import Hunyuan3DPaintPipeline; print('texgen OK')" || { echo CHAIN_FAIL_texgen; exit 1; }
touch "$HOME/PAINT_ENV_DONE"
export HF_HUB_DISABLE_SYMLINKS=1
python - <<'PY'
from huggingface_hub import snapshot_download
print(snapshot_download("tencent/Hunyuan3D-2", allow_patterns=["hunyuan3d-paint-v2-0/*", "hunyuan3d-delight-v2-0/*"]))
PY
touch "$HOME/CHAIN_DONE"; echo "CHAIN_DONE $(date -u)"
