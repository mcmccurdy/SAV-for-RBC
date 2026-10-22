"""Figure 8 (Section 6.9): temperature (with a line-integral-convolution texture of the velocity) at Ra = 1e6 from the
uniform-grid snapshots of nsb.edp -snap N -snapu 1, and Nu(t) from the time series.
usage: python3 fig_ra1e6.py RUNDIR [OUTDIR]"""
import sys, os, glob, numpy as np, matplotlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import BLUE, RED, GOLD  # line colors shared by all plots
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import ListedColormap, Normalize
from scipy.ndimage import map_coordinates
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'render')); import render
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm', 'axes.formatter.use_mathtext': True, 'axes.unicode_minus': False, 'font.size': 8})
run = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else '.'
base = glob.glob(os.path.join(run, '*.txt'))[0]
def load(f):
    h = open(f).readline().split(); d = dict(zip(h[1::2], h[2::2]))
    nx, ny, L = int(d['nx=']), int(d['ny=']), float(d['L='])
    a = np.loadtxt(f, comments='#')
    return float(d['t=']), [a[:, k].reshape(ny + 1, nx + 1) for k in range(3)], L
def up(F, Nx, Ny):                        # cubic spline to Ny x Nx (x periodic: last column = first)
    ny1, nx1 = F.shape
    X = np.linspace(0, nx1 - 1, Nx, endpoint=False); Y = np.linspace(0, ny1 - 1, Ny)
    J, I = np.meshgrid(Y, X, indexing='ij')
    return map_coordinates(F[:, :-1], [J, I], order=3, mode='grid-wrap')
cm = plt.get_cmap('RdBu_r')                # the color map of the other temperature figures (Figures 1, 4, 9)
st, Nx, Ny = 0.3, 2000, 500
snaps = sorted(glob.glob(base + '.snap1*'))
times = [float(open(f).readline().split()[2]) for f in snaps]
pick = [snaps[int(np.argmin(np.abs(np.array(times) - tt)))] for tt in (0.009, 0.012, 0.03)]
fig = plt.figure(figsize=(6.5, 5.6))
gs = GridSpec(4, 1, figure=fig, height_ratios=[1, 1, 1, 1.25], hspace=0.18, left=0.08, right=0.9, top=0.99, bottom=0.07)
for i, f in enumerate(pick):
    t, (T, ux, uy), L = load(f)
    Ti, ui, vi = (up(F, Nx, Ny) for F in (T, ux, uy))
    tex = render.lic(ui, vi, length=max(18, Nx // 80))
    img = render.color(Ti, tex, cm, lic_strength=0.05, s=st)
    ax = fig.add_subplot(gs[i, 0]); ax.imshow(img, extent=[0, L, 0, 1], aspect='equal', interpolation='bilinear')
    ax.set_xticks(range(int(round(L)) + 1)); ax.set_yticks([0, 0.5, 1]); ax.set_ylabel('$y$', labelpad=2)
    ax.tick_params(length=2.5, labelsize=7)
    if i < 2: ax.set_xticklabels([])
    else: ax.set_xlabel('$x$', labelpad=1)
    ax.text(0.995, 0.96, f'$t={t:.4f}$', transform=ax.transAxes, ha='right', va='top', fontsize=8,
            color='w', bbox=dict(fc='k', alpha=0.45, lw=0, pad=1.5))
f_ = lambda T: np.clip(render.stretch(np.asarray(T, float), st), 0, 1)
# color bar on a linear scale in T: the color at T is cm(f_(T)), as in the images, so the ticks are equally
# spaced and the bar shows where the stretch changes the color fastest (near T = 1/2)
cmT = ListedColormap(cm(f_(np.linspace(0, 1, 512))))
cax = fig.add_axes([0.915, 0.42, 0.012, 0.54])
cb = fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0, 1), cmap=cmT), cax=cax, ticks=[0, 0.25, 0.5, 0.75, 1]); cb.set_label('$T$', labelpad=2); cax.tick_params(labelsize=7)
d = np.loadtxt(base, comments='#')
ax = fig.add_subplot(gs[3, 0])
ax.plot(d[:, 1], d[:, 6], color=RED, lw=0.8, label=r'$Nu$, bottom wall')
ax.plot(d[:, 1], d[:, 7], color=GOLD, lw=0.8, label=r'$Nu$, top wall')
ax.plot(d[:, 1], d[:, 8], color=BLUE, lw=0.8, label=r'$Nu$, volume')
for f in pick:
    ax.axvline(float(open(f).readline().split()[2]), color='0.6', lw=0.5, ls=':')
ax.set_xlim(0, d[-1, 1]); ax.set_ylim(0, None); ax.set_xlabel('$t$'); ax.set_ylabel('$Nu$')
ax.legend(fontsize=7, frameon=False, loc='upper right')
pos = ax.get_position(); ax.set_position([pos.x0 + 0.02, pos.y0 - 0.02, pos.width - 0.04, pos.height])
fig.savefig(os.path.join(out, 'fig_ra1e6.pdf'), dpi=300); fig.savefig(os.path.join(out, 'fig_ra1e6.png'), dpi=150)
print('wrote fig_ra1e6', [os.path.basename(p) for p in pick])
