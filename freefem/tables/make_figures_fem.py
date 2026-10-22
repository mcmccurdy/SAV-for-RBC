"""Figures of the paper, from the FreeFem runs in $NSB_FF (default: the current folder).

usage: python3 make_figures_fem.py OUTDIR [names...]

fig_onset.pdf        growth rates near onset (free slip 32^2, dt = 0.005; rigid 48^2 graded, dt = 0.01, with the quadratic fit)
fig_convergence.pdf  (a) manufactured solution, time errors against a same-mesh reference; (b) the transient at Ra = 5000;
                     slope-2 triangles
fig_weightC.pdf      2x2: (a) Q~ during the formation of the rolls; (b) 1 - min Q~ against dt; a collapse of Q~ (C = 1):
                     (c) kinetic energy, (d) Q~ and the stored Q
fig_flows.pdf        temperature and streamlines: rigid rolls at Ra = 5000; free-slip cells, Pr = 6.8, r = 10
"""
import math, os, subprocess, sys, glob, tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import BLUE, RED, GOLD, INK, REF, C_COLOR

B = os.environ.get('NSB_FF', '.') + '/'
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
ONLY = sys.argv[2:]
plt.rcParams.update({'text.usetex': False, 'font.family': 'serif', 'mathtext.fontset': 'cm', 'axes.formatter.use_mathtext': True,
                     'font.serif': ['cmr10'], 'axes.unicode_minus': False,
                     'font.size': 9, 'axes.labelsize': 9, 'legend.fontsize': 7.5, 'xtick.labelsize': 8,
                     'ytick.labelsize': 8, 'lines.linewidth': 1.0, 'axes.linewidth': 0.6, 'legend.frameon': False,
                     'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02})
W = 6.5


def save(fig, name):
    fig.savefig(os.path.join(OUT, name)); plt.close(fig); print('wrote', name)


def slope(ax, x0, y0, x1, p, label):
    """slope triangle on log-log axes: hypotenuse of slope p from (x0, y0) to x1, right angle below it at (x1, y0);
    the label is set just above the hypotenuse by finish_slopes() once the layout is final"""
    y1 = y0*(x1/x0)**p
    ax.fill([x0, x1, x1], [y0, y0, y1], facecolor='0.92', edgecolor='k', lw=0.6, zorder=1)
    ax._slope = getattr(ax, '_slope', []) + [(x0, y0, x1, y1, label)]


def finish_slopes(fig):
    """write each triangle's label along its hypotenuse, rotated to the hypotenuse as drawn"""
    fig.canvas.draw()
    for ax in fig.axes:
        for x0, y0, x1, y1, label in getattr(ax, '_slope', []):
            (X0, Y0), (X1, Y1) = ax.transData.transform([(x0, y0), (x1, y1)])
            ang = math.degrees(math.atan2(Y1 - Y0, X1 - X0))
            xm, ym = math.sqrt(x0*x1), math.sqrt(y0*y1)
            n = (-math.sin(math.radians(ang)), math.cos(math.radians(ang)))
            ax.annotate(label, (xm, ym), xytext=(2*n[0], 2*n[1]), textcoords='offset points', rotation=ang,
                        rotation_mode='anchor', ha='center', va='bottom', fontsize=7.5)


def log(f):
    """numeric rows of an nsb.edp log, the SUMMARY fields and whether it blew up"""
    rows, summ, blow = [], None, False
    for l in open(f):
        if l.startswith('# SUMMARY'): summ = [float(v) for v in l.split(': ')[1].split()]
        elif l.startswith('# blow-up'): blow = True
        elif not l.startswith('#'): rows.append([float(v) for v in l.split()])
    n = max(len(r) for r in rows); rows = [r for r in rows if len(r) == n]      # drop a truncated last line
    return np.array(rows), summ, blow


def sigma(f, t0=1., t1=2.):
    a = log(f)[0]; t, e = a[:, 1], a[:, 4]; m = (t >= t0 - 1e-9) & (t <= t1 + 1e-9)
    return 0.5*np.polyfit(t[m], np.log(e[m]), 1)[0]


def fig_onset():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 2.2))
    k = math.pi/math.sqrt(2); K = math.sqrt(k*k + math.pi**2)
    Ra = np.linspace(450, 1050, 200)
    a1.plot(Ra, k*np.sqrt(Ra)/K - K*K, 'k-', lw=0.8, label='exact')
    Rs = [500, 600, 650, 660, 700, 800, 1000]
    a1.plot(Rs, [sigma(f'{B}onset2/N32_Ra{r}_dt0.005.txt') for r in Rs], 'o', ms=4, mfc='none', color=BLUE,
            label=r'computed, $32\times32$, $\delta t=0.005$')
    a1.axhline(0, color='k', lw=0.4); a1.axvline(27*math.pi**4/4, color='k', lw=0.4, ls=':')
    a1.text(27*math.pi**4/4 + 8, -1.3, r'$27\pi^4/4$', fontsize=7.5)
    a1.set_xlabel('$Ra$'); a1.set_ylabel(r'growth rate $\sigma$'); a1.legend(loc='upper left')
    a1.set_title(r'(a) free slip, $k=\pi/\sqrt{2}$', fontsize=9)
    Rs = [1650, 1700, 1710, 1750, 1800]; s = [sigma(f'{B}rigid2/N48_Ra{r}.txt') for r in Rs]
    c = np.polyfit(Rs, s, 2); x = np.linspace(1630, 1820, 100)
    a2.plot(x, np.polyval(c, x), 'k-', lw=0.8, label='quadratic fit')
    a2.plot(Rs, s, 's', ms=4, mfc='none', color=BLUE, label=r'computed, $48\times48$, $\delta t=0.01$')
    a2.axhline(0, color='k', lw=0.4); a2.axvline(1707.76, color='k', lw=0.4, ls=':')
    a2.text(1709, min(s)*0.8, r'$1707.76$', fontsize=7.5)
    a2.set_xlabel('$Ra$'); a2.set_ylabel(r'growth rate $\sigma$'); a2.legend(loc='upper left')
    a2.set_title(r'(b) rigid, $k=3.1163$', fontsize=9)
    fig.tight_layout(w_pad=2)
    save(fig, 'fig_onset.pdf')


def ref_diff(run, dt):
    for l in open(f'{B}mms/cmp/{run}_{dt}.txt'):
        if l.startswith('# REF'): return [float(v) for v in l.split(': ')[1].split()]


def ek_at(f, tt=0.2):
    a, s, blow = log(f)
    m = np.abs(a[:, 1] - tt) < 1e-9
    return a[m, 4][0] if m.any() else np.inf


def fig_convergence():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 2.3))
    dts = ['0.05', '0.025', '0.0125', '0.00625', '0.003125', '0.0015625']
    rT = np.array([ref_diff('rT', d) for d in dts]); rF = np.array([ref_diff('rF', d) for d in dts])
    dt = rT[:, 0]
    for k, lab, mk, c in ((1, r'$\mathbf{u}$', 'o', BLUE), (2, '$p$', 's', RED), (3, '$T$', '^', GOLD)):
        a1.loglog(dt, rT[:, k], mk + '-', color=c, ms=3.5, label=lab + ', rotational')
    a1.loglog(dt, rF[:, 2], 's--', ms=3.5, mfc='none', color=RED, label='$p$, standard')
    slope(a1, dt[-1], rT[-1, 3]*0.12, dt[-3], 2, '2')
    a1.set_xlabel(r'$\delta t$'); a1.set_ylabel(r'$L^2$ error at $t=0.5$')
    a1.set_title('(a) manufactured solution', fontsize=9); a1.legend(loc='lower right')
    e0 = ek_at(f'{B}dt/ref_t02.txt')
    sty = {(1, 'rel'): (RED, 'o-', r'$C=1$, relaxed'), (1, 'unrel'): (RED, 'o--', r'$C=1$, unrelaxed'),
           (100, 'rel'): (BLUE, 's-', r'$C=100$, relaxed'), (100, 'unrel'): (BLUE, 's--', r'$C=100$, unrelaxed')}
    for (C, rl), (c, mk, lab) in sty.items():
        x, y = [], []
        for s in ['5e-4', '1e-3', '2e-3', '4e-3']:
            f = f'{B}dt/C{C}_{rl}_dt{s}.txt'
            if not os.path.exists(f): continue
            err = abs(ek_at(f) - e0)/e0
            if np.isfinite(err) and err < 1: x.append(float(s)); y.append(err)
        if x: a2.loglog(x, y, mk, color=c, ms=3.5, mfc='none' if rl == 'unrel' else c, label=lab)
    slope(a2, 5e-4, 6e-6, 1.25e-3, 2, '2')
    a2.set_xlabel(r'$\delta t$'); a2.set_ylabel(r'relative error of $\frac{1}{2}\|\mathbf{u}\|^2$ at $t=0.2$')
    a2.set_title(r'(b) transient, $Ra=5000$', fontsize=9); a2.legend(loc='lower right', fontsize=6.5)
    a2.set_ylim(3e-6, 3); a2.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    fig.tight_layout(w_pad=2)
    finish_slopes(fig)
    save(fig, 'fig_convergence.pdf')


def fig_weightC():
    fig, ((a1, a2), (a3, a4)) = plt.subplots(2, 2, figsize=(W, 4.3))
    for C, s, c, ls in ((1, '1e-3', RED, ':'), (1, '2e-3', RED, '--'), (1, '3e-3', RED, '-'),
                        (100, '3e-3', BLUE, '-'), (100, '6e-3', BLUE, '--')):
        f = f'{B}dt/C{C}_rel_dt{s}.txt'
        if not os.path.exists(f): continue
        d = log(f)[0]; m = d[:, 1] <= 0.6
        a1.plot(d[m, 1], d[m, 2], ls, color=c, label=f'${C}$, ${float(s)*1e3:g}$')
    a1.axhline(1, color='k', lw=0.4)
    a1.set_xlabel('$t$'); a1.set_ylabel(r'$\tilde Q^n$'); a1.set_ylim(0.5, 1.22)
    a1.set_title(r'(a) $\tilde Q^n$ (stored $Q^n=1$)', fontsize=9)
    a1.legend(loc='lower right', fontsize=6.2, ncol=2, columnspacing=0.8, handlelength=1.6,
              title=r'$C$, $\delta t/10^{-3}$', title_fontsize=6.2)
    for C, c, mk in ((1, RED, 'o'), (100, BLUE, 's'), ('1e4', GOLD, '^')):
        x, y = [], []
        for s in ['5e-4', '1e-3', '2e-3', '3e-3', '4e-3', '6e-3', '8e-3']:
            f = f'{B}dt/C{C}_rel_dt{s}.txt'
            if not os.path.exists(f): continue
            a, summ, blow = log(f)
            if summ is None or blow or summ[1] < 1e-6: continue
            x.append(float(s)); y.append(1 - summ[1])
        a2.loglog(x, y, mk + '-', color=c, ms=3.5)
        if x:  # label each line at its last point, so no legend covers the data
            a2.annotate('$C=10^4$' if C == '1e4' else f'$C={C}$', (x[-1], y[-1]), xytext=(4, -1),
                        textcoords='offset points', ha='left', va='center', color=c, fontsize=7.5)
    slope(a2, 1e-3, 8e-6, 2.5e-3, 3, '3')
    a2.set_xlim(4e-4, 1.6e-2)
    a2.set_xticks([5e-4, 1e-3, 2e-3, 4e-3, 8e-3])
    a2.set_xticklabels([r'$5\cdot10^{-4}$', r'$10^{-3}$', r'$2\cdot10^{-3}$', r'$4\cdot10^{-3}$', r'$8\cdot10^{-3}$'], fontsize=7)
    a2.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    a2.set_xlabel(r'$\delta t$'); a2.set_ylabel(r'$1-\min_n\tilde Q^n$')
    a2.set_title('(b) deviation of $\\tilde Q$', fontsize=9)
    f = f'{B}dt/C1_rel_dt4e-3.txt'
    if os.path.exists(f):
        d = log(f)[0]; m = np.isfinite(d[:, 4]) & (d[:, 4] > 0); tmax = d[m, 1].max()
        a3.semilogy(d[m, 1], d[m, 4], 'k-')
        a3.set_xlabel('$t$'); a3.set_ylabel(r'$\frac{1}{2}\|\mathbf{u}\|^2$'); a3.set_xlim(0, tmax)
        a4.plot(d[m, 1], np.clip(d[m, 2], -0.1, 1.3), '-', color=RED, lw=1.0, label=r'$\tilde Q^n$')
        a4.plot(d[m, 1], d[m, 3], '--', color=INK, lw=1.0, label='stored $Q^n$')
        a4.axhline(0, color='k', lw=0.4)
        a4.set_ylim(-0.1, 1.2); a4.set_xlim(0, tmax); a4.set_xlabel('$t$'); a4.set_ylabel('$Q$')
        a4.legend(loc='center right')
    a3.set_title(r'(c) kinetic energy, $C=1$, $\delta t=4\cdot10^{-3}$', fontsize=9)
    a4.set_title(r'(d) $\tilde Q^n$ and stored $Q^n$, same run', fontsize=9)
    fig.tight_layout(w_pad=1.5, h_pad=1.2)
    finish_slopes(fig)
    save(fig, 'fig_weightC.pdf')


def snapshot(args, dat, name, snx, sny):
    """one step from a saved steady state, writing T, u_x, u_y on a uniform grid"""
    out = os.path.join(tempfile.mkdtemp(prefix='nsbfig_'), f'{name}.txt')
    cmd = f'FreeFem++-nw {B}nsb.edp {args} -tend {args.split("-dt ")[1].split()[0]} -init {dat} -snap 1 -snapu 1 ' \
          f'-snx {snx} -sny {sny} -out {out}'
    subprocess.run(cmd, shell=True, cwd=B, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    f = out + '.snap10000'
    h = open(f).readline().split(); L = float(h[h.index('L=') + 1])
    a = np.loadtxt(f, comments='#').reshape(sny + 1, snx + 1, 3)
    T, ux = a[..., 0], a[..., 1]
    y = np.linspace(0, 1, sny + 1)
    psi = np.concatenate([np.zeros((1, snx + 1)), np.cumsum(0.5*(ux[1:] + ux[:-1])*np.diff(y)[:, None], axis=0)])
    return np.linspace(0, L, snx + 1), y, T, psi, L


def draw(ax, x, y, T, P, L, title, nlev=10, ylabel=True):
    im = ax.imshow(T, origin='lower', extent=[0, L, 0, 1], cmap='RdBu_r', vmin=0, vmax=1, interpolation='bilinear')
    m = np.abs(P).max(); lev = (np.arange(nlev) + 0.5)/nlev*m
    ax.contour(x, y, P, levels=lev, colors='k', linewidths=0.35)
    ax.contour(x, y, P, levels=-lev[::-1], colors='k', linewidths=0.35, linestyles='dashed')
    ax.set_xticks([0, L/2, L]); ax.set_xticklabels(['$0$', f'${L/2:.2f}$', f'${L:.2f}$'])
    ax.set_yticks([0, 0.5, 1]); ax.set_yticklabels(['$0$', '$0.5$', '$1$'])
    ax.set_xlabel('$x$', labelpad=1)
    if ylabel: ax.set_ylabel('$y$', labelpad=1)
    ax.tick_params(length=2.5, pad=2)
    ax.set_title(title, fontsize=8, pad=3)
    return im


def fig_flows():
    panels = [('-Ra 5000 -k 3.117 -l 1e6 -gy 0 -C 100 -nx 32 -ny 32 -dt 2e-3', B + 'rolls/rg5000_N32.dat', 'flow_a',
               r'(a) rigid, $Ra=5000$, $Pr=1$'),
              ('-kap 1 -nu 6.8 -G 44710.77278460711 -k 2.221441469079183 -l 0 -nx 48 -ny 32 -C 1000 -dt 0.001',
               B + 'bench/mw_r10.dat', 'flow_b', r'(b) free slip, $Pr=6.8$, $Ra=10\,Ra_c$')]
    panels = [p for p in panels if os.path.exists(p[1])]
    fig, axs = plt.subplots(1, len(panels), figsize=(W, 2.15), layout='constrained')
    axs = np.atleast_1d(axs)
    for i, (ax, (args, dat, name, title)) in enumerate(zip(axs, panels)):
        x, y, T, P, L = snapshot(args, dat, name, int(160*2.1), 160)
        im = draw(ax, x, y, T, P, L, title, ylabel=(i == 0))
    cb = fig.colorbar(im, ax=list(axs), shrink=0.8, aspect=14, pad=0.015, ticks=[0, 0.25, 0.5, 0.75, 1])
    cb.set_label('$T$', rotation=0, labelpad=6); cb.ax.tick_params(length=2.5, labelsize=7.5); cb.outline.set_linewidth(0.5)
    save(fig, 'fig_flows.pdf')


def fig_bench():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    argv = sys.argv; sys.argv = argv[:1]
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        from table_bench_fem import CB, MW, summ
    sys.argv = argv
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 2.3))
    for Pr, c, mk in ((0.71, BLUE, 'o'), (7.0, RED, 's')):
        R = [2000, 3000, 5000, 10000]; a1.plot(R, [CB[Pr][r] for r in R], mk, color=c, mfc='none', ms=4.5, label=f'CB, $Pr={Pr:g}$')
        x, y = [], []
        for r in [2000, 3000, 5000, 10000]:
            d = summ(f'{B}bench/cb_a3.117_P{Pr}_R{r}.txt')
            if d and not d.get('blow'): x.append(r); y.append(d['nuv'])
        a1.plot(x, y, '-', color=c, lw=0.9, marker=mk, ms=2.5, label=f'present, $Pr={Pr:g}$')
    a1.set_xscale('log'); a1.set_xlabel('$Ra$'); a1.set_ylabel('$Nu$'); a1.legend(loc='upper left', fontsize=6.5)
    a1.set_title(r'(a) rigid walls, $\alpha=3.117$', fontsize=9)
    rs = sorted(MW); a2.plot(rs, [MW[r][0] for r in rs], 'o', color=REF, mfc='none', ms=4.5, label='Veronis')
    a2.plot(rs, [MW[r][1] for r in rs], 'x', color='k', ms=4, label=r'MW, $24\times18$')
    x, y = [], []
    for r in rs:
        d = summ(f'{B}bench/mw_r{r}.txt')
        if d and not d.get('blow'): x.append(r); y.append(d['nuv'])
    a2.plot(x, y, '-', color=BLUE, lw=0.9, marker='.', ms=3, label='present')
    a2.set_xscale('log'); a2.set_xlabel('$r=Ra/Ra_c$'); a2.set_ylabel('$Nu$'); a2.legend(loc='upper left', fontsize=6.5)
    a2.set_title(r'(b) free slip, $Pr=6.8$', fontsize=9)
    fig.tight_layout(w_pad=2)
    save(fig, 'fig_bench.pdf')


for name, fn in [('onset', fig_onset), ('convergence', fig_convergence), ('weightC', fig_weightC), ('flows', fig_flows), ('bench', fig_bench)]:
    if not ONLY or name in ONLY:
        try: fn()
        except Exception as ex: print('skipped', name, ':', ex)
