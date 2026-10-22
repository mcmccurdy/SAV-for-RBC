#!/bin/bash
# postprocess.sh WORK OUT : every table, values file and figure of the manuscript from the run logs in WORK,
# plus text files with the numbers that the text quotes from runs without a table of their own.
HERE=$(cd "$(dirname "$0")" && pwd); FF=$(dirname "$HERE"); T=$FF/tables
WORK=$(cd "$1" && pwd); mkdir -p "$2"; OUT=$(cd "$2" && pwd); mkdir -p "$OUT/logs"
export NSB_FF=$WORK
cd "$WORK"
step() {  # step NAME command...
  name=$1; shift
  if "$@" > "$OUT/logs/$name.txt" 2>&1; then echo "  ok      $name"; else echo "  FAILED  $name (see $OUT/logs/$name.txt)"; fi
}
echo "stage 3: tables and figures -> $OUT"
step tables_bench   python3 "$T/table_bench_fem.py"     "$OUT/table_cb.tex"    "$OUT/table_mw.tex"
step tables_decay   python3 "$T/table_decay_eta_fem.py" "$OUT/table_decay.tex" "$OUT/table_eta.tex"
step tables_dt      python3 "$T/table_dt_fem.py"        "$OUT/table_dt.tex"    "$OUT/table_trans.tex"
step table_growth   python3 "$T/table_growth_fem.py"    "$OUT/table_growth.tex" "$OUT/values_rac.tex"
step table_mms      python3 "$T/table_mms_fem.py"       "$OUT/table_mms.tex"
step table_rolls    python3 "$T/table_rolls_fem.py"     "$OUT/table_rolls.tex"
step table_space    python3 "$T/table_space_fem.py"     "$WORK/space/" "$OUT/table_space.tex"
step figures        python3 "$T/make_figures_fem.py"    "$OUT" onset convergence weightC flows bench
if ls scaling/Ra*_C*_dt*.txt >/dev/null 2>&1; then
  step fig_scaling  python3 "$FF/scaling/post_scaling.py" "$OUT"
  cp "$OUT/logs/fig_scaling.txt" "$OUT/text_scaling_fit.txt"
else
  echo "  skipped fig_scaling (no runs in scaling/)"
fi
{ echo "# kinetic and thermal parts of R^{n+1} (Section 6.5): largest |R_kin|, largest |R_th| over each run, and their ratio"
  grep -H '# RPARTS' scaling_rparts/*.txt 2>/dev/null; } > "$OUT/text_scaling_rparts.txt"
if [ -f "$WORK/ra1e6/ra1e6b.txt" ]; then
  step fig_ra1e6    python3 "$T/fig_ra1e6.py" "$WORK/ra1e6" "$OUT"
else
  echo "  skipped fig_ra1e6 (the Ra = 1e6 run needs --with-long)"
fi
# numbers quoted in the text
step slip_rac       python3 "$T/slip_rac.py"
cp "$OUT/logs/slip_rac.txt" "$OUT/text_slip_rac.txt"
{ echo "# direct eigenvalue check (Section 6.2): growth rates (EIG) and critical Rayleigh numbers (RAC)"
  for k in fs_sigma fs_rac rg_rac ns_rac; do cat eig/${k}_N*.txt 2>/dev/null; done; } > "$OUT/text_eig.txt"
{ echo "# manufactured solution on the graded mesh (Section 6.1): L2 difference u p T, standard minus rotational"
  grep -h '# REF' mms/gy/std_*.txt 2>/dev/null; } > "$OUT/text_mms_graded.txt"
{ echo "# relaxation parameter on the manufactured solution (Section 6.8): dt, Linf u p T, L2 u p T, |Q~-1|, |Q-1|"
  for f in eta_mms/mms_eta*.txt; do echo "$f: $(grep -h '# MMS dt' "$f" | head -1)"; done 2>/dev/null; } > "$OUT/text_eta_mms.txt"
echo "  wrote text_slip_rac.txt, text_eig.txt, text_mms_graded.txt, text_eta_mms.txt (and text_scaling_fit.txt)"
