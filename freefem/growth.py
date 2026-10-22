"""growth rate (1/2) d ln Ekin/dt on [t0,t1] from an nsb.edp log; exact free-slip sigma
usage: python3 growth.py run.txt Ra [t0 t1]"""
import sys, numpy as np
def growth(f, t0=1., t1=2.):
    a = np.loadtxt(f); t, ek = a[:,1], a[:,4]; m = (t >= t0-1e-9) & (t <= t1+1e-9)
    return 0.5*np.polyfit(t[m], np.log(ek[m]), 1)[0]
def exact(Ra, k=np.pi/np.sqrt(2)):
    K = np.sqrt(k*k + np.pi**2); return k*np.sqrt(Ra)/K - K*K
if __name__ == '__main__':
    t0, t1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (1., 2.)
    s = growth(sys.argv[1], t0, t1); Ra = float(sys.argv[2]); e = exact(Ra)
    print(f'sigma={s:.8f} exact={e:.8f} err={s-e:.3e}')
