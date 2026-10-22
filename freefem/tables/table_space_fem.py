"""spatial convergence of the manufactured solution (Appendix A). Reads space/sN_dt2.5e-4.txt,
lines '# MMS2 dt, exact-function errors L2 u T p, H1-seminorm u T, L2 div u'. Writes table_space.tex."""
from texfmt import finalize
import os, sys, numpy as np
B = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get('NSB_FF', '.'), 'space') + '/'
out = sys.argv[2] if len(sys.argv) > 2 else 'table_space.tex'
Ns, E = [], []
for N in (8, 16, 32, 64):
    f = f'{B}s{N}_dt2.5e-4.txt'
    if not os.path.exists(f): continue
    l = [x for x in open(f) if x.startswith('# MMS2')]
    if not l: continue
    v = [float(x) for x in l[0].split(': ')[1].split()]
    Ns.append(N); E.append(v[1:])          # L2u L2T L2p H1u H1T L2div
E = np.array(E)
def sci(v):
    m, e = ('%.2e' % v).split('e'); return r'$%s\cdot10^{%d}$' % (m, int(e))
cols = [(0, r'$\|\vu-\vu_h\|$', 3), (3, r'$|\vu-\vu_h|_{1}$', 2), (5, r'$\|\nabla\cdot\vu_h\|$', 2),
        (1, r'$\|T-T_h\|$', 3), (4, r'$|T-T_h|_{1}$', 2), (2, r'$\|p-p_h\|$', 2)]
L = [r'\begin{table}[htbp]\centering\small\setlength{\tabcolsep}{3pt}', r'\resizebox{\textwidth}{!}{\begin{tabular}{r' + 'll'*len(cols) + '}\\toprule',
     '$N$ & ' + ' & '.join(f'\\multicolumn{{2}}{{c}}{{{h}}}' for _, h, _ in cols) + r'\\',
     r'& ' + ' & '.join('error & order' for _ in cols) + r'\\\midrule']
for i, N in enumerate(Ns):
    row = [str(N)]
    for k, _, _ in cols:
        row.append(sci(E[i, k])); row.append('' if i == 0 else '%.2f' % np.log2(E[i - 1, k]/E[i, k]))
    L.append(' & '.join(row) + r'\\')
L.append(r'\midrule ' + ' & '.join(['expected'] + [x for _, _, o in cols for x in ('', str(o))]) + r'\\')
L += [r'\bottomrule\end{tabular}}',
      r'\caption{Spatial convergence of the Taylor--Hood discretization for the manufactured solution (\ref{app:mms}):'
      r' errors at $t=0.5$ on uniform $N\times N$ meshes with $\dt=2.5\cdot10^{-4}$, against the exact functions; $|\cdot|_1$ is the'
      r' $H^1$ seminorm, and the pressures are compared after removing their means. Orders from successive meshes. The'
      r' expected orders are those of $P_2$--$P_1$ elements for smooth solutions.}\label{tab:space}', r'\end{table}']
open(out, 'w').write(finalize('\n'.join(L) + '\n')); print('\n'.join(L))
