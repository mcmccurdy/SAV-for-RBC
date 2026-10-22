#!/bin/bash
# Reproduce every computation, table and figure of the manuscript (two-dimensional part).
#
#   reproduce/reproduce.sh --quick          about a minute: checks the installation on five short runs
#   reproduce/reproduce.sh [-j N]           all 2D runs except the two Ra = 1e6 runs (about 27 CPU hours;
#                                           with N cores, roughly 27/N hours), then the tables and figures
#   reproduce/reproduce.sh --with-long      also the two Ra = 1e6 runs (several hours each, one core each)
#   reproduce/reproduce.sh --post-only      only the tables and figures, from an existing work folder
#
# Options: -j N (parallel jobs, default: number of cores), --work DIR (default: freefem/work),
#          --out DIR (default: freefem/out).
# The runs are resumable: after an interruption, run the same command again and finished jobs are skipped.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
FF=$(dirname "$HERE")
J=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
WORK=$FF/work; OUT=$FF/out
QUICK=0; LONG=0; POST=0
while [ $# -gt 0 ]; do
  case $1 in
    -j) J=$2; shift;;
    --work) WORK=$2; shift;;
    --out) OUT=$2; shift;;
    --quick) QUICK=1;;
    --with-long) LONG=1;;
    --post-only) POST=1;;
    -h|--help) sed -n '2,12p' "$0"; exit 0;;
    *) echo "unknown option $1"; exit 1;;
  esac
  shift
done
mkdir -p "$WORK"; WORK=$(cd "$WORK" && pwd)
[ $QUICK = 0 ] && { mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd); }

# --- requirements ---
command -v FreeFem++-nw >/dev/null || { echo "FreeFem++-nw not found (FreeFEM 4.x is needed)"; exit 1; }
python3 -c "import numpy, scipy, matplotlib" 2>/dev/null || { echo "python3 with numpy, scipy and matplotlib is needed"; exit 1; }
echo "FreeFEM: $(FreeFem++-nw 2>&1 | head -1)"
echo "work folder: $WORK   parallel jobs: $J"; [ $QUICK = 0 ] && echo "output folder: $OUT"

prepare() {   # $1 = job file with comments: writes the bare job list, creates the output folders
  grep -v '^[[:space:]]*#' "$1" | grep -v '^[[:space:]]*$' > "$2"
  grep -oE '(-out|-save|>) [^ ;]+' "$2" | awk '{print $2}' | xargs -n1 dirname | sort -u | (cd "$WORK" && xargs mkdir -p)
}
runall() {    # $1 = bare job list
  n=$(wc -l < "$1")
  seq "$n" | xargs -P "$J" -I{} bash "$HERE/runjob.sh" "$WORK" "$1" {}
  failed=$(grep -c FAIL "$WORK/progress.log" 2>/dev/null || true)
  [ "$failed" != "0" ] && [ -n "$failed" ] && echo "WARNING: $failed job(s) failed; see $WORK/progress.log" || true
}

cp "$FF/nsb.edp" "$FF/eig.edp" "$FF/mms.idp" "$WORK/"

if [ $QUICK = 1 ]; then
  prepare "$HERE/quick_jobs.txt" "$WORK/quick_list.txt"
  rm -rf "$WORK/.done"/quick_list_*
  start=$(date +%s); runall "$WORK/quick_list.txt"
  echo "quick runs took $(( $(date +%s) - start )) s"
  python3 "$HERE/quick_check.py" "$WORK" "$HERE/reference/quick"
  exit $?
fi

if [ $POST = 0 ]; then
  # stage 1: every run of runs.txt (the Ra = 1e6 runs only with --with-long)
  if [ $LONG = 1 ]; then grep -v '^[[:space:]]*#' "$FF/runs.txt" > "$WORK/runs_selected.txt"
  else grep -v '#@long' "$FF/runs.txt" > "$WORK/runs_selected.txt"; fi
  prepare "$WORK/runs_selected.txt" "$WORK/run_list.txt"
  echo "stage 1: $(wc -l < "$WORK/run_list.txt") runs"; start=$(date +%s)
  runall "$WORK/run_list.txt"
  echo "stage 1 took $(( ($(date +%s) - start) / 60 )) min"
  # stage 2: time errors of the manufactured solution against the reference run (Table tab:mms)
  MMS="-mms 1 -y0 -1 -y1 1 -Lx 6.283185307179586 -nu 0.1 -kap 0.05 -G 1 -l 1 -every 100000 -nx 40 -ny 40"
  : > "$WORK/cmp_list.txt"
  for r in rT rF u; do for dt in 0.05 0.025 0.0125 0.00625 0.003125 0.0015625; do
    echo "FreeFem++-nw nsb.edp $MMS -dt $dt -tend 0 -init mms/${r}_N40_dt$dt.dat -ref mms/ref_N40.dat -out mms/cmp/${r}_$dt.txt" >> "$WORK/cmp_list.txt"
  done; done
  mkdir -p "$WORK/mms/cmp"; echo "stage 2: comparison with the reference run"
  runall "$WORK/cmp_list.txt"
fi

# stage 3: tables, figures and the numbers quoted in the text
bash "$HERE/postprocess.sh" "$WORK" "$OUT"
