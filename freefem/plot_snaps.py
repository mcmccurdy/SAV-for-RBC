"""Render the temperature snapshots written by nsb.edp -snap N.
usage: python3 plot_snaps.py run.txt [every]   -> run.txt.snapNNNN.png (and a strip of six, run_snaps.png)"""
import sys, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
base = sys.argv[1]; every = int(sys.argv[2]) if len(sys.argv) > 2 else 1
files = sorted(glob.glob(base + '.snap1*'))[::every]
def load(f):
    h = open(f).readline().split(); d = dict(zip(h[1::2], h[2::2]))
    nx, ny, L = int(d['nx=']), int(d['ny=']), float(d['L='])
    a = np.loadtxt(f, comments='#')
    T = (a[:, 0] if a.ndim == 2 else a).reshape(ny + 1, nx + 1)     # column T (u_x, u_y follow with -snapu 1)
    return float(d['t=']), T, L, float(d['Tmin=']), float(d['Tmax='])
for f in files:
    t, T, L, a, b = load(f)
    fig, ax = plt.subplots(figsize=(8, 2.3))
    ax.imshow(T, origin='lower', extent=[0, L, 0, 1], cmap='RdBu_r', vmin=0, vmax=1, interpolation='bilinear')
    ax.set_title(f't = {t:.4g}   T in [{a:.4f}, {b:.4f}]', fontsize=9); ax.set_xticks([]); ax.set_yticks([])
    fig.savefig(f + '.png', dpi=150, bbox_inches='tight'); plt.close(fig)
print(len(files), 'snapshots rendered')
if len(files) >= 6:
    pick = [files[int(i)] for i in np.linspace(0, len(files) - 1, 6)]
    fig, axs = plt.subplots(6, 1, figsize=(8, 12))
    for ax, f in zip(axs, pick):
        t, T, L, a, b = load(f)
        ax.imshow(T, origin='lower', extent=[0, L, 0, 1], cmap='RdBu_r', vmin=0, vmax=1, interpolation='bilinear')
        ax.set_title(f't = {t:.4g}', fontsize=9); ax.set_xticks([]); ax.set_yticks([])
    fig.savefig(base.rsplit('.', 1)[0] + '_snaps.png', dpi=150, bbox_inches='tight')
