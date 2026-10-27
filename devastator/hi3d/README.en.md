# Devastator / Hi3D v1.0 Geometry Study

[简体中文](README.md) | **English**

Devastator geometry generated from the reference images and turntable video with
**Hunyuan3D-2 (coarse mesh) + Hi3D v1.0 (geometry refinement)**. **Geometry only, no color.**
Run on 2026-10-27 on one 48 GB L40S (AWS g6e.xlarge, Tokyo). Method and environment fixes follow the
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

## Not committed

**The generated GLB meshes are not in the repository.** The inputs are Rex Hsu's reference artwork
(see [`../REFERENCE.md`](../REFERENCE.md)) with no redistribution permission; 3D models generated directly
from it are derivative content and riskier to publish than these documentation renders. The full meshes
(coarse, 1024, 1536; 8 files, ~200 MB) are kept on the Kiro Crew host that ran the study
(`/home/ubuntu/workplace/devastator-hi3d-run/out/`, outside Git). They can be added once rights are confirmed,
or the study can be rerun from original references.

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

## Next steps (not done)

- **Color**: the references are grey clay with no color information. Make a color concept image first
  (e.g. a G1 green/purple scheme), then decimate and generate a UV texture with Hunyuan3D-Paint.
- **View selection**: Hunyuan3D-2mv takes at most front/left/back/right; try other frame sets and seeds.
- **Retopology**: bake the 2M-face mesh to a low-poly + normal map with oss-image-models-lab's `blender_retopo_bake.py`.
