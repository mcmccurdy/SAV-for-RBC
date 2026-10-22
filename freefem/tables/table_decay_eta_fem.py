"""energy decay without heating: max_n (X^{n+1}-X^n) over steps n>=3 and max kinetic energy.
eta sensitivity (Ra=5000, C=1: Nu(4) and min stored Q; decay: max dX)."""
from texfmt import finalize
import os, sys, numpy as np
B = os.environ.get('NSB_FF', '.') + '/'
def load(f):
    if not os.path.exists(f): return None
    rows = []; blow = False; summ = None
    for l in open(f):
        if l.startswith('# blow-up'): blow = True
        elif l.startswith('# SUMMARY'): summ = l.split(': ')[1].split()
        elif not l.startswith('#'): rows.append([float(x) for x in l.split()])
    if summ is None: return None
    return np.array(rows), blow, summ
def dX(f):
    r = load(f)
    if r is None: return None
    a = r[0]; n = a[:, 0]; X = a[:, 10]; m = n >= 3          # X^{n+1}-X^n for n>=3 (paper convention)
    d = np.diff(X)[m[:-1]]
    return d.max(), a[:, 4].max()
def e(x):
    m, k = f'{x:.2e}'.split('e'); return f'${m}{{\\times}}10^{{{int(k)}}}$'
rows = []
for dt in ['1e-2', '1e-3', '1e-4']:  # largest dt first
    c = []
    for A in ['5e5', '1']:
        r = dX(f'{B}decay/A{A}_dt{dt}.txt'); c += [e(r[0]), f'${r[1]:.3f}$'] if r else ['--', '--']
    m, k = dt.split('e'); rows.append(f'$10^{{{int(k)}}}$ & ' + ' & '.join(c) + r'\\')
print('\n'.join(rows))
t9 = r'''\begin{table}[htbp]
\centering
\caption{No differential heating ($T_b=T_t=T_{\rm ref}$), $G=3000$, rigid walls, relaxed scheme, Taylor--Hood elements on a
$32\times32$ mesh: largest one-step change of the energy $X^n$ of Theorem~\ref{thm:stab}(a) over $t\in[0,0.5]$ (steps $n\ge3$),
and the peak kinetic energy.}
\label{tab:decay}
\footnotesize
\begin{tabular}{r cc cc}
\toprule
& \multicolumn{2}{c}{$A=5\times10^5$ (theorem applies)} & \multicolumn{2}{c}{$A=1$}\\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
$\dt$ & $\max_n(X^{n+1}-X^n)$ & $\max_n\frac12\|\vu^n\|^2$ & $\max_n(X^{n+1}-X^n)$ & $\max_n\frac12\|\vu^n\|^2$\\
\midrule
ROWS
\bottomrule
\end{tabular}
\end{table}
'''.replace('ROWS', '\n'.join(rows))
etas = ['0', '1e-8', '1e-6', '1e-4', '1e-2', '0.5', '0.95', '0.99']
def nu4(f):
    r = load(f)
    if r is None: return None
    a, blow, s = r
    if blow: return 'blow-up', float(s[3])
    return f'{0.5*(float(s[6]) + float(s[7])):.6f}', float(s[3])
er = []
for eta in etas:
    c = []
    for dt in ['3e-3', '1e-3']:  # largest dt first
        f = f'{B}eta/C1_dt{dt}_eta{eta}.txt'
        if eta == '0.95': f = f'{B}dt/C1_rel_dt{dt}.txt'
        r = nu4(f) if os.path.exists(f) else None
        c += [r[0], ('$<10^{-2}$' if r[1] < 1e-2 else f'{r[1]:.4f}')] if r else ['--', '--']
    d = dX(f'{B}eta/decay_eta{eta}.txt'); c.append(e(d[0]) if d else '--')
    lab = eta if 'e' not in eta else '10^{%d}' % int(eta.split('e')[1])
    er.append(f'${lab}$ & ' + ' & '.join(c) + r'\\')
print('\n'.join(er))
t10 = r'''\begin{table}[htbp]
\centering
\caption{Sensitivity to the relaxation parameter $\eta$ (Taylor--Hood elements, $32\times32$ mesh). Left: rigid walls, $Ra=5000$,
$k=3.117$, $t\in[0,4]$, $C=1$ as in Table~\ref{tab:dt}: $Nu$ at $t=4$ (converged value $2.110511$ on this mesh) and the
smallest stored $Q^n$. Right: no differential heating, $A=1$, $\dt=10^{-2}$ as in Table~\ref{tab:decay}: largest one-step
change of $X^n$.}
\label{tab:eta}
\setlength{\tabcolsep}{3.5pt}\footnotesize
\begin{tabular}{c cc cc c}
\toprule
& \multicolumn{2}{c}{$\dt=3\cdot10^{-3}$} & \multicolumn{2}{c}{$\dt=10^{-3}$} & decay\\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-6}
$\eta$ & $Nu(4)$ & $\min Q^n$ & $Nu(4)$ & $\min Q^n$ & $\max_n(X^{n+1}-X^n)$\\
\midrule
ROWS
\bottomrule
\end{tabular}
\end{table}
'''.replace('ROWS', '\n'.join(er))
if len(sys.argv) > 2: open(sys.argv[1], 'w').write(finalize(t9)); open(sys.argv[2], 'w').write(finalize(t10))
