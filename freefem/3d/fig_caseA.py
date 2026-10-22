"""Figure for Case A (Section 6.10): usage python3 fig_caseA.py caseA.txt fig_caseA.pdf"""
import sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm', 'axes.formatter.use_mathtext': True, 'axes.unicode_minus': False, 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
a = np.loadtxt(sys.argv[1]); t, Qt, Ek, Nub, Nuv, Ekz = a[:, 1], a[:, 2], a[:, 4], a[:, 6], a[:, 8], a[:, 9]
c1, c2, ink = '#1f5fa8', '#c8553d', '#555555'
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.4))
ax[0].plot(t, Nub, color=c2, lw=1.2); ax[0].plot(t, Nuv, color=c1, lw=1.2)
ax[0].axhline(2.1103, color=ink, lw=0.8, ls=':')
ax[0].text(0.98, 2.1103 + 0.01, '2D, $32^2$', ha='right', va='bottom', fontsize=7, color=ink)
ax[0].text(0.20, 1.62, 'volume', color=c1, fontsize=7); ax[0].text(0.20, 1.40, 'walls', color=c2, fontsize=7)
ax[0].set_ylim(0.95, 2.35); ax[0].set_ylabel('$Nu$'); ax[0].set_title('(a) Nusselt number', fontsize=9, loc='left')
ax[1].semilogy(t, Ek, color=c1, lw=1.2); ax[1].semilogy(t, np.maximum(Ekz, 1e-16), color=c2, lw=1.2)
ax[1].text(0.55, 700, r'$\frac{1}{2}\|\mathbf{u}\|^2$', color=c1, fontsize=8)
ax[1].text(0.45, 1e-5, r'$\frac{1}{2}\|u_z\|^2$', color=c2, fontsize=8)
ax[1].set_ylim(1e-14, 1e4); ax[1].set_title('(b) kinetic energy', fontsize=9, loc='left')
ax[2].semilogy(t, np.maximum(np.abs(1 - Qt), 1e-14), color=c1, lw=1.2)
ax[2].set_ylim(1e-14, 1e-3); ax[2].set_title(r'(c) $|1-\tilde Q^n|$', fontsize=9, loc='left')
for x in ax: x.set_xlabel('$t$'); x.set_xlim(0, 1); x.grid(True, color='#dddddd', lw=0.5)
fig.tight_layout(); fig.savefig(sys.argv[2]); print('wrote', sys.argv[2])
