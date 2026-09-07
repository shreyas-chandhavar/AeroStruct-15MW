# Surrogate-assisted optimization workflow

## Why use ML here?

The objective is computational acceleration, not replacement of mechanics. A single candidate evaluation executes BEM, rotating structural response, gust, fatigue-proxy and modal calculations. The physics model is affordable for hundreds of designs but unnecessarily expensive for tens of thousands of design candidates.

The workflow is therefore:

```text
physics model → DOE database → surrogate model → large search → physics verification
```

## Design variables

1. peak smooth twist: 0–2°;
2. aerodynamic modification start: 70–77 m;
3. structural modification start: 70–85 m;
4. flapwise EI increase: 0–30%.

The aerodynamic shape is fixed to a 10 m half-cosine ramp, 20 m plateau and 10 m half-cosine ramp down. Structural reinforcement occupies a 30 m window.

## Physics database

A 300-point Latin Hypercube sample (seed 42) is evaluated. Outputs include rated \(C_P\), rated root moment, rated rotating tip deflection, simplified gust root moment, DEL10 fatigue proxy, first flapwise/edgewise modal frequencies, 3P margins and derived added mass.

## Regressors

The notebook compares Random Forest (400 trees), Extra Trees (400 trees), and Gradient Boosting (300 estimators, learning rate 0.04, depth 3). Each target is allowed to select its own best model rather than forcing one algorithm across all responses.

## Validation

The 300 designs are split into 240 training and 60 holdout designs. R², MAE and RMSE are computed, then 5-fold shuffled cross-validation is applied to the full database.

## Large search

The selected target-specific surrogate models evaluate a 100,000-point Latin Hypercube sample (seed 123). Hard engineering constraints are applied before Pareto filtering.

| Stage | Count |
|---|---:|
| physics DOE | 300 |
| training / holdout | 240 / 60 |
| surrogate search | 100,000 |
| basic feasible candidates | 59,633 |
| core surrogate Pareto | 152 |
| physics-feasible after re-evaluation | 102 |
| final physics Pareto | 54 |
| ≤1% DEL-proxy penalty | 17 |

## Final selection

After full physics re-evaluation, final candidates are filtered to at most 1% DEL10-proxy penalty. Rated root moment, rated rotating tip deflection, DEL10 and mass are min-max normalized and combined with equal-weight Euclidean distance to an idealized utopia point.

The final solution converges toward approximately 1.5° of outboard twist and essentially zero structural reinforcement.

The correct project description is **surrogate-assisted multi-objective optimization with physics re-verification**.
