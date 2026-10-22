"""temporal errors of the manufactured solution against a same-mesh reference run.
Reads mms/cmp/{rT,rF,u}_<dt>.txt ("# REF" lines) and mms/u_N40_dt<dt>.txt ("# MMS" lines, |Q-1|)."""
from texfmt import finalize
import math, os, re, sys
dts = ['0.05', '0.025', '0.0125', '0.00625', '0.003125']
base = os.environ.get('NSB_FF', '.') + '/mms/'
def ref(run, dt):
    for l in open(f'{base}cmp/{run}_{dt}.txt'):
        if l.startswith('# REF'): return [float(v) for v in l.split(': ')[1].split()[1:]]
def q1(dt):
    for l in open(f'{base}u_N40_dt{dt}.txt'):
        if l.startswith('# MMS'): return float(l.split()[-1])
def floor():
    for l in open(f'{base}ref_N40.txt'):
        if l.startswith('# MMS'): return [float(v) for v in l.split(': ')[1].split()[4:7]]
def e(x):
    m, k = f'{x:.2e}'.split('e'); return f'${m}{{\\times}}10^{{{int(k)}}}$'
rows = []; prev = None
for dt in dts:  # largest dt first; the order on the row of dt compares dt with 2 dt
    r = ref('rT', dt); s = ref('rF', dt)[1]; q = q1(dt)
    cells = []
    for i in range(3):
        o = '--' if prev is None else f'{math.log2(prev[i]/r[i]):.2f}'
        cells += [e(r[i]), o]
    rows.append(f'{dt} & ' + ' & '.join(cells) + f' & {e(s)} & {e(q)}\\\\')
    prev = r
out = r'''\begin{table}[htbp]
\centering
\caption{Manufactured solution (Section~\ref{sec:mms}), Taylor--Hood elements on a $40\times40$ mesh: $L^2$ differences at
$t=0.5$ from a run with $\dt=1.953125\cdot10^{-4}$ on the same mesh, which isolate the error of the time
discretization, and observed orders, for the rotational scheme with relaxation. The next column is the pressure of the
standard incremental form, measured in the same way; the last is $|Q^N-1|$ without relaxation.}
\label{tab:mms}
\setlength{\tabcolsep}{2pt}\footnotesize
\begin{tabular}{r cc cc cc c c}
\toprule
& \multicolumn{6}{c}{rotational, relaxed} & standard & unrelaxed\\
\cmidrule(lr){2-7}\cmidrule(lr){8-8}\cmidrule(lr){9-9}
$\dt$ & $\vu$ & order & $p$ & order & $T$ & order & $p$ & $|Q^N-1|$\\
\midrule
ROWS
\bottomrule
\end{tabular}
\end{table}
'''
out = out.replace('ROWS', '\n'.join(rows))
open(sys.argv[1] if len(sys.argv) > 1 else 'table_mms.tex', 'w').write(finalize(out))
print(out)
