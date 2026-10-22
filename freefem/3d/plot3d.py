"""Plots for nsb3d.edp runs.
usage: python3 plot3d.py run.txt            -> run_series.png (Nu, kinetic energy and its z part, Q~ against t)
                                               run_slices.png (T on the mid-plane y = H/2 for up to six slice files)
Needs numpy and matplotlib. Works on logs that were extended by restarts (-load)."""
import sys, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
f = sys.argv[1]; base = f.rsplit('.', 1)[0]
rows = [l.split() for l in open(f) if l[0].isdigit()]
a = np.array([[float(x) for x in r[:10]] for r in rows])
t, Qt, Ek, Nub, Nut, Nuv, Ekz = a[:, 1], a[:, 2], a[:, 4], a[:, 6], a[:, 7], a[:, 8], a[:, 9]
fig, ax = plt.subplots(3, 1, figsize=(7, 7), sharex=True)
ax[0].plot(t, Nub, label='Nu bottom'); ax[0].plot(t, Nut, label='Nu top'); ax[0].plot(t, Nuv, 'k', lw=.8, label='Nu volume')
ax[0].set_ylabel('Nu'); ax[0].legend(fontsize=8)
ax[1].semilogy(t, Ek, label='kinetic energy'); ax[1].semilogy(t, np.maximum(Ekz, 1e-300), label='z part')
ax[1].set_ylabel('kinetic energy'); ax[1].legend(fontsize=8)
ax[2].plot(t, 1 - Qt); ax[2].set_ylabel(r'$1-\tilde Q$'); ax[2].set_xlabel('t')
fig.tight_layout(); fig.savefig(base + '_series.png', dpi=130); print('wrote', base + '_series.png')
sl = sorted(glob.glob(f + '.slice1*'))
if sl:
    pick = [sl[int(i)] for i in np.linspace(0, len(sl) - 1, min(6, len(sl)))]
    n = len(pick); fig, ax = plt.subplots(1, n, figsize=(3*n, 3.2), squeeze=False)
    for axi, s in zip(ax[0], pick):
        h = open(s).readline().split(); d = dict(zip(h[1::2], h[2::2]))
        nx, nz, Lx, Lz = int(d['nx=']), int(d['nz=']), float(d['Lx=']), float(d['Lz='])
        T = np.loadtxt(s, comments='#')[:, 0].reshape(nz + 1, nx + 1)
        axi.imshow(T, origin='lower', extent=[0, Lx, 0, Lz], cmap='RdBu_r', vmin=0, vmax=1)
        axi.set_title(f"t = {float(d['t=']):.3g}", fontsize=9); axi.set_xlabel('x'); axi.set_ylabel('z')
    fig.suptitle('temperature on the mid-plane y = H/2', fontsize=10); fig.tight_layout()
    fig.savefig(base + '_slices.png', dpi=130); print('wrote', base + '_slices.png')
