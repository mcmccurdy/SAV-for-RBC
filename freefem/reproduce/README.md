# Reproducing the computations of the manuscript

Everything here is run from the `freefem/` folder. Requirements: FreeFEM 4.x (`FreeFem++-nw` on the path) and Python 3 with numpy, scipy and matplotlib.

## 1. Check the installation (about a minute)

    bash reproduce/reproduce.sh --quick

Runs five short jobs from `runs.txt` (rigid-wall onset, manufactured solution in time and in space, energy decay, direct eigenvalue) and compares every number in their logs with the logs behind the paper (`reference/quick/`). It ends with `QUICK CHECK PASSED` or lists what differs. On the development machine (FreeFEM 4.13) the agreement is exact; another FreeFEM version, compiler or sparse solver may differ in the last digits, and the check allows a relative difference of 1e-6.

## 2. All two-dimensional computations

    bash reproduce/reproduce.sh -j 8

- **Stage 1**: every run of `runs.txt` (272 jobs, including the 45 runs of the scaling study) in `work/`, 8 at a time. About 27 CPU hours in total, so roughly 3.5 hours on 8 cores; the longest single run takes about 40 minutes.
- **Stage 2**: the comparison of the manufactured-solution runs with the reference run (time errors of Table 2).
- **Stage 3**: every table (`table_*.tex`), `values_rac.tex` and figure (`fig_*.pdf`) in `out/`, plus text files with the numbers quoted in the text from runs without a table (slip coefficients, eigenvalue check, graded-mesh manufactured solution, relaxation parameter, and the fitted exponents and the parts of R^{n+1} of the scaling study).

The runs are resumable: if the computer stops, run the same command again and finished jobs are skipped (`work/progress.log` records every job). `bash reproduce/reproduce.sh --post-only` repeats stage 3 only.

The two runs at Ra = 1e6 (Section 6.9 and Figure 8) take several hours each and are left out unless you add `--with-long`. Without them, Figure 8 is not regenerated.

## 3. Three-dimensional computations (optional, long)

See `../3d/README.md`. The paper's runs are:

    cd 3d
    bash checks3d.sh                              # the checks of Section 6.10 (about 25 minutes)
    TEND=1 bash run3d_A_rolls.sh                  # Case A (500 steps, 16^3; about 30 minutes)
    TEND=6.76 CHUNK=6.76 bash run3d_B_pattern.sh  # Case B (3380 steps, 32x16x32; about 12 hours)
    python3 fig_caseA.py caseA/caseA.txt ../out/fig_caseA.pdf
    mkdir -p caseB/render
    for s in 100500 101500 103250; do python3 render3d.py caseB/caseB.txt_$s.vtu caseB/render/c_$s.png --level=0.12 --res=1800x1350 --crop=1; done
    python3 fig_caseB.py caseB/caseB.txt caseB/render ../out/fig_caseB.pdf
