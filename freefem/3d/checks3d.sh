#!/bin/bash
# Smoke tests of nsb3d.edp (the checks listed in README_3d.md).
# Output in checks/; a short report is printed at the end.
if [ -z "$FF_LOADPATH" ] && [ -d /usr/lib/freefem++ ]; then export FF_LOADPATH=/usr/lib/freefem++; fi   # plugin folder (msh3, iovtk) on Debian/Ubuntu; not needed on macOS
cd "$(dirname "$0")"; mkdir -p checks; D=checks
FF="FreeFem++-nw nsb3d.edp"
# (1) manufactured solution, time: 6^3 mesh, differences from a run with dt/32 (second order expected)
M="-mms 1 -Lx 6.283185307179586 -Lz 6.283185307179586 -y0 -1 -y1 1 -nu 0.1 -kap 0.05 -G 1 -l 1 -nx 6 -ny 6 -nz 6 -tend 0.5"
$FF $M -dt 0.0015625 -save $D/ref6.dat -out $D/ref6.txt > /dev/null 2>&1
for dt in 0.05 0.025 0.0125 0.00625; do $FF $M -dt $dt -ref $D/ref6.dat -out $D/mt_$dt.txt > /dev/null 2>&1; done
# (2) manufactured solution, space: N = 4 ... 12, errors against the exact fields
for N in 4 6 8 12; do $FF ${M/-nx 6 -ny 6 -nz 6/} -dt 0.0125 -iter 1 -nx $N -ny $N -nz $N -out $D/ms_$N.txt > /dev/null 2>&1; done
# (3) restart: 20 steps at once against 10 + save + load + 10
A="-Ra 5000 -k 3.117 -l 1e6 -gy 0 -Tamp 0.1 -Tz 0.05 -nx 6 -ny 6 -nz 6 -dt 2e-3 -C 100"
$FF $A -tend 0.04 -out $D/rs_full.txt > /dev/null 2>&1
$FF $A -tend 0.02 -save $D/rs.dat -out $D/rs_split.txt > /dev/null 2>&1
$FF $A -tend 0.04 -load $D/rs.dat -out $D/rs_split.txt > /dev/null 2>&1
# (4) free-slip onset at Ra = 1000, k = pi/sqrt 2: the roll varying in x and the same roll varying in z (equal growth rates)
K=2.221441469079183; LK=2.8284271247461903
$FF -Ra 1000 -k $K -Lz 0.5 -nx 12 -ny 12 -nz 2 -dt 0.005 -tend 2 -iter 1 -out $D/fs_x.txt > /dev/null 2>&1 &
$FF -Ra 1000 -k $K -Lx 0.5 -Lz $LK -kz $K -rollz 1 -nx 2 -ny 12 -nz 12 -dt 0.005 -tend 2 -iter 1 -out $D/fs_z.txt > /dev/null 2>&1 &
wait
# (5) rigid rolls, Ra = 5000, k = 3.117, z-independent, to the steady state (t = 4), and the 2D code on the same mesh
$FF -Ra 5000 -k 3.117 -Lz 0.5 -l 1e6 -gy 0 -Tamp 0.1 -nx 12 -ny 12 -nz 2 -dt 2e-3 -C 100 -tend 4 -every 10 -iter 1 -out $D/rg3d.txt > /dev/null 2>&1 &
if [ -f ../nsb.edp ]; then
  FreeFem++-nw ../nsb.edp -Ra 5000 -k 3.117 -l 1e6 -gy 0 -Tamp 0.1 -nx 12 -ny 12 -dt 2e-3 -C 100 -tend 4 -every 10 -out $D/rg2d.txt > /dev/null 2>&1 &
fi
wait
# (6) energy decay without heating (Theorem 4.2(a)): X^n must not increase
E="-Tb 0.5 -Tt 0.5 -Tref 0.5 -G 3000 -k 3.117 -l 1e6 -gy 0 -Tamp 0.2 -Tz 0.1 -nx 8 -ny 8 -nz 8 -X 1 -iter 1"
for A5 in 1 5e5; do
  $FF $E -A $A5 -dt 1e-2 -tend 1 -out $D/dec_A${A5}_dt1e-2.txt > /dev/null 2>&1
  $FF $E -A $A5 -dt 1e-3 -tend 0.3 -out $D/dec_A${A5}_dt1e-3.txt > /dev/null 2>&1
done
# report
echo "(1) time, L2 differences of u T p from dt/32:"; for dt in 0.05 0.025 0.0125 0.00625; do grep -h "^# REF" $D/mt_$dt.txt | cut -d: -f2; done
echo "(2) space, L2 errors of u T p against the exact fields:"; for N in 4 6 8 12; do echo "N=$N $(grep -h '^# MMS' $D/ms_$N.txt | cut -d: -f2)"; done
echo "(3) restart (the two lines must agree):"; grep -v '^#' $D/rs_full.txt | tail -1; grep -v '^#' $D/rs_split.txt | tail -1
echo "(4) free-slip growth rate sigma from E_kin over the last half of the run, roll in x and roll in z (equal):"
for f in fs_x fs_z; do grep -v '^#' $D/$f.txt | awk '{t[NR]=$2; e[NR]=$5} END{m=int(NR/2); printf "%s sigma = %.6f\n", nm, 0.5*log(e[NR]/e[m])/(t[NR]-t[m])}' nm=$f; done
echo "(5) rigid rolls at t = 4, 3D (E_kin is per Lz = 0.5) and 2D:"; grep -v '^#' $D/rg3d.txt | tail -1; [ -f $D/rg2d.txt ] && grep -v '^#' $D/rg2d.txt | tail -1
echo "(6) energy decay, largest one-step change of X (must be <= 0):"; grep -H "max X" $D/dec_*.txt
grep -l -i -w "nan\|blow-up" $D/*.txt 2>/dev/null && echo "some runs blew up or produced NaN (files above)"
