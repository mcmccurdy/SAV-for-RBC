"""steady rolls against Clever & Busse (1974), Table 1 (rigid, alpha = 3.117) and
Moore & Weiss (1973), Table 1 (free slip, Pr = 6.8). Nu = mean of the two walls at the end of the run; the volume
average is printed alongside as a check that the state is steady (they agree for a steady state). The tables report the volume average (less mesh dependent)."""
from texfmt import finalize
import os, sys
B = os.environ.get('NSB_FF', '.') + '/bench/'
CB = {0.71: {2000: 1.212, 2500: 1.475, 3000: 1.663, 5000: 2.116, 10000: 2.661, 20000: 3.258},
      7.0: {2000: 1.214, 2500: 1.478, 3000: 1.667, 5000: 2.112, 10000: 2.618, 20000: 3.119}}
MW = {1.1: (1.18, 1.16, '--'), 1.2: (1.34, 1.32, '--'), 1.4: (1.61, 1.58, '--'), 2: (2.14, 2.12, '2.14'),
      3: (2.68, 2.65, '--'), 4: (3.04, 3.01, '--'), 6: (3.55, 3.52, '--'), 10: (4.24, 4.19, '--')}


def summ(f):
    if not os.path.exists(f): return None
    rows = [l.split() for l in open(f) if not l.startswith('#')]
    for l in open(f):
        if l.startswith('# SUMMARY'):
            v = [float(x) for x in l.split(': ')[1].split()]
            if v[8] > 0: return dict(blow=True)
            # steadiness over the last quarter of the run (wall Nu at the bottom)
            t = [float(r[1]) for r in rows]; nb = [float(r[6]) for r in rows]; T = t[-1]
            late = [n for tt, n in zip(t, nb) if tt >= 0.75*T]
            return dict(blow=False, nu=0.5*(v[6] + v[7]), nuv=v[10], var=max(late) - min(late), qmin=v[1], qmax=v[2])
    return None


def pct(a, b): return f'${100*(a - b)/b:+.2f}\\%$'.replace('+', '+').replace('-', '-')


rows = []
for Ra in [2000, 3000, 5000, 10000]:
    c = [str(Ra)]
    for Pr in (0.71, 7.0):
        s = summ(f'{B}cb_a3.117_P{Pr}_R{Ra}.txt')
        if s is None or s.get('blow'): c += ['--', f'{CB[Pr][Ra]}', '--']; continue
        c += [f'{s["nuv"]:.4f}', f'{CB[Pr][Ra]}', pct(s['nuv'], CB[Pr][Ra])]
        print('CB', Pr, Ra, s)
    rows.append(' & '.join(c) + r'\\')
t5 = r'''\begin{table}[htbp]
\centering
\caption{Rigid walls, rolls of wave number $\alpha=3.117$: Nusselt number against Table~1 of Clever and Busse
\cite{CleverBusse1974} (CB), and the relative difference. Present values are steady states reached from
$\theta=0.1\sin(\pi y)\cos(\alpha x)$ with relaxation, on a $32\times32$ mesh graded towards the walls; $Nu$ is the volume
average of Section~\ref{sec:rolls}.}
\label{tab:cb}
\footnotesize
\begin{tabular}{r ccr ccr}
\toprule
& \multicolumn{3}{c}{$Pr=0.71$} & \multicolumn{3}{c}{$Pr=7$}\\
\cmidrule(lr){2-4}\cmidrule(lr){5-7}
$Ra$ & present & CB & diff. & present & CB & diff.\\
\midrule
ROWS
\bottomrule
\end{tabular}
\end{table}
'''.replace('ROWS', '\n'.join(rows))
rows = []
for r in [1.1, 1.2, 1.4, 2, 3, 4, 6, 10]:
    s = summ(f'{B}mw_r{r}.txt'); v, m1, m2 = MW[r]
    if s: print('MW', r, s)
    p = '--' if (s is None or s.get('blow')) else f'{s["nuv"]:.4f}'
    rows.append(f'{r} & {p} & {v} & {m1} & {m2}' + r'\\')
t6 = r'''\begin{table}[htbp]
\centering
\caption{Free-slip walls, $Pr=6.8$, cells of width $\sqrt2$ ($k=\pi/\sqrt2$), $Ra=rRa_c$: Nusselt number
against Table~1 of Moore and Weiss \cite{MooreWeiss1973}, which lists the values of Veronis and their
finite-difference values on two meshes. Present: volume average of $Nu$, $32\times32$ mesh ($48\times32$ for $r=10$).}
\label{tab:mw}
\footnotesize
\begin{tabular}{r c c c c}
\toprule
& & \multicolumn{3}{c}{Moore and Weiss, Table 1}\\
\cmidrule(lr){3-5}
$r$ & present & Veronis & $24\times18$ & $48\times34$\\
\midrule
ROWS
\bottomrule
\end{tabular}
\end{table}
'''.replace('ROWS', '\n'.join(rows))
if len(sys.argv) > 2: open(sys.argv[1], 'w').write(finalize(t5)); open(sys.argv[2], 'w').write(finalize(t6))
