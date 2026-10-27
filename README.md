
Code for the paper

> M. McCurdy, *A second-order linear decoupled scheme with a relaxed zero-energy variable for Rayleigh–Bénard convection*, submitted to the Journal of Computational Physics.

It computes every table and figure of the paper.

## Contents

| folder | what it holds |
|---|---|
| `freefem/` | the 2D FreeFEM code `nsb.edp`, the eigenvalue check `eig.edp`, the manufactured solution (`gen_mms_ff.py` writes `mms.idp`), the command line of every run `runs.txt`, the table and figure scripts `tables/` (with the shared line colours `tables/palette.py`), the reproduction pipeline `reproduce/`, the scaling study `scaling/`, and the 3D code `3d/`; each has its own README |
| `tools/render/` | `render.py`: the line-integral-convolution texture and contrast stretch used for Figure 8 |

## Requirements

- FreeFEM 4.x with `FreeFem++-nw` on the path (the manuscript's results were computed with 4.13). The 3D code also needs the `msh3` and `iovtk` plugins, which the standard installers include.
- Python 3 with numpy, scipy and matplotlib. Also, pyvista and Pillow for the 3D images.

## 1. Check the installation (should take about a minute)

    cd freefem
    bash reproduce/reproduce.sh --quick

Runs five short jobs and compares every number in their logs with the logs behind the paper. It ends with `QUICK CHECK PASSED`. Another FreeFEM version, compiler or sparse solver may differ in the last digits; the check allows a relative difference of 10⁻⁶.

## 2. All two-dimensional computations (Sections 6.1–6.9)

    cd freefem
    bash reproduce/reproduce.sh -j 8                 # every 2D run, then all tables and figures
    bash reproduce/reproduce.sh -j 8 --with-long     # also the two Ra = 1e6 runs (Figure 8; several hours each)

- About 27 CPU hours in total (roughly 3.5 hours on 8 cores), including the scaling study of Section 6.5; results go to `freefem/work/`, tables and figures to `freefem/out/`.
- The runs are resumable: after an interruption, run the same command again, and finished jobs are skipped.
- `bash reproduce/reproduce.sh --post-only` repeats only the tables and figures.

## 3. Scaling of the computational scalar with E/C (Section 6.5, Figure 7)

Its 40 runs, and 5 more that log the kinetic and thermal parts of R^{n+1} (`nsb.edp -rparts 1`), are part of `runs.txt`, so step 2 already computes them, writes `fig_scaling.pdf`, and saves the fit in `out/text_scaling_fit.txt` and the parts of R^{n+1} in `out/text_scaling_rparts.txt`.
It should read `d ~ dt^3.04 C^-1.00 E^2.74`, as in Section 6.5.

To run only this study:

    cd freefem/scaling
    bash run_jobs.sh jobs_scaling.txt 4       # 40 runs; replace 4 by the number of cores (under an hour-ish on 4 cores)
    python3 post_scaling.py ../out            # fig_scaling.pdf, and the fitted exponents printed out

## 4. Three-dimensional computations (Section 6.10, Table 12, Figures 9 and 10)

From `freefem/3d` (details in `3d/README.md`):

    bash checks3d.sh                              # the checks of Section 6.10 (~25-30-ish minutes)
    TEND=1 bash run3d_A_rolls.sh                  # Figure 9 (500 steps, 16^3; ~30 minutes)
    TEND=6.76 CHUNK=6.76 bash run3d_B_pattern.sh  # Figure 10 (3380 steps, 32x16x32; ~12 hours)
    python3 fig_caseA.py caseA/caseA.txt ../out/fig_caseA.pdf
    mkdir -p caseB/render
    for s in 100500 101500 103250; do python3 render3d.py caseB/caseB.txt_$s.vtu caseB/render/c_$s.png --level=0.12 --res=1800x1350 --crop=1; done
    python3 fig_caseB.py caseB/caseB.txt caseB/render ../out/fig_caseB.pdf

If FreeFEM reports "Load error: msh3", set `FF_LOADPATH` to the folder that holds `msh3.so` (see `3d/README.md` for more info about this).

## Notes

- `nsb.edp -fastint 1` computes the integrals of each step from assembled vectors and matrices instead of quadrature expressions (the same values up to round-off, and faster). (The runs of `scaling/` use it, all other runs do not.)
- `freefem/reproduce/reference/` and `freefem/3d/runs/` hold the logs of the paper's runs that the quick check and the 3D comparison use as references.
