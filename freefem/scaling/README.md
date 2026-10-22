# Scaling of the computational scalar with E/C (Section 6.5, Figure 7)

`max|Q~ - 1|` over the formation of the rolls, for five Rayleigh numbers (Ra = 2000 to 2e4, kinetic energies from about 11 to about 1600), two weights `C = 1, 100` and four time-steps (2.5e-4 to 2e-3). Rigid walls, 32x32 mesh graded towards the walls, relaxed scheme; the runs stop at t = 0.5 (t = 1.5 at Ra = 2000), after the rolls have saturated.

| file | what it is |
|---|---|
| `jobs_scaling.txt` | the 40 runs, one per line (`../nsb.edp` with `-fastint 1`, which computes the integrals of each step from assembled vectors and matrices: the same values up to round-off, and faster) |
| `run_jobs.sh` | runs a job file in parallel; finished runs are skipped, so it can be restarted after an interruption; copies `../nsb.edp` and `../mms.idp` here if they are missing |
| `post_scaling.py` | writes `fig_scaling.pdf` and prints the least-squares fit of the exponents |

The same 40 runs are also in `../runs.txt`, so `bash reproduce/reproduce.sh` (from `code/freefem`) computes them with everything else and writes `fig_scaling.pdf` and `text_scaling_fit.txt` in `out/`. To run only this study, from this folder (zsh or bash, with `FreeFem++-nw` on the path):

    bash run_jobs.sh jobs_scaling.txt 4     # 40 runs; replace 4 by the number of cores
    python3 post_scaling.py ../out          # fig_scaling.pdf, and the fit printed on the screen

The fit printed should be `d ~ dt^3.04 C^-1.00 E^2.74` (rms of the log residual is 0.22), as in Section 6.5.
