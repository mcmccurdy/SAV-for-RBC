
`nsb.edp` implements the scheme of the paper (Sections 2–5) with finite elements. It produces every two-dimensional table and figure of the manuscript.

The folder `3d/` holds the three-dimensional version (`3d/nsb3d.edp`), with its checks and two production scripts.

## Discretization

- **Time stepping:**
  - BDF2 (backward Euler for the first step), with extrapolated nonlinear terms and buoyancy.
  - The zero-energy variable Q with weight C, relaxation of Q, and rotational pressure correction (`-rot 0`: standard incremental).
- **Elements:** Taylor–Hood P2/P1, periodic in x. `-gy 0` grades the mesh towards the walls: y = ½(1 − cos πs).
- **Nonlinear terms:** skew-symmetric form b(w,v,z) = ½[((w·∇)v,z) − ((w·∇)z,v)], so the zero-energy cancellation holds exactly for the Galerkin scheme.
- **Hydrostatic pressure:** the computed pressure is the deviation from the hydrostatic pressure of the conduction state, which is removed analytically.
  - Why: Taylor–Hood elements are not pressure robust (John et al., SIAM Rev. 2017). Otherwise, the quadratic p_c drives a spurious O(Gh²) flow that swamps small perturbations near onset.
  - Exception: the manufactured solution (`-mms 1`) keeps the full pressure.
- **Matrices:** assembled and factorized once. Each step solves θ, u_x, and u_y with two right-hand sides each (X₁ + Q̃X₂), then one pressure Poisson problem, two L² projections and the scalar update for Q̃.

## Options

| option | meaning |
|---|---|
| `-Ra -G -nu -kap -A -C` | Rayleigh number (G = Ra ν κ unless `-G`), viscosity, diffusivity, thermal weight, weight of the Q equation |
| `-Tb -Tt -Tref` | wall and reference temperatures (energy decay test: all 0.5) |
| `-k` / `-Lx` | wave number (cell length 2π/k) or cell length |
| `-l` | slip coefficient (0 free slip, 1e6 ≈ no slip) |
| `-nx -ny -gy` | mesh; `-gy 0` grades towards the walls |
| `-dt -tend` | time step, final time |
| `-eta` | relaxation parameter (negative: no relaxation) |
| `-rot` | 1 rotational (default), 0 standard incremental |
| `-Tamp -noise S` | initial amplitude; random initial temperature with seed S |
| `-X 1` | log E^n and X^n of Theorem 4.2(a) |
| `-rparts 1` | log the largest kinetic and thermal parts of R^{n+1} over the run (`# RPARTS`) |
| `-timing 1` | log the CPU time of the set-up and of the time loop (`# TIME`) |
| `-fastint 1` | integrals of each step from assembled vectors and matrices (same values up to round-off, faster; used by `scaling/`) |
| `-save F -init F -ref F` | write / read / compare final fields (same mesh and options); `-tend 0 -init A -ref B` compares two states |
| `-mms 1 -y0 -y1` | manufactured solution of Section 6.1 (walls at y0, y1) |
| `-snap N -snapu 1 -snx -sny` | every N steps, T (and u) on a uniform grid → `<out>.snapNNNN`; `plot_snaps.py` renders them |
| `-plot N -arrows 1 -field T\|theta` | live picture every N steps (graphics `FreeFem++`, not `-nw`) |
| `-every -out` | log interval and file |

**Log columns:** step, t, Q̃, Q, E_kin, E_θ, Nu (bottom), Nu (top), Nu (volume average), then [E, X] with `-X 1`.

**Final lines:**
- `# SUMMARY` gives the range of Q̃ and Q, E_kin, the Nusselt numbers, the blow-up step (−1 if none) and the largest one-step change of X^n.
- `# MMS` gives the errors against the exact solution.
- `# REF` gives the L² differences from a saved state.
- A run stops when E_kin > 10¹⁰ and writes `# blow-up`.
- `# MMS` and `# MMS2` give the errors against the manufactured solution; `# MMS2` uses the exact functions and adds the H¹ seminorms and the L² norm of div u.
- `# RPARTS` (with `-rparts 1`) gives the largest kinetic and thermal parts of R^{n+1} and their ratio.
- `# TIME` (with `-timing 1`) gives the CPU time of the set-up and of the time loop.

The volume-average Nu = 1 + ⟨u_y θ⟩/(κ|T_c′|) equals the wall value for a steady state, and it converges like h⁴ while the wall derivative is O(h²). The tables use it, except for unrelaxed runs, where the flux carries Q̃.

## Reproducing the paper

Use `reproduce/reproduce.sh` (see `reproduce/README.md`):

```
bash reproduce/reproduce.sh --quick     # about a minute: checks the installation against the paper's logs
bash reproduce/reproduce.sh -j 8        # every 2D run, then all tables and figures in out/
```

`runs.txt` lists every run, one independent job per line; `reproduce.sh` runs them in parallel (resumable), adds the comparison step of the manufactured solution, and writes the tables, values and figures. Cost: about 0.1 s per step on 24², 0.25 s on 32² and 0.6–1 s on 48² (one core); the whole 2D set, including the scaling study, takes about 27 CPU hours, plus several hours each for the two Ra = 1e6 runs (`--with-long`).

## Ra = 10⁶ transient (§6.8)

```
FreeFem++ nsb.edp -Ra 1e6 -Lx 4 -l 1e6 -gy 0 -nx 128 -ny 48 -dt 1e-5 -tend 0.1 -C 1e5 -Tamp 1e-2 -noise 1 -every 10 -snap 500 -plot 200 -out ra1e6.txt
python3 plot_snaps.py ra1e6.txt
```

## Further scripts and runs

- `nsb.edp -mms 1` now also prints a line `# MMS2 ...`: errors against the exact functions (not their interpolants), with a 9th-order quadrature — L² of u, T, p, H¹ seminorms of u and T, and ‖∇·u_h‖. `gen_mms_ff.py` writes `mms.idp` (exact solution, forcing, gradients).
- `tables/table_space_fem.py`: spatial-convergence table (manufactured solution, N = 8, 16, 32, 64, δt = 2.5·10⁻⁴) from `space/sN_dt2.5e-4.txt`.
- `tables/slip_rac.py`: Ra_c at k = 3.1163 for l/ν = 10²…10⁶ (rigid-wall check), from `slipcheck/` and `rigid2/`.
- `tables/fig_ra1e6.py RUNDIR`: the Ra = 10⁶ figure from the snapshots of the local run.
- `runs.txt` lists the command line of every run in the paper, including the further checks (spatial study, slip check, 48² Clever–Busse cases, graded-mesh MMS, MMS η sweep, the C = 1 first attempts, and both Ra = 10⁶ runs).
- `eig.edp`: the linear stability problem of the conduction state solved directly as a generalized eigenproblem.
