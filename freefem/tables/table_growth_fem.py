"""free-slip growth-rate errors on 32^2 (orders from successive differences), Ra_c from 48^2 at dt=0.005,
and rigid Ra_c from rigid2/ (24^2, 32^2, 48^2)."""
from texfmt import finalize
import numpy as np, sys, os
O = os.environ.get('NSB_FF', '.') + '/onset2/'; RG = os.environ.get('NSB_FF', '.') + '/rigid2/'
k = np.pi/np.sqrt(2); K = np.sqrt(k*k + np.pi**2)
ex = lambda Ra: k*np.sqrt(Ra)/K - K*K
def sig(f, t0=1., t1=2.):
    a = np.loadtxt(f); t, e = a[:, 1], a[:, 4]; m = (t >= t0 - 1e-9) & (t <= t1 + 1e-9)
    return 0.5*np.polyfit(t[m], np.log(e[m]), 1)[0]
Ras = [500, 600, 650, 660, 700, 800, 1000]; dts = ['0.04', '0.02', '0.01', '0.005']
def e(x):
    m, kk = f'{x:.2e}'.split('e'); return f'${m}{{\\times}}10^{{{int(kk)}}}$'
rows = []
for Ra in Ras:
    fs = [f'{O}N32_Ra{Ra}_dt{d}.txt' for d in dts]
    if not all(os.path.exists(f) for f in fs): continue
    s = [sig(f) for f in fs]; err = [x - ex(Ra) for x in s]
    d = [s[i] - s[i+1] for i in range(3)]; ords = [np.log2(abs(d[i]/d[i+1])) for i in range(2)]
    rows.append(f'{Ra} & ${ex(Ra):.5f}$ & ' + ' & '.join(e(x) for x in err) + ' & ' + ', '.join(f'{o:.2f}' for o in ords) + r'\\')  # largest dt first
    print(Ra, err, ords)
def rac(files, Ras):
    s = [sig(f) for f in files]; c = np.polyfit(Ras, s, 2); r = np.roots(c).real
    return r[np.argmin(abs(r - np.mean(Ras)))]
fsR = [600, 650, 660, 700]; f48 = [f'{O}N48_Ra{R}_dt0.005.txt' for R in fsR]
racfs = rac(f48, fsR) if all(os.path.exists(f) for f in f48) else None
rgR = [1650, 1700, 1750, 1800]
racrg = {N: rac([f'{RG}N{N}_Ra{R}.txt' for R in rgR], rgR) for N in (24, 32, 48)}
print('Ra_c free slip 48^2:', racfs, ' rigid:', racrg)
out = r'''\begin{table}[htbp]
\centering
\caption{Onset with free-slip walls ($l=0$, $k=\pi/\sqrt2$, Taylor--Hood elements on a $32\times32$ mesh): error of the
computed growth rate, $\frac12\frac{d}{dt}\ln\|\vu\|^2$ fitted on $t\in[1,2]$, against the exact value $\sigma=k\sqrt{Ra}/K-K^2$,
and orders in $\dt$ from successive differences $\sigma(\dt)-\sigma(\dt/2)$, which cancel the spatial error.}
\label{tab:growth}
\setlength{\tabcolsep}{3pt}\footnotesize
\begin{tabular}{r r cccc c}
\toprule
$Ra$ & exact $\sigma$ & $\dt=0.04$ & $0.02$ & $0.01$ & $0.005$ & orders\\
\midrule
ROWS
\bottomrule
\end{tabular}
\end{table}
'''.replace('ROWS', '\n'.join(rows))
if len(sys.argv) > 2 and rows:
    open(sys.argv[1], 'w').write(finalize(out))
    open(sys.argv[2], 'w').write('\\newcommand{\\RacFS}{%.3f}\n\\newcommand{\\RacRG}{%.2f}\n' % (racfs, racrg[48]))
