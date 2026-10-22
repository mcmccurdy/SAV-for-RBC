"""Scaling of the deviation of the computational scalar with E/C (Section 6.5, Figure 7; runs of jobs_scaling.txt).

usage: python3 post_scaling.py [OUTDIR]   (run from this folder; reads scaling/*.txt)

For each run: d = max_n |Q~^n - 1| (from the # SUMMARY line), E = largest kinetic energy of the run.
Writes fig_scaling.pdf:
  (a) d against dt, for every Rayleigh number and C = 1, 100;
  (b) (C/E) d against (dt/tau)^3 with the advective time tau = H/U, U = sqrt(2E/|Omega|),
and prints the least-squares fit  log d = a log dt + b log C + c log E + const  over the runs in which Q~ did not collapse.
The argument of Section 3 predicts a = 3, b = -1 and, with tau = H/U ~ E^(-1/2), c = 1 + 3/2 = 2.5.
"""
import glob, math, os, re, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tables'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import ORDER, REF  # line colors shared by all plots

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
plt.rcParams.update({'text.usetex': False, 'font.family': 'serif', 'mathtext.fontset': 'cm', 'axes.formatter.use_mathtext': True,
                     'font.serif': ['cmr10'], 'axes.unicode_minus': False,
                     'font.size': 9, 'axes.labelsize': 9, 'legend.fontsize': 7.5, 'xtick.labelsize': 8,
                     'ytick.labelsize': 8, 'lines.linewidth': 1.0, 'axes.linewidth': 0.6, 'legend.frameon': False,
                     'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02})
W = 6.5
H = 1.0
L = 2*math.pi/3.117
DMAX = 0.1  # runs with a larger deviation (or a blow-up) are outside the asymptotic regime


def read(f):
    head = open(f).readline()
    r = {k: float(v) for k, v in re.findall(r'(Ra|dt|C)=([0-9.eE+-]+)', head)}
    ek = []
    s = None
    for line in open(f):
        if line.startswith('# SUMMARY'):
            s = line.split(':')[1].split()
        elif not line.startswith('#') and line.strip():
            ek.append(float(line.split()[4]))
    if s is None or not ek:
        return None
    qmin, qmax, blow = float(s[1]), float(s[2]), int(s[8])
    r['d'] = max(1 - qmin, qmax - 1)
    r['E'] = max(ek)
    r['ok'] = blow < 0 and r['d'] < DMAX and math.isfinite(r['d'])
    return r


runs = [r for r in (read(f) for f in sorted(glob.glob('scaling/Ra*_C*_dt*.txt'))) if r]
if not runs:
    sys.exit('no finished runs in scaling/')
ok = [r for r in runs if r['ok']]

print(f'{len(runs)} runs, {len(ok)} in the asymptotic regime (no blow-up, d < {DMAX})')
print(f'{"Ra":>6} {"C":>5} {"dt":>8} {"E":>9} {"max|Q~-1|":>11}  (C/E)d/(dt/tau)^3')
for r in sorted(runs, key=lambda r: (r['Ra'], r['C'], r['dt'])):
    tau = H/math.sqrt(2*r['E']/(L*H))
    x = (r['dt']/tau)**3
    note = '' if r['ok'] else '   collapsed or blew up'
    print(f'{r["Ra"]:6.0f} {r["C"]:5.0f} {r["dt"]:8.2e} {r["E"]:9.2f} {r["d"]:11.3e}  {r["C"]/r["E"]*r["d"]/x:9.3e}{note}')

names = ['dt', 'C', 'E']
cols = [k for k in names if max(r[k] for r in ok) > 1.5*min(r[k] for r in ok)]  # fit only what varies
X = np.array([[math.log(r[k]) for k in cols] + [1.0] for r in ok])
y = np.array([math.log(r['d']) for r in ok])
coef, res, *_ = np.linalg.lstsq(X, y, rcond=None)
pred = X @ coef
rms = float(np.sqrt(np.mean((y - pred)**2)))
print('\nfit  d ~ ' + ' '.join(f'{k}^{c:.2f}' for k, c in zip(cols, coef)) + f'   (rms of log residual {rms:.2f}, i.e. factor {math.exp(rms):.2f})')
print('prediction  dt^3 C^-1 E^2.5 (with tau = H/U)')

# figure
Ras = sorted({r['Ra'] for r in runs})
col = {Ra: ORDER[i % len(ORDER)] for i, Ra in enumerate(Ras)}
mk = {1.0: 'o', 100.0: 's'}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 2.5))
for Ra in Ras:
    for C in (1.0, 100.0):
        good = sorted([r for r in runs if r['Ra'] == Ra and r['C'] == C and r['ok']], key=lambda r: r['dt'])
        if good:
            a1.loglog([r['dt'] for r in good], [r['d'] for r in good], '-', marker=mk[C], ms=3.5, color=col[Ra],
                      mfc=col[Ra] if C == 100 else 'white')
            xs = [(r['dt']*math.sqrt(2*r['E']/(L*H))/H)**3 for r in good]
            ys = [r['C']/r['E']*r['d'] for r in good]
            a2.loglog(xs, ys, marker=mk[C], ls='none', ms=3.5, color=col[Ra], mfc=col[Ra] if C == 100 else 'white')
# reference line y = K x, K = median of the ratio over the runs with E > 100
K = float(np.median([r['C']/r['E']*r['d']/((r['dt']*math.sqrt(2*r['E']/(L*H))/H)**3) for r in ok if r['E'] > 100]))
x0, x1 = a2.get_xlim()
a2.plot([x0, x1], [K*x0, K*x1], '--', color=REF, lw=0.7, zorder=0)
a2.set_xlim(x0, x1)
a1.set_xticks([2.5e-4, 5e-4, 1e-3, 2e-3])
a1.set_xticklabels([r'$2.5\cdot10^{-4}$', r'$5\cdot10^{-4}$', r'$10^{-3}$', r'$2\cdot10^{-3}$'])
a1.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
a1.set_xlabel(r'$\delta t$')
a1.set_ylabel(r'$\max_n|\tilde Q^n-1|$')
a1.set_title('(a)', fontsize=9)
a2.set_xlabel(r'$(\delta t/\tau)^3$, with $\tau=H/U$ and $U=\sqrt{2E/|\Omega|}$')
a2.set_ylabel(r'$(C/E)\,\max_n|\tilde Q^n-1|$')
a2.set_title('(b)', fontsize=9)
handles = []
for Ra in Ras:
    E = float(np.median([r['E'] for r in ok if r['Ra'] == Ra]))
    handles.append(plt.Line2D([], [], color=col[Ra], marker='s', ms=3.5, label=f'$Ra={Ra:.0f}$, $E\\approx{E:.0f}$'))
handles.append(plt.Line2D([], [], color='k', marker='o', mfc='white', ls='none', ms=3.5, label='$C=1$'))
handles.append(plt.Line2D([], [], color='k', marker='s', ls='none', ms=3.5, label='$C=100$'))
handles.append(plt.Line2D([], [], color=REF, ls='--', lw=0.7, label=f'slope 1 ($K={K:.0f}$)'))
fig.tight_layout(rect=(0, 0.13, 1, 1))
fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=6.8, bbox_to_anchor=(0.5, 0.0))
fig.savefig(os.path.join(OUT, 'fig_scaling.pdf'))
print('wrote', os.path.join(OUT, 'fig_scaling.pdf'), ' K =', K)
