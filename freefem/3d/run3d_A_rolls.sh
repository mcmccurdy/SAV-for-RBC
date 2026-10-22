#!/bin/bash
# Case A: three-dimensional check of the steady rolls of the Clever-Busse comparison (paper Section 6.4, Table cb):
# Pr = 0.71, Ra = 5000, rigid walls, alpha = 3.117, square periodic box Lx = Lz = 2 pi/alpha, H = 1.
# Start from the 2D roll plus a small three-dimensional mode (Tz), and follow whether the 3D part decays (column
# Ekin_z) and Nu approaches the 2D value (2.1103 on the 32x32 mesh, Table cb; Clever & Busse 2.116).
# The run is done in chunks with restart files, so it can be stopped and resumed (rerun the script: it continues
# from the last chunk it finds).
if [ -z "$FF_LOADPATH" ] && [ -d /usr/lib/freefem++ ]; then export FF_LOADPATH=/usr/lib/freefem++; fi   # plugin folder (msh3, iovtk) on Debian/Ubuntu; not needed on macOS
cd "$(dirname "$0")"; mkdir -p caseA; cd caseA
N=${N:-16}; DT=2e-3; CHUNK=${CHUNK:-1.0}; TEND=${TEND:-10}
ARGS="-Ra 5000 -nu 0.71 -kap 1 -G 3550 -k 3.117 -l 1e6 -gy 0 -nx $N -ny $N -nz $N -dt $DT -C 1000 -Tamp 0.1 -Tz 0.01 -every 10 -slice 500 -iter 1"
prev=""
NCH=$(awk -v a=$TEND -v b=$CHUNK 'BEGIN{printf "%d", a/b + 0.5}')
for k in $(seq 1 $NCH); do
  t1=$(awk -v k=$k -v b=$CHUNK 'BEGIN{printf "%.6g", k*b}'); tag=$(printf "%08.3f" $t1)
  if [ -f state_$tag.dat ]; then prev=state_$tag.dat; continue; fi
  LOAD=""; [ -n "$prev" ] && LOAD="-load $prev"
  FreeFem++-nw ../nsb3d.edp $ARGS -tend $t1 $LOAD -save state_$tag.dat -out caseA.txt > log_$tag.txt 2>&1 || { echo "run failed, see caseA/log_$tag.txt"; exit 1; }
  echo "t = $t1 done: $(grep -v '^#' caseA.txt | tail -1 | cut -c1-100)"
  prev=state_$tag.dat
done
python3 ../plot3d.py caseA.txt
