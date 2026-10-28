#!/usr/bin/env bash
# Multi-view color pass chain (nohup on GPU box). Markers in ~/: MV_ENVS_DONE, PREPARE_OK, EDIT_OK, BAKE_OK, MV_DONE.
set -uo pipefail
exec > >(tee -a "$HOME/mv.log") 2>&1
echo "=== mv chain start $(date -u) ==="
bash "$HOME/prelude.sh" || { echo MV_FAIL_prelude; exit 1; }

# Track A (background): diffusers venv + prefetch Qwen-Image-Edit-2511 weights (~58 GB) while CUDA ext compile
(
  exec > "$HOME/qwen_env.log" 2>&1
  cd "$HOME" && python3 -m venv .venv && . .venv/bin/activate && pip install -q --upgrade pip wheel \
    && pip install -q "torch==2.7.*" "torchvision==0.22.*" \
    && pip install -q -U diffusers transformers accelerate safetensors sentencepiece \
    && python -c "from huggingface_hub import snapshot_download as s; print(s('Qwen/Qwen-Image-Edit-2511'))" \
    && touch "$HOME/QWEN_ENV_DONE" || echo QWEN_ENV_FAIL
) &
QPID=$!

export MAX_JOBS=2
bash "$HOME/hi3d_env.sh" || { echo MV_FAIL_hi3d; exit 1; }
bash "$HOME/hunyuan_env.sh" || { echo MV_FAIL_hunyuan; exit 1; }
cd "$HOME/Hi3Dv1.0" && . .venv/bin/activate
pip install -q "diffusers==0.31.0" "huggingface-hub==0.28.1" xatlas rembg onnxruntime trimesh pyrender pymeshlab omegaconf pygltflib imageio imageio-ffmpeg
echo "$HOME/Hunyuan3D-2" > "$(python -c 'import site;print(site.getsitepackages()[0])')/hunyuan.pth"
bash "$HOME/paint_env.sh"
python -c "from hy3dgen.texgen import Hunyuan3DPaintPipeline; print('texgen OK')" || { echo MV_FAIL_texgen; exit 1; }
wait $QPID; test -f "$HOME/QWEN_ENV_DONE" || { echo MV_FAIL_qwen_env; exit 1; }
touch "$HOME/MV_ENVS_DONE"; echo "MV_ENVS_DONE $(date -u)"

export HF_HUB_DISABLE_SYMLINKS=1
cd "$HOME/Hunyuan3D-2" && . "$HOME/Hi3Dv1.0/.venv/bin/activate"
python "$HOME/mv_prepare.py" "$HOME/out/mvB_refined_1536.glb" "$HOME/painted/mvB1536_150000_cond.png" 150000 && touch "$HOME/PREPARE_OK" || { echo MV_FAIL_prepare; exit 1; }
deactivate
cd "$HOME" && . .venv/bin/activate
python "$HOME/mv_edit.py" "$HOME/concept/concept_s0.png" 0 && touch "$HOME/EDIT_OK" || { echo MV_FAIL_edit; exit 1; }
deactivate
cd "$HOME/Hunyuan3D-2" && . "$HOME/Hi3Dv1.0/.venv/bin/activate"
python "$HOME/mv_bake.py" && touch "$HOME/BAKE_OK" || { echo MV_FAIL_bake; exit 1; }
cd "$HOME" && python "$HOME/mv_render.py" || echo MV_WARN_render
touch "$HOME/MV_DONE"; echo "MV_DONE $(date -u)"
