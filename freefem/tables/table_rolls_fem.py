"""steady rolls. Free slip: volume Nu on 32^2 (and 24^2 where available, with the h^4 extrapolation);
rigid: Nu (wall and volume) and kinetic energy, 32^2 and 48^2."""
from texfmt import finalize
import sys, os
R = os.environ.get('NSB_FF', '.') + '/rolls/'
def summ(f):
    if not os.path.exists(f): return None
    for l in open(f):
        if l.startswith('# SUMMARY'):
            v = l.split(': ')[1].split(); d = dict(Ek=float(v[5]), Nub=float(v[6]), Nut=float(v[7]), Qtmin=float(v[1]))
            d['Nuv'] = float(v[-1]) if 'Nu_vol' in l else None
            if d['Nuv'] is None and os.path.exists(f.replace('.txt', '_final.txt')):   # older log: Nu_vol from the saved final state
                d['Nuv'] = summ(f.replace('.txt', '_final.txt'))['Nuv']
            return d
rs = ['1.02', '1.05', '1.1', '1.2', '1.5', '2']
fs = []
for r in rs:
    a = summ(f'{R}fs_r{r}_N32.txt'); b = summ(f'{R}fs_r{r}.txt')
    if a is None: fs.append(None); continue
    eps = float(r) - 1; nu = a['Nuv']
    ext = nu + (nu - b['Nuv'])/((32/24)**4 - 1) if b else None
    fs.append((r, nu, (nu - 1)/eps, 2*(float(r) - 1)/float(r)/eps, ext, a['Nub']))
rg = []
for Ra in ['3000', '5000', '10000']:
    a = summ(f'{R}rg{Ra}_N32.txt'); b = summ(f'{R}rg{Ra}_N48.txt')
    rg.append((Ra, a, b))
for x in fs: print(x)
for x in rg: print(x)
rows = []
for i in range(6):
    f = fs[i]; left = f'${f[0]}$ & ${f[1]:.6f}$ & ${f[2]:.4f}$ & ${f[3]:.4f}$' if f else ' & & & '
    right = ' & & '
    if i < 3 and rg[i][1]:
        Ra, a, b = rg[i]; right = f'${Ra}$ & ${a["Nuv"]:.6f}$ & ${a["Ek"]:.4f}$'
    rows.append(left + ' & ' + right + r'\\')
out = r'''\begin{table}[htbp]
\centering
\caption{Steady rolls, $Pr=1$, Taylor--Hood elements on a $32\times32$ mesh, $Nu$ from the volume average
$1+\langle u_y\theta\rangle/(\kappa|T_c'|)$. Left: free-slip walls, $k=\pi/\sqrt2$, $Ra=rRa_c$, uniform mesh; the ratio
$(Nu-1)/\epsilon$ against the Lorenz value $2(r-1)/r/\epsilon$. Right: rigid walls, $k=3.117$, mesh graded towards the walls;
$Nu$ and the kinetic energy.}
\label{tab:rolls}
\footnotesize
\begin{tabular}{c c c c @{\hspace{2em}} c c c}
\toprule
\multicolumn{4}{c}{free slip} & \multicolumn{3}{c}{rigid}\\
\cmidrule(lr){1-4}\cmidrule(lr){5-7}
$r$ & $Nu$ & $(Nu-1)/\epsilon$ & $2(r-1)/r\ /\ \epsilon$ & $Ra$ & $Nu$ & $\frac12\|\vu\|^2$\\
\midrule
ROWS
\bottomrule
\end{tabular}
\end{table}
'''.replace('ROWS', '\n'.join(rows))
if len(sys.argv) > 1: open(sys.argv[1], 'w').write(finalize(out))
