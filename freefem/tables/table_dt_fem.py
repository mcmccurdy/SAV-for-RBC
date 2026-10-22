"""Ra=5000 rigid, 32^2, t in [0,4]: volume Nu at t=4 and the range of Q~ for C=1,100, relaxed/unrelaxed.
relative error of the kinetic energy at t=0.2 against dt/ref_t02.txt."""
from texfmt import finalize
import os, sys, numpy as np
D = os.environ.get('NSB_FF', '.') + '/dt/'
dts = ['1.6e-2', '1.2e-2', '8e-3', '6e-3', '4e-3', '3e-3', '2e-3', '1e-3', '5e-4']  # largest dt first
def lab(d):
    m, e = d.split('e'); return f'${m}\\cdot10^{{{int(e)}}}$' if m != '1' else f'$10^{{{int(e)}}}$'
def run(C, rel, dt):
    f = f'{D}C{C}_{"rel" if rel else "unrel"}_dt{dt}.txt'
    if not os.path.exists(f): return None
    s = None; blow = False; rows = []
    for l in open(f):
        if l.startswith('# blow-up'): blow = True
        elif l.startswith('# SUMMARY'): s = l.split(': ')[1].split()
        elif not l.startswith('#'): rows.append([float(x) for x in l.split()])
    if s is None: return None
    a = np.array(rows)
    return dict(blow=blow, qmin=float(s[1]), qmax=float(s[2]), Q_min=float(s[3]), nuv=float(s[-1]), nub=float(s[6]), a=a,
                steps=int(s[0]), nut=float(s[7]))
STAR = [False]
def cell(r):
    if r is None: return '\\multicolumn{2}{c}{--}'
    if r['blow'] or r['qmin'] < 1e-6: return 'blow-up & collapse'
    a = r['a']; late = a[a[:, 1] >= 3.0]; nu = 0.5*(late[:, 6] + late[:, 7])
    osc = (nu.max() - nu.min())/nu.mean()
    tag = '$^*$' if 1e-6 < osc < 1e-2 else ''
    STAR[0] |= bool(tag)
    if osc >= 1e-2: return f'unsteady$^\\dagger$ & ${r["qmin"]:.4f}$--${r["qmax"]:.4f}$'
    return f'${0.5*(r["nub"] + r["nut"]):.6f}${tag} & ${r["qmin"]:.4f}$--${r["qmax"]:.4f}$'
rows = []
for dt in dts:
    rows.append(lab(dt) + ' & ' + ' & '.join(cell(run(C, rel, dt)) for C in (1, 100) for rel in (True, False)) + r'\\')
print('\n'.join(rows))
t7 = r'''\begin{table}[htbp]
\centering
\caption{Rigid walls, $Ra=5000$, $k=3.117$, $t\in[0,4]$, Taylor--Hood elements on a $32\times32$ mesh graded towards the walls:
$Nu$ at $t=4$ (mean over the two walls) and the range of the computational scalar $\tilde Q^n$ over the run, for the weights $C=1$ and $C=100$ of the
$Q$ equation, with and without relaxation. The converged value on this mesh is $Nu=2.110511$. (The volume average of Section~\ref{sec:rolls} is not used here: without relaxation, the heat flux carries the factor $\tilde Q$.) With relaxation, the stored
$Q^n$ is $1$ at every step; without it, $Q^n=\tilde Q^n$. ``Blow-up'': $\frac12\|\vu\|^2>10^{10}$ (the run is stopped);
``collapse'': $\min_n\tilde Q^n<10^{-6}$. STARNOTE$^\dagger$$Nu$ oscillates by more than $1\%$ over $t\in[3,4]$.}
\label{tab:dt}
\footnotesize
\setlength{\tabcolsep}{2pt}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}r cc cc cc cc@{}}
\toprule
& \multicolumn{4}{c}{$C=1$} & \multicolumn{4}{c}{$C=100$}\\
\cmidrule(lr){2-5}\cmidrule(lr){6-9}
& \multicolumn{2}{c}{relaxed} & \multicolumn{2}{c}{unrelaxed} & \multicolumn{2}{c}{relaxed} & \multicolumn{2}{c}{unrelaxed}\\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}
$\dt$ & $Nu(4)$ & range of $\tilde Q^n$ & $Nu(4)$ & range of $\tilde Q^n$ & $Nu(4)$ & range of $\tilde Q^n$ & $Nu(4)$ & range of $\tilde Q^n$\\
\midrule
ROWS
\bottomrule
\end{tabular*}
\end{table}
'''.replace('ROWS', '\n'.join(rows)).replace('STARNOTE', r'$^*$Not yet steady at $t=4$; ' if STAR[0] else '')
# relative error of the kinetic energy at t = 0.2 (formation of the rolls)
def ek02(f):
    if not os.path.exists(f): return None
    for l in open(f):
        if l.startswith('# blow-up'): return np.inf
        if not l.startswith('#'):
            v = l.split()
            if abs(float(v[1]) - 0.2) < 1e-9: return float(v[4])
    return np.inf
ref = ek02(D + 'ref_t02.txt')
t8rows = []
if ref and np.isfinite(ref):
    prev = {}
    for dt in ['4e-3', '2e-3', '1e-3', '5e-4']:  # largest dt first
        cells = []
        for C in (1, 100):
            for rel in (True, False):
                e = ek02(f'{D}C{C}_{"rel" if rel else "unrel"}_dt{dt}.txt')
                if e is None: cells.append('--'); continue
                err = abs(e - ref)/ref if np.isfinite(e) else np.inf
                key = (C, rel)
                if not np.isfinite(err) or err > 1: cells.append('$>1$')
                else:
                    m, x = f'{err:.2e}'.split('e'); s = f'${m}{{\\times}}10^{{{int(x)}}}$'
                    if key in prev and np.isfinite(prev[key]) and prev[key] <= 1 and err > 0: s += f' $({prev[key]/err:.1f})$'
                    cells.append(s)
                prev[key] = err
        t8rows.append(lab(dt) + ' & ' + ' & '.join(cells) + r'\\')
    print('\n'.join(t8rows))
t8 = r'''\begin{table}[htbp]
\centering
\caption{Formation of the rolls in the run of Table~\ref{tab:dt}: relative error of $\frac12\|\vu\|^2$ at $t=0.2$, when the rolls saturate,
against a computation with $\dt=3.125\cdot10^{-5}$ and $C=100$ on the same mesh. In parentheses: ratio of the error at twice
the time step to this error ($4$ for second order).}
\label{tab:trans}
\footnotesize
\begin{tabular}{r cc cc}
\toprule
& \multicolumn{2}{c}{$C=1$} & \multicolumn{2}{c}{$C=100$}\\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
$\dt$ & relaxed & unrelaxed & relaxed & unrelaxed\\
\midrule
ROWS
\bottomrule
\end{tabular}
\end{table}
'''.replace('ROWS', '\n'.join(t8rows))
if len(sys.argv) > 2: open(sys.argv[1], 'w').write(finalize(t7)); open(sys.argv[2], 'w').write(finalize(t8))
