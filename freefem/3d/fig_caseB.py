"""Figure for Case B (Section 6.10): three 3D renderings (render3d.py --level=0.12 --res=1800x1350 --crop=1) and the time series.
usage: python3 fig_caseB.py caseB.txt render_dir out.pdf [Nu2d]
render_dir holds c_100500.png, c_101500.png, c_103250.png (t = 1, 3, 6.5)."""
import sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
plt.rcParams.update({'font.size': 8.5, 'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm', 'axes.formatter.use_mathtext': True, 'axes.unicode_minus': False,
                     'axes.spines.top': False, 'axes.spines.right': False})
log, rdir, out = sys.argv[1:4]; nu2d = float(sys.argv[4]) if len(sys.argv) > 4 else None
rows = [l.split() for l in open(log) if l[0].isdigit()]
a = np.array([[float(x) for x in r] for r in rows if len(r) == 10])
t, Qt, Ek, Nub, Nut, Nuv, Ekz = a[:, 1], a[:, 2], a[:, 4], a[:, 6], a[:, 7], a[:, 8], a[:, 9]
c1, c2, ink = '#1f5fa8', '#c8553d', '#555555'
snaps = [('c_100500.png', 1.0, r'(a) $t=1$: rolls, wave vector $\frac{\pi}{2}(2,0)$'),
         ('c_101500.png', 3.0, r'(b) $t=3$: transition'),
         ('c_103250.png', 6.5, r'(c) $t=6.5$: steady rolls, $\frac{\pi}{2}(1,-1)$')]
fig = plt.figure(figsize=(7.2, 3.75))
gs = GridSpec(2, 3, figure=fig, height_ratios=[1.0, 1.0], hspace=0.38, wspace=0.3, left=0.085, right=0.99, top=0.94, bottom=0.11)
for i, (f, ts, title) in enumerate(snaps):
    ax = fig.add_subplot(gs[0, i]); ax.imshow(plt.imread(rdir + '/' + f)); ax.set_axis_off()
    ax.set_title(title, fontsize=8, pad=2)
axs = [fig.add_subplot(gs[1, i]) for i in range(3)]
axs[0].plot(t, Nub, color=c2, lw=0.9); axs[0].plot(t, Nuv, color=c1, lw=0.9)
axs[0].text(4.0, 1.66, 'walls', color=c2, fontsize=7); axs[0].text(4.0, 1.56, 'volume', color=c1, fontsize=7)
if nu2d:
    axs[0].axhline(nu2d, color=ink, lw=0.7, ls=':')
axs[0].set_ylim(0.95, 2.25); axs[0].set_ylabel('$Nu$'); axs[0].set_title('(d) Nusselt number', fontsize=8, loc='left')
axs[1].semilogy(t, Ek, color=c1, lw=0.9); axs[1].semilogy(t, np.maximum(Ekz, 1e-12), color=c2, lw=0.9)
axs[1].text(3.6, 2.2e3, r'$\frac{1}{2}\|\mathbf{u}\|^2$', color=c1, fontsize=8)
axs[1].text(3.6, 3e1, r'$\frac{1}{2}\|u_z\|^2$', color=c2, fontsize=8)
axs[1].set_ylim(1e-7, 2e4); axs[1].set_title('(e) kinetic energy', fontsize=8, loc='left')
axs[2].semilogy(t, np.maximum(np.abs(1 - Qt), 1e-13), color=c1, lw=0.9)
axs[2].set_ylim(1e-13, 1e-4); axs[2].set_title(r'(f) $|1-\tilde Q^n|$', fontsize=8, loc='left')
for ax in axs:
    ax.set_xlabel('$t$'); ax.set_xlim(0, t[-1]); ax.grid(True, color='#dddddd', lw=0.5)
    for f, ts, _ in snaps: ax.axvline(ts, color='0.6', lw=0.5, ls='--')
fig.savefig(out, dpi=300); print('wrote', out)
