# 3D version of the Boussinesq SAV scheme

`nsb3d.edp` is the scheme of the paper in three dimensions:
- BDF2 with the zero-energy variable Q (weight C) and the rotational pressure correction;
- relaxation of the stored Q;
- Taylor–Hood P2/P1 elements, with P2 temperature;
- skew-symmetric convection;
- the hydrostatic pressure of the conduction state removed analytically.

The domain is the box [0, Lx) × (0, H) × [0, Lz): y is vertical, periodic in x and z, with walls at y = 0 and y = H. The walls carry the Navier condition on both tangential velocity components (l ≥ 10⁵ means rigid), u_y = 0, and T = T_b, T_t. The script has the same layout and steps as `nsb.edp`, with a third velocity component. Its right-hand sides come from matrices assembled once (mass, gradient, and divergence) and from the convection matrix of each step, which is faster in 3D than quadrature expressions

## Requirements

- FreeFem 4.x, including the plugins `msh3` (3D meshes) and `iovtk` (ParaView output) (these are often included in standard installers)
- If FreeFem cannot find the plugins ("Load error: msh3"), set `FF_LOADPATH` to the folder that contains `msh3.so`
      * Linux: `/usr/lib/freefem++`
      * macOS installer: `/Applications/FreeFem++.app/Contents/ff-4.x/lib/ff++/4.x/lib`

- Python 3 with numpy and matplotlib, for `plot3d.py`
- The run scripts are bash

## Options

The options are those of `nsb.edp`, except `-init` (use `-load`), the snapshot and live-picture options (`-snap`, `-plot`, and their companions), `-fastint`, `-rparts`, and `-timing` (the TIMING line is always written). Without `-G`, G = Ra ν κ / H³.

In addition:
- `-nz` and `-Lz`;
- `-rollz 1`: the initial roll varies in z instead of x;
- `-Tz A`: adds a 3D mode A sin(πy) cos(kx) cos(k_z z), with k_z from `-kz`, default 2π/Lz;
- `-noise S`: random initial temperature, seed S;
- `-iter 1`: conjugate gradients instead of sparse factorization. Recommended from about 16³ up: it gives the same results as the direct solver to 10–12 digits, needs no factorization, and uses less memory;
- `-save F` / `-load F`: restart. Both time levels and Q are stored, so a split run reproduces an unsplit run exactly;
- `-slice N`: T and u_y on the mid-plane y = H/2, on a uniform `-snx` × `-snz` grid (default 128 × 128), every N steps;
- `-vtk N`: ParaView `.vtu` files every N steps;
- `-X 1`: the discrete energy E^n and X^n of Theorem 4.2;
- `-mms 1`: 3D manufactured solution (`gen_mms3d.py` writes `mms3d.idp`);
- `-ref F`: L² differences from a saved state.

The log has one line per `-every` steps: step, t, Q̃, Q, E_kin, E_θ, Nu_bottom, Nu_top, Nu_vol, E_kin,z (the kinetic energy of u_z, which measures three-dimensionality) [, E, X]. It ends with a `# SUMMARY` line (as in 2D, with E_kin,z in place of the largest change of X^n, which has its own `# max X^{n+1}-X^n` line with `-X 1`), a `# TIMING` line, and the `# MMS` or `# REF` line with `-mms 1` or `-ref F`.

## Checks done on the development machine

`bash checks3d.sh` repeats all of them (about 25 minutes on 2 cores) and prints a short report; the development machine's report is `checks_report.txt`. Check 4 compares with the 2D code `../nsb.edp` when it is there.

1. **Time convergence, manufactured solution (6³ mesh).** Differences from a run with δt/32 are 7.1·10⁻³, 1.8·10⁻³, 4.5·10⁻⁴ and 1.1·10⁻⁴ for u at δt = 0.05 … 0.00625, i.e. second order; T and p behave the same; |Q̃−1| = O(δt³).
2. **Space, manufactured solution (N = 4 … 12).** Orders about 3 for u and T in L², about 2.2–2.5 for p. These meshes are still pre-asymptotic.
3. **Onset, free slip, Ra = 1000.** With the roll varying in x or in z, σ = 3.446650 in both cases. The 2D code on the same 12×12 mesh gives 3.446617: the elements differ (tetrahedra against triangles) and the difference is 3·10⁻⁵.
4. **Rigid rolls, Ra = 5000, z-independent (12×12×2, Lz = 0.5, δt = 2·10⁻³, 2000 steps to t = 4, steady).** Nu_vol = 2.1103080 against 2.1103008 from the 2D code on the 12×12 mesh; E_kin/Lz = 142.0568 against 142.0622; the wall Nusselt numbers 2.11186 against 2.11088. E_kin,z stays exactly 0. The differences come from the elements (tetrahedra against triangles) on this coarse mesh.
5. **Energy decay without heating** (T_b = T_t = T_ref, G = 3000, 3D initial perturbation, A = 1 and A = 5·10⁵, δt = 10⁻², 10⁻³). X^n never increased: the largest one-step change is ≤ 0 in all runs. (This is Theorem 4.2(a) in 3D.)
6. **Restart.** 10 + 10 steps with `-save`/`-load` equal 20 steps to all printed digits.
7. **Iterative solver.** `-iter 1` gives the same results as the direct solver to 10–12 digits (manufactured solution and the rolls). CG stops with an error when a right-hand side is at round-off level, which happens in two cases, and those solves are skipped (solution 0): the u_z equations in z-independent flows, and the two pressure solves in a steady state, where (div ũ, q) tends to zero by cancellation between its three terms (skipped below 10⁻¹⁰ of the sum of their norms). Check 4 runs with `-iter 1` into its steady state.

## Production runs

- `run3d_A_rolls.sh`: the Clever–Busse rolls (Pr = 0.71, Ra = 5000, α = 3.117) in a square periodic box, from the 2D roll plus a small 3D mode, to t = 10 (5000 steps, 16³). It shows whether the 3D perturbation decays (E_kin,z) and whether Nu approaches the 2D value, 2.1103 on 32² in Table cb.
- `run3d_B_pattern.sh`: convection from random initial data in a 4 × 4 × 1 box (Pr = 0.71, Ra = 5000) to t = 20 (10000 steps, 32×16×32).
