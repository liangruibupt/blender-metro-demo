"""Deterministic PBR surface maps, embedded in both GLB and the Blender file."""

import bpy
import numpy as np


def image(name, rgb, directory, color=False):
    height, width = rgb.shape[:2]
    result = bpy.data.images.new(name, width=width, height=height, alpha=True)
    result.colorspace_settings.name = "sRGB" if color else "Non-Color"
    rgba = np.ones((height, width, 4), dtype=np.float32)
    if color:
        rgb = np.where(rgb <= .0031308, rgb*12.92, 1.055*np.maximum(rgb, 0)**(1/2.4)-.055)
    rgba[:, :, :3] = np.clip(rgb, 0, 1)
    result.pixels.foreach_set(rgba.ravel())
    result.filepath_raw = str(directory / f"{name}.png")
    result.file_format = "PNG"
    result.save()
    result.pack()
    return result


def build_maps(directory, palette):
    directory.mkdir(parents=True, exist_ok=True)
    size = 512
    rng = np.random.default_rng(240913)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    u, v = x/(size-1), y/(size-1)
    grain = rng.random((size, size), dtype=np.float32)
    brushing = rng.random((size, 1), dtype=np.float32)*.30+grain*.70
    distance = np.minimum.reduce([u, 1-u, v, 1-v])
    broken_edge = np.clip(1-distance/.021, 0, 1)
    broken_edge *= np.clip(.35+grain*.8+np.sin(x*.23)*np.cos(y*.19)*.3, 0, 1)
    scratches = np.zeros((size, size), dtype=np.float32)
    for _ in range(80):
        yy, xx = rng.integers(2, size-30, size=2)
        length = int(rng.integers(5, 42))
        scratches[yy, xx:min(size, xx+length)] = rng.uniform(.1, .8)
    wear = np.clip(broken_edge*.8+scratches*.34, 0, .85)
    height = brushing*.0015-scratches*.002-broken_edge*.001
    dy, dx = np.gradient(height)
    normal = np.stack((-dx*11, -dy*11, np.ones_like(dx)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    normal_map = image("micro-brushed-normal", normal*.5+.5, directory)
    maps = {}
    for key, (color, metallic, roughness) in palette.items():
        base = np.array(color, dtype=np.float32)[None, None, :]
        shade = (.91+grain*.10+brushing*.07)[:, :, None]
        steel = np.array((.34, .37, .41), dtype=np.float32)[None, None, :]
        rgb = base*shade*(1-wear[:, :, None])+steel*wear[:, :, None]
        packed = np.ones((size, size, 3), dtype=np.float32)
        packed[:, :, 1] = np.clip(roughness+(brushing-.5)*.08+wear*.10, .12, .65)
        packed[:, :, 2] = metallic+(1-metallic)*wear
        maps[key] = (
            image(f"{key}-base", rgb, directory, color=True),
            image(f"{key}-metal-rough", packed, directory),
        )
    return maps, normal_map
