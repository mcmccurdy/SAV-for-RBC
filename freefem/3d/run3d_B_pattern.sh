#!/bin/bash
# Case B: convection patterns from random initial data in a wide periodic box (aspect ratio 4 x 4 x 1),
# Pr = 0.71, Ra = 5000, rigid walls. Output: Nu(t), kinetic energy and its z part, range of Q~, the mid-plane
# temperature every 250 steps (plot3d.py), and ParaView files every 250 steps.
# C = 1e4 (the free-fall value (1/2)|Omega| G |dT| H = 2.8e4 bounds the kinetic energy in practice; the rolls of
# Case A have E of order 1e2 per roll cell). Chunks with restart files as in Case A.
if [ -z "$FF_LOADPATH" ] && [ -d /usr/lib/freefem++ ]; then export FF_LOADPATH=/usr/lib/freefem++; fi   # plugin folder (msh3, iovtk) on Debian/Ubuntu; not needed on macOS
cd "$(dirname "$0")"; mkdir -p caseB; cd caseB
NX=${NX:-32}; NY=${NY:-16}; DT=2e-3; CHUNK=${CHUNK:-2.0}; TEND=${TEND:-20}
ARGS="-Ra 5000 -nu 0.71 -kap 1 -G 3550 -Lx 4 -Lz 4 -l 1e6 -gy 0 -nx $NX -ny $NY -nz $NX -dt $DT -C 1e4 -Tamp 1e-3 -noise 1 -every 10 -slice 250 -vtk 250 -iter 1"
prev=""
NCH=$(awk -v a=$TEND -v b=$CHUNK 'BEGIN{printf "%d", a/b + 0.5}')
for k in $(seq 1 $NCH); do
  t1=$(awk -v k=$k -v b=$CHUNK 'BEGIN{printf "%.6g", k*b}'); tag=$(printf "%08.3f" $t1)
  if [ -f state_$tag.dat ]; then prev=state_$tag.dat; continue; fi
  LOAD=""; [ -n "$prev" ] && LOAD="-load $prev"
  FreeFem++-nw ../nsb3d.edp $ARGS -tend $t1 $LOAD -save state_$tag.dat -out caseB.txt > log_$tag.txt 2>&1 || { echo "run failed, see caseB/log_$tag.txt"; exit 1; }
  echo "t = $t1 done: $(grep -v '^#' caseB.txt | tail -1 | cut -c1-100)"
  prev=state_$tag.dat
done
python3 ../plot3d.py caseB.txt
