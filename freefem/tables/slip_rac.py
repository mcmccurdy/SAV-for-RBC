"""Rigid-wall check (Section 6.2): critical Rayleigh number at k = 3.1163 on the 32x32 graded mesh for slip
coefficients l/nu = 1e2 .. 1e6, from the growth rates of runs at Ra = 1650, 1700, 1750, 1800 (quadratic fit, zero),
as for the rigid-wall Ra_c. Run from the freefem folder: python3 tables/slip_rac.py"""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
from growth import growth
def rac(prefix):
    Ras = np.array([1650, 1700, 1750, 1800])
    s = np.array([growth(f'{prefix}_Ra{r}.txt') for r in Ras])
    r = np.roots(np.polyfit(Ras, s, 2)); r = r[(r.real > 1500) & (r.real < 1900)]
    return r[0].real
ref = rac('rigid2/N32')
for l in ['1e2', '1e3', '1e4', '1e5']:
    v = rac(f'slipcheck/l{l}'); print(f'l/nu = {l}: Ra_c = {v:.3f}, deficit from 1e6: {ref - v:.4f}')
print(f'l/nu = 1e6: Ra_c = {ref:.3f}')
