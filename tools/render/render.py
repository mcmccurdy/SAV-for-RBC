"""Image helpers for the Ra = 10^6 figure (tables/fig_ra1e6.py).

lic:     line-integral-convolution texture of a velocity field on a uniform image grid (periodic in x)
stretch: contrast stretch of the temperature around the bulk value 1/2
color:  RGB image from the temperature and the texture
"""
import numpy as np
from scipy.ndimage import map_coordinates


def lic(u, v, length=18, h=0.6, seed=1):
    """line integral convolution of white noise along (u,v) on a uniform image grid (x periodic)"""
    Ny, Nx = u.shape
    rng = np.random.default_rng(seed)
    noise = rng.random((Ny, Nx))
    sp = np.hypot(u, v) + 1e-12
    du, dv = u / sp, v / sp
    J, I = np.mgrid[0:Ny, 0:Nx].astype(float)
    acc = noise.copy(); cnt = np.ones_like(noise)
    for sgn in (1.0, -1.0):
        px, py = I.copy(), J.copy()
        for s in range(length):
            cu = map_coordinates(du, [py, px], order=1, mode='grid-wrap')
            cv = map_coordinates(dv, [py, px], order=1, mode='grid-wrap')
            px = (px + sgn * h * cu) % Nx
            py = np.clip(py + sgn * h * cv, 0, Ny - 1)
            w = 1.0 - s / length                      # tapered kernel
            acc += w * map_coordinates(noise, [py, px], order=1, mode='grid-wrap')
            cnt += w
    out = acc / cnt
    return (out - out.mean()) / (out.std() + 1e-12)


def stretch(T, s):
    """contrast stretch around the bulk temperature 1/2, keeping 0 and 1 fixed (s=0: none)"""
    if s <= 0: return T
    return 0.5 + 0.5 * np.tanh((T - 0.5) / s) / np.tanh(0.5 / s)


def color(Ti, tex, cmap, lic_strength=0.05, s=0.0):
    """RGB image from temperature (contrast stretch s) and LIC texture (strength lic_strength; 0 = none)"""
    rgb = cmap(np.clip(stretch(Ti, s), 0, 1))[..., :3]
    if lic_strength > 0:
        rgb = np.clip(rgb * (1.0 + lic_strength * tex[..., None]), 0, 1)
    return rgb[::-1]          # row 0 = top of the cell
