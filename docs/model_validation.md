# Model validation and numerical checks

## 1. Aerodynamic design-point check

Before optimization, the final BEM formulation was compared with selected IEA 15-MW reference design-point values.

| Quantity | Reference | Reduced-order model | Difference |
|---|---:|---:|---:|
| \(C_P\) | 0.489 | 0.49241 | ≈ +0.70% |
| \(C_T\) | 0.799 | 0.80213 | ≈ +0.39% |
| Aerodynamic power | 16.092 MW | 16.204 MW | ≈ +0.70% |

This provides evidence that the BEM implementation reproduces the selected rated aerodynamic quantities closely enough for the intended reduced-order design exploration.

It is not a substitute for a complete OpenFAST comparison over multiple operating points.

## 2. Root-moment numerical integration check

The one-blade root moment was evaluated both directly from the distributed normal load and by integrating the internal shear distribution. The two routes agreed to numerical precision in the development study, giving approximately 63.108 MN·m for the rated baseline.

## 3. Structural solver cross-check

Before adding centrifugal geometric stiffness, the beam FEM was compared with the earlier curvature-integration model:

| Method | Tip deflection |
|---|---:|
| numerical integration | 17.0701 m |
| Euler-Bernoulli FEM | 17.0427 m |
| difference | ≈ −0.16% |

The close match checks the load transfer, boundary conditions, stiffness mapping and finite-element implementation.

## 4. Centrifugal stiffening sanity check

At 7.56 rpm:

- non-rotating FEM tip: approximately 17.043 m;
- rotating FEM tip: approximately 15.570 m;
- reduction from centrifugal stiffening: approximately 8.64%.

This is physically consistent with the tensile geometric stiffness expected for a rotating blade.

## 5. BEM operating-envelope health checks

The development notebook also checked station convergence, maximum iteration counts, induction ranges, minimum active Prandtl loss factor, angle-of-attack range and polar-table coverage. The public AeroDyn polar files used in the study cover a broad ±180° range, so the steady high-wind load-reversal cases remain within the tabulated interpolation domain.

## 6. ML validation

Surrogate models were evaluated on a 20% holdout set and again with 5-fold cross-validation. The raw performance tables are stored in `results/tables/surrogate_holdout_metrics.csv` and `results/tables/surrogate_cv_metrics.csv`. The final engineering selection was **not accepted from ML prediction alone**; core Pareto candidates were re-evaluated with the original reduced-order physics model.
