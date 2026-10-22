import sys, numpy as np
from growth import growth, exact
paper = {500:[-9.28e-2,-2.06e-2,-4.98e-3,-1.23e-3], 600:[-1.07e-2,-2.57e-3,-6.35e-4,-1.58e-4],
         650:[-1.71e-4,-4.25e-5,-1.06e-5,-2.65e-6], 660:[-1.85e-5,-4.64e-6,-1.16e-6,-2.90e-7],
         700:[-5.15e-3,-1.32e-3,-3.33e-4,-8.36e-5], 800:[-5.19e-2,-1.40e-2,-3.61e-3,-9.12e-4],
         1000:[-2.48e-1,-7.31e-2,-1.95e-2,-5.00e-3]}
dts = ['0.04','0.02','0.01','0.005']
rows = {}
for Ra in paper:
    s = np.array([growth(f'onset/Ra{Ra}_dt{d}.txt') for d in dts]); e = s - exact(Ra)
    rows[Ra] = (s, e)
    od = np.log2(np.diff(s)[:-1]/np.diff(s)[1:])      # orders from successive differences (no spatial error)
    print(f'{Ra:5d} exact {exact(Ra):9.5f} | FF err ' + ' '.join(f'{x:10.3e}' for x in e)
          + ' | paper ' + ' '.join(f'{x:9.2e}' for x in paper[Ra]) + ' | diff-orders ' + ' '.join(f'{x:.2f}' for x in od))
# critical Rayleigh number: zero of a quadratic fit of sigma(Ra) at dt = 0.005 on Ra = 600..700
Ras = np.array([600, 650, 660, 700]); s = np.array([rows[r][0][3] for r in Ras])
c = np.polyfit(Ras, s, 2); r = np.roots(c); r = r[(r > 600) & (r < 700)]
print('Ra_c (dt=0.005, quadratic fit) =', r, ' exact 27 pi^4/4 =', 27*np.pi**4/4)
