# Devastator / Hi3D v1.0 Geometry and Color Study

[简体中文](README.md) | **English**

Devastator geometry generated from the reference images and turntable video with
**Hunyuan3D-2 (coarse mesh) + Hi3D v1.0 (geometry refinement)**. Geometry run on 2026-10-27; [color](#color-qwen-image-edit--hunyuan3d-2-paint) added 2026-10-28.
Both on one 48 GB L40S (AWS g6e.xlarge, Tokyo). Method and environment fixes follow the
[oss-image-models-lab Hi3D evaluation](https://github.com/liangruibupt/oss-image-models-lab#-hi3d-v10图像--3d-几何细化).

## Findings

- **A multi-view coarse mesh is what makes it work.** Four turntable frames about 90° apart, fed to
  Hunyuan3D-2mv, give a coarse mesh that matches the reference from every side: raised cannon,
  staggered stance, mixer drum, truck cab, tracks and wheel sets all land in roughly the right place.
  With one front image (Hunyuan3D-2mini) the front reads well, but the back and sides are invented and the pose drifts.
- **Hi3D refinement is a large visible step.** The coarse mesh looks like melted clay; 1024 adds flat hard
  surfaces, panel seams, tire treads, grilles and fins; 1536 sharpens edges and small raised details.
- **It is not an exact replica.** Thin parts in the reference (four-barrel muzzle, crane cables, track links,
  hydraulic hoses, mesh railings) are averaged into solids or replaced by plausible invented greebles.
  There are no separable parts, so no V2-style assembly animation. The output is one triangle soup
  (2M faces, 271 pieces, not watertight) that needs retopology/repair before editing, printing or painting.
- **Use it as** a fast high-poly sculpt that resembles the reference (stills, 360° video, concept review,
  a starting point for painting or retopology), not as a replacement for V2's part-by-part editable, animatable model.

## Reference vs Hi3D (matching angles)

Row 1: reference video frames (background removed). Row 2: multi-view coarse + Hi3D 1536.
Row 3: single-view coarse + Hi3D 1536. All meshes use one matte grey material, not textures.

![Reference frames vs Hi3D 1536 multi-view vs single-view](images/ref-vs-hi3d.jpg)

## Refinement stages (upper-body close-up, multi-view)

![Coarse vs Hi3D 1024 vs Hi3D 1536 close-up](images/closeups-coarse-1024-1536.jpg)

## 360° turntable

[devastator-hi3d-360.mp4](deliverables/devastator-hi3d-360.mp4): 12 s, 1280 × 720, 24 fps, multi-view + Hi3D 1536 clay.

## Intermediate comparisons

<details>
<summary>Coarse: single view vs two multi-view frame assignments</summary>

The reference turntable's rotation direction is not recorded, so both left/right assignments were tried
(mvA: left = frame 6; mvB: left = frame 18). mvB has a more coherent cannon and back and was used for 1536.

![Coarse comparison](images/coarse-sv-vs-mv.jpg)
</details>

<details>
<summary>1024: single view vs multi-view (mvA)</summary>

![1024 comparison](images/sv-vs-mv-1024.jpg)
</details>

<details>
<summary>Multi-view mvB: coarse vs 1024</summary>

![mvB coarse vs 1024](images/mv-coarse-vs-1024.jpg)
</details>

## Measurements

| Run | Input | Time | Peak VRAM | Output (verts / faces / pieces) |
| --- | --- | --- | --- | --- |
| Single-view coarse + Hi3D 1024 | `rex-hsu-b-0001.jpg` | 589 s (incl. coarse) | 11.7 GB | 494K / 1.0M / 1,822 |
| Multi-view coarse mvA / mvB | video frames 00/06/12/18 | 34 s inference (+1–2 min load) | — | 809K / 1.6M; 738K / 1.5M |
| mvA → Hi3D 1024 | coarse + frame 00 | 438 s | 13.2 GB | 499K / 1.0M |
| mvB → Hi3D 1024 | coarse + frame 00 | 429 s | 9.8 GB | 499K / 1.0M / 204 |
| mvB → Hi3D 1536 | coarse + frame 00 | 613 s | 19.5 GB | 999K / 2.0M / 271 |
| Single view → Hi3D 1536 | coarse + `rex-hsu-b-0001` | 643 s | 23.6 GB | 993K / 2.0M / 910 |

All with `--sequential-cpu-offload`. Peak VRAM is sampled every 30 s and may undercount. No mesh is watertight.
The whole session (setup, ~70 GB of weights, 7 runs, renders) took about 1.5 hours; the instance was then terminated.

## Generated meshes (GLB)

All 8 meshes are in [`models/`](models/) (~207 MB total, not watertight; all untextured grey except the last):

| File | What | Size |
| --- | --- | --- |
| [`sv_coarse.glb`](models/sv_coarse.glb) | Single-view coarse (Hunyuan3D-2 mini) | 15 MB |
| [`sv_refined_1024.glb`](models/sv_refined_1024.glb) | Single view → Hi3D 1024 | 18 MB |
| [`sv_refined_1536.glb`](models/sv_refined_1536.glb) | Single view → Hi3D 1536 | 36 MB |
| [`mvA_coarse.glb`](models/mvA_coarse.glb) | Multi-view coarse mvA (Hunyuan3D-2mv) | 29 MB |
| [`mvA_refined_1024.glb`](models/mvA_refined_1024.glb) | mvA → Hi3D 1024 | 18 MB |
| [`mvB_coarse.glb`](models/mvB_coarse.glb) | Multi-view coarse mvB | 27 MB |
| [`mvB_refined_1024.glb`](models/mvB_refined_1024.glb) | mvB → Hi3D 1024 | 18 MB |
| [`mvB_refined_1536.glb`](models/mvB_refined_1536.glb) | **mvB → Hi3D 1536 (recommended)** | 36 MB |
| [`mvB_1536_painted_150k.glb`](models/mvB_1536_painted_150k.glb) | mvB 1536 decimated to 150k + Paint color (2048² texture) | 10 MB |

The inputs are Rex Hsu's reference artwork (see [`../REFERENCE.md`](../REFERENCE.md)); these meshes are
derivative content published for technical documentation only. Confirm rights before redistributing or
using them commercially.

## Reproduce

Scripts are in [`scripts/`](scripts/); run them in order:

1. `launch_gpu.py`: launch a g6e.xlarge with boto3 (dedicated key pair and security group).
2. `chain.sh` (calls oss-image-models-lab's `hi3d_env.sh` and `hunyuan_env.sh`): install, pin
   `diffusers==0.31.0` and `huggingface-hub==0.28.1`, pre-download Hi3D, Hunyuan3D-2mini and Hunyuan3D-2mv with
   `HF_HUB_DISABLE_SYMLINKS=1`, and dereference leftover symlinks (Hi3D's loader rejects them).
3. `prep_inputs.py`: sample 24 frames from the reference video, remove backgrounds, crop to centred 1024 × 1024 RGBA.
4. `runs1.sh`: single-view 1024, two multi-view coarse meshes (`coarse_mv.py`) and their 1024 refinements.
5. `runs2.sh`: 1536 refinement for mvB and the single view.
6. `render_clay.py`, `final_assets.py`: comparison sheets, close-ups and the 360° video.

Terminate the instance and delete `devastator-hi3d-key` and `devastator-hi3d-sg` afterwards.

## Color (Qwen-Image-Edit + Hunyuan3D-2 Paint)

Added 2026-10-28. The references are grey clay with no color, so this takes two steps:

1. **Colored concept image**: [Qwen-Image-Edit-2511](https://huggingface.co/Qwen/Qwen-Image-Edit-2511) repaints
   reference frame 00 (the same front view mvB was refined against) in the G1 Devastator scheme: lime-green armor,
   purple joints, silver barrels, red eyes, with pose and structure kept.
2. **Texture**: decimate the mvB 1536 mesh (2M faces) to 150k faces, then Hunyuan3D-2 Paint runs multi-view diffusion
   conditioned on the concept and bakes one 2048 × 2048 UV color texture into a textured GLB.

![Grey reference frame vs colored concept](images/color-concept.jpg)

Row 1: reference frame, concept, baked UV texture, painted close-up. Row 2: painted mesh at 0/90/180/270°.

![Painted result](images/color-views.jpg)

Hi3D clay (top) vs painted (bottom) at matching angles:

![Clay vs painted](images/color-vs-clay.jpg)

360° color turntable: [devastator-hi3d-color-360.mp4](deliverables/devastator-hi3d-color-360.mp4) (12 s, 1280 × 720, 24 fps).
Painted mesh: [`models/mvB_1536_painted_150k.glb`](models/mvB_1536_painted_150k.glb) (10 MB, 150k faces + 2048² texture).

**Observations**

- **The front is best**: the large color regions (green armor, purple torso and joints, silver barrels, red lights)
  match the concept and read clearly as G1 Devastator.
- **Sides and back are inferred**: the concept covers only the front, so Paint's multi-view diffusion fills in the other
  sides. It keeps the green/purple scheme, but regions are less accurate than the front, with smears and seams.
- **Detail is soft**: at 150k faces the texture carries large color regions only, with no paint lines or weathering;
  colors of small parts often bleed into neighbors. The UVs are xatlas auto-unwrap fragments, not hand-editable.
- **Use it as** a concept / color-scheme preview for stills and turntables, not finished figure paintwork.
- The rock base came out purple because the concept image painted it purple.

**Measurements (one L40S)**

| Step | Time | Peak VRAM |
| --- | --- | --- |
| Qwen-Image-Edit-2511 concept (1024², 40 steps, model CPU offload) | 807 s incl. swapping (+555 s first load) | 39.1 GB |
| Decimate 2M → 150k + Paint load | 189 s load | — |
| Hunyuan3D-2 Paint (multi-view diffusion + bake) | 210 s | 9.7 GB |

g6e.xlarge has only 30 GB RAM; offloading the 20B Qwen-Image-Edit model needed a 96 GB swap file on NVMe.
The session took about 45 minutes; the instance was then terminated.

**Reproduce**: scripts in [`scripts/paint/`](scripts/paint/): `chain_paint.sh` (runs `prelude.sh` for swap + apt; needs
oss-image-models-lab's `hi3d_env.sh`, `hunyuan_env.sh`, `paint_env.sh`) → `color_concept.py` → `run_paint.sh`
(`paint_devastator.py`) → `render_color.py`.

## Next steps (not done)

- **Multi-view concepts**: make colored concepts for the back and sides too (from turntable frames) so Paint stops guessing them.
- **View selection**: Hunyuan3D-2mv takes at most front/left/back/right; try other frame sets and seeds.
- **Retopology**: bake the 2M-face mesh to a low-poly + normal map with oss-image-models-lab's `blender_retopo_bake.py`
  before painting; detail will hold up better than plain decimation.
