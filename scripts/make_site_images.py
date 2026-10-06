"""Generate the original, license-free hero imagery used on the website (frontend/public/img/*.webp).

Procedural dusk / sunset scenes (sky gradient, haze, layered silhouettes, film grain). Deterministic: same seed, same pixels.

    python scripts/make_site_images.py
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parents[1] / "frontend" / "public" / "img"
rng = np.random.default_rng(509)


def lerp(a, b, t):
    return a + (b - a) * t


def hex_rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i : i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def vgrad(w: int, h: int, stops: list[tuple[float, str]]) -> np.ndarray:
    """Vertical multi-stop gradient, float32 HxWx3."""
    ys = np.linspace(0, 1, h, dtype=np.float32)
    cols = np.array([hex_rgb(c) for _, c in stops])
    pos = np.array([p for p, _ in stops], dtype=np.float32)
    out = np.stack([np.interp(ys, pos, cols[:, k]) for k in range(3)], axis=-1)
    return np.repeat(out[:, None, :], w, axis=1)


def noise(w: int, h: int, octaves: int = 5, base: int = 4, persistence: float = 0.55) -> np.ndarray:
    """Smooth fractal noise in [0,1]."""
    total = np.zeros((h, w), np.float32)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        gw, gh = base * 2**o, max(2, int(base * 2**o * h / w))
        g = rng.random((gh, gw)).astype(np.float32)
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        total += amp * (np.asarray(img, np.float32) / 255)
        norm += amp
        amp *= persistence
    return total / norm


def radial(w: int, h: int, cx: float, cy: float, r: float, power: float = 2.0) -> np.ndarray:
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((x - cx * w) ** 2 + (y - cy * h) ** 2) / (r * w)
    return np.clip(1 - d, 0, 1) ** power


def to_img(a: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def grain(a: np.ndarray, amount: float = 7.0) -> np.ndarray:
    g = rng.normal(0, amount, a.shape[:2]).astype(np.float32)
    return a + g[..., None]


def vignette(a: np.ndarray, strength: float = 0.35) -> np.ndarray:
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    return a * (1 - strength * np.clip(d - 0.4, 0, 1)[..., None] ** 1.6)


def silhouette(mask: Image.Image, color: np.ndarray, base: np.ndarray, haze: np.ndarray, haze_amt: float, blur: float) -> np.ndarray:
    """Composite a silhouette (white-on-black mask) over `base`, tinted toward `haze` for atmospheric depth."""
    m = mask.filter(ImageFilter.GaussianBlur(blur)) if blur else mask
    alpha = (np.asarray(m, np.float32) / 255)[..., None]
    col = lerp(color, haze, haze_amt)
    return base * (1 - alpha) + col * alpha


def ridge(w: int, h: int, y0: float, amp: float, freq: float, seed_shift: float) -> Image.Image:
    """Smooth rolling ridge line as a mask."""
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    xs = np.arange(0, w + 8, 8)
    ys = [
        y0 * h
        + amp * h * (0.6 * math.sin(x * freq + seed_shift) + 0.3 * math.sin(x * freq * 2.3 + seed_shift * 1.7) + 0.1 * math.sin(x * freq * 5.1 + seed_shift * 0.4))
        for x in xs
    ]
    d.polygon([(0, h)] + list(zip(xs.tolist(), ys, strict=True)) + [(w, h)], fill=255)
    return im


def houses(w: int, h: int, baseline: float, scale: float, count: int, seed: int) -> Image.Image:
    """A row of suburban houses (gable roofs, chimneys) with a few utility poles and sagging wires."""
    r = np.random.default_rng(seed)
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    y = baseline * h
    x = -0.02 * w
    step = w / count
    poles: list[float] = []
    while x < w:
        bw = step * r.uniform(0.55, 0.95) * scale
        bh = bw * r.uniform(0.36, 0.55)
        rh = bw * r.uniform(0.22, 0.42)
        d.rectangle([x, y - bh, x + bw, y + 4], fill=255)
        if r.random() < 0.8:  # gable
            d.polygon([(x - bw * 0.06, y - bh), (x + bw * 0.5, y - bh - rh), (x + bw * 1.06, y - bh)], fill=255)
        else:  # hip/flat
            d.polygon([(x - bw * 0.04, y - bh), (x + bw * 0.14, y - bh - rh * 0.6), (x + bw * 0.86, y - bh - rh * 0.6), (x + bw * 1.04, y - bh)], fill=255)
        if r.random() < 0.55:
            cx = x + bw * r.uniform(0.62, 0.82)
            d.rectangle([cx, y - bh - rh * 1.05, cx + bw * 0.06, y - bh - rh * 0.4], fill=255)
        if r.random() < 0.35:
            poles.append(x + bw + step * 0.12)
        x += bw + step * r.uniform(0.04, 0.5)
    # trees between houses
    for _ in range(int(count * 0.9)):
        tx = r.uniform(0, w)
        tr = step * r.uniform(0.22, 0.5) * scale
        d.ellipse([tx - tr, y - tr * 1.7, tx + tr, y + 2], fill=255)
    # utility poles + wires (the grid)
    pole_x = sorted(poles)[:: max(1, len(poles) // 4)][:4]
    for px in pole_x:
        ph = h * 0.16 * scale
        d.rectangle([px, y - ph, px + 3 * scale, y + 2], fill=255)
        d.rectangle([px - 14 * scale, y - ph, px + 17 * scale, y - ph + 3 * scale], fill=255)
    for a, b in zip(pole_x, pole_x[1:], strict=False):
        for off in (0, 7, 14):
            pts = []
            for i in range(0, 41):
                t = i / 40
                sag = 4 * (t - t * t) * h * 0.012
                pts.append((lerp(a, b, t), y - h * 0.16 * scale + off * scale + sag))
            d.line(pts, fill=255, width=max(1, int(2 * scale)))
    return im


def scene_dusk(w: int = 2400, h: int = 1350) -> Image.Image:
    sky = vgrad(w, h, [(0.0, "#1c2124"), (0.38, "#3a403e"), (0.6, "#6d5e51"), (0.72, "#c07a47"), (0.8, "#e59a52"), (1.0, "#2a2018")])
    n = noise(w, h, 6, 3)
    clouds = np.clip((n - 0.42) * 2.6, 0, 1)[..., None]
    glow = radial(w, h, 0.72, 0.74, 0.55, 2.2)[..., None]
    sky = sky * (1 - 0.35 * clouds) + hex_rgb("#17191a") * 0.35 * clouds
    sky += glow * hex_rgb("#ff9b4a") * 0.55 * (1 - 0.55 * clouds)
    hot = radial(w, h, 0.72, 0.76, 0.16, 1.6)[..., None]
    sky += hot * hex_rgb("#ffd49a") * 0.5
    a = sky
    haze = hex_rgb("#a86a42")
    a = silhouette(ridge(w, h, 0.74, 0.03, 0.004, 0.5), hex_rgb("#4a3a30"), a, haze, 0.55, 5)
    a = silhouette(houses(w, h, 0.80, 0.62, 34, 3), hex_rgb("#2b221d"), a, haze, 0.45, 1.6)
    a = silhouette(ridge(w, h, 0.83, 0.02, 0.006, 2.1), hex_rgb("#231b17"), a, haze, 0.25, 2)
    a = silhouette(houses(w, h, 0.90, 1.05, 22, 9), hex_rgb("#17110e"), a, haze, 0.1, 1.0)
    fg = Image.new("L", (w, h), 0)
    ImageDraw.Draw(fg).rectangle([0, 0.93 * h, w, h], fill=255)
    a = silhouette(fg, hex_rgb("#0f0b09"), a, haze, 0.0, 6)
    a = vignette(grain(a, 6.0), 0.4)
    return to_img(a)


def scene_dunes(w: int = 2400, h: int = 1200) -> Image.Image:
    sky = vgrad(w, h, [(0.0, "#53301c"), (0.35, "#b2531f"), (0.62, "#ec8a2f"), (0.78, "#f6b457"), (1.0, "#e89b4a")])
    n = noise(w, h, 5, 3)
    sky *= (0.9 + 0.2 * n)[..., None]
    sun = radial(w, h, 0.56, 0.62, 0.05, 0.6)[..., None]
    sky = sky * (1 - sun) + hex_rgb("#fff0cc") * sun
    sky += radial(w, h, 0.56, 0.62, 0.45, 2.0)[..., None] * hex_rgb("#ffcf86") * 0.45
    a = sky
    haze = hex_rgb("#d77a35")
    for i, (y0, amp, f, col, ha, bl) in enumerate(
        [(0.66, 0.035, 0.0035, "#7a3a1a", 0.55, 3), (0.74, 0.045, 0.0028, "#5b2a14", 0.4, 2), (0.84, 0.05, 0.0021, "#3a1b0e", 0.2, 1.5), (0.94, 0.04, 0.0017, "#1f0f08", 0.0, 1.5)]
    ):
        a = silhouette(ridge(w, h, y0, amp, f, 1.3 * i + 0.4), hex_rgb(col), a, haze, ha, bl)
    return to_img(vignette(grain(a, 6.0), 0.3))


def save(im: Image.Image, name: str, max_w: int, quality: int = 74) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    p = OUT / name
    im.save(p, "WEBP", quality=quality, method=6)
    print(f"{name}: {im.size}, {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    save(scene_dusk(), "dusk.webp", 2000)
    save(scene_dunes(), "sunset.webp", 2000)
