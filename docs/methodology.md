# Methodology

This document records the end-to-end technical methodology used in the AeroStruct-15MW development notebook. It separates exploratory checks from the final reduced-order workflow so that the public repository is readable and reproducible.

## 1. Study objective

The study asks whether spanwise aerodynamic load redistribution and localized structural tailoring can reduce flapwise blade-root loading and blade deflection while maintaining aerodynamic performance and avoiding unacceptable mass, fatigue-proxy or modal penalties.

The IEA 15-MW reference turbine is used as a **public baseline**, not as original project data.

## 2. Reference turbine and data

Core operating/model parameters used in the study:

- 3 blades
- rotor radius: 120 m
- blade span: approximately 117 m
- rated/design wind condition used for baseline validation: 10.59 m/s
- rated rotor speed: 7.56 rpm
- baseline pitch at the design point: 0°
- air density: 1.225 kg/m³

Reference inputs include:

- AeroDyn blade span, twist and chord
- AeroDyn station-specific airfoil polar tables
- ElastoDyn mass density
- ElastoDyn flapwise bending stiffness
- ElastoDyn edgewise bending stiffness

The `scripts/fetch_reference_data.py` script downloads these from the public upstream repository and creates the processed CSV tables.

## 3. Preliminary load-path checks

Before the distributed aerodynamic model was completed, point loads were used to verify the mechanics of a cantilevered blade. At an arbitrary section x, the internal shear and bending moment were computed as `V(x)=sum(F_i)` for loads outboard of the section and `M(x)=sum(F_i(r_i-x))`.

This was educational scaffolding only and is not used as the final aerodynamic load model.

## 4. Blade Element Momentum model

At each blade station, axial and tangential induction factors are iterated. The local induced velocities are `V_a=U_inf(1-a)` and `V_t=Omega*r*(1+a')`. Relative velocity, inflow angle and angle of attack follow from the velocity triangle. Station-specific AeroDyn polars are interpolated at the calculated angle of attack to obtain Cl and Cd, which are resolved into rotor-normal and rotor-tangential coefficients.

Finite-blade losses are represented with Prandtl hub and tip factors. The exact root and tip stations are treated as boundary points because the Prandtl expressions are singular there. In the high-induction region the notebook uses a Buhl-type correction. Iteration is stabilized with 0.25 under-relaxation, a tolerance of 1e-5, and a maximum of 300 iterations.

Sectional lift and drag are converted to rotor-normal and tangential distributed loads. Rotor thrust, torque, aerodynamic power, Cp, Ct and one-blade flapwise root moment are then obtained by spanwise integration.

## 5. Baseline aerodynamic validation

The baseline design point was compared with selected reference values:

- reference Cp=0.489; model approximately 0.4924
- reference Ct=0.799; model approximately 0.8021
- reference aerodynamic power 16.092 MW; model approximately 16.204 MW

The corresponding differences are approximately 0.70%, 0.39%, and 0.70%. This is a reduced-order design-point validation, not a complete OpenFAST or IEC validation campaign.

## 6. Non-rotating structural model

The distributed BEM normal load is integrated inward to obtain shear and bending moment. Curvature is evaluated from `kappa=M/EI`. The notebook first evaluates a linearized displacement, then uses large-rotation kinematics by integrating `cos(theta)` and `sin(theta)` along the blade. This check gave approximately 17.07 m linearized deflection and 16.87 m after the large-rotation kinematic correction at the baseline design point.

## 7. Structural sensitivity studies

Localized flapwise stiffness increases were scanned across the blade. The investigation evolved through three increasingly fair comparisons: equal local percentage EI increase, equal added-EI budget, and equal added structural mass. This showed that the preferred span region depends strongly on how the structural cost is normalized. A balanced intermediate structural concept used roughly a 30 m reinforcement window in the 80–110 m region, about +25.84% local EI and approximately +1000 kg/blade.

## 8. Mass-to-stiffness proxy

Detailed composite laminate sizing was outside the scope of the project. The structural design stage therefore uses the screening approximation `delta m'/m' ≈ delta EI/EI` inside the modified structural window. This does not model laminate layup, spar caps, webs, sandwich construction, buckling, failure indices, or material substitution.

## 9. Aerodynamic load-alleviation concept

A positive outboard twist increment reduces local angle of attack and therefore outboard normal loading. An initial abrupt step produced useful load reduction but visible loading discontinuities. It was replaced by a smooth 40 m modification: 10 m half-cosine ramp up, 20 m plateau, and 10 m half-cosine ramp down. A smooth peak twist near 1.5° produced about a 1% Cp penalty and approximately 5%–5.5% rated root-moment reduction in the reduced-order model.

## 10. Steady operating controller

Below rated, a target tip-speed ratio lambda_opt=9 is used and rotor speed is clipped between 5 rpm and 7.56 rpm. Above rated, rotor speed is held at 7.56 rpm and collective pitch is found with bisection so that aerodynamic rotor power matches the baseline BEM rated aerodynamic power. This is a steady controller; actuator dynamics, generator dynamics and feedback-control transients are not represented.

## 11. Operating-envelope diagnostics

Wind-speed sweeps were used to check station convergence, induction-factor ranges, Prandtl loss factor, iteration count, angle-of-attack range and airfoil-polar coverage. The high-wind cases revealed outboard load reversal as large pitch angles moved sections to negative angle of attack. The resulting sign change in flapwise displacement is retained in the final interpretation.

## 12. Centrifugal tension and rotating beam FEM

The rotating blade carries axial centrifugal tension obtained by integrating `m'(r)*Omega^2*r` from each station to the tip. A two-DOF-per-node Euler-Bernoulli beam FEM was assembled. Each element contains elastic bending stiffness and tensile geometric stiffness, and distributed aerodynamic load is applied using a consistent beam load vector. Cantilever root displacement and rotation are fixed.

The non-rotating FEM was cross-checked against the numerical integration model: approximately 17.0427 m versus 17.0701 m, a difference of about -0.16%. At 7.56 rpm, centrifugal stiffening reduced the baseline predicted deflection by roughly 8.64% relative to the non-rotating FEM. The rotating FEM was therefore used for the final structural comparisons.

## 13. Gravity and edgewise loading

Gravity is represented as a sinusoidal 1P edgewise load over rotor azimuth. The root-moment cycle combines a steady aerodynamic edgewise contribution and the gravity-induced periodic component. This exposed a drawback of the +1000 kg intermediate design: added mass increases gravity-driven cyclic loading.

## 14. Fatigue screening

A simple S-N sensitivity was first applied over representative exponents m=6, 8, 10 and 12. For optimization, a DEL-style proxy with m=10 and N_ref=1e7 was used. This is a screening metric, not an IEC rainflow-counted fatigue result.

## 15. Modal analysis and Campbell diagram

The rotating beam stiffness and consistent mass matrices are used in the generalized eigenproblem `K phi = lambda M phi`. First flapwise and edgewise modes are tracked against 1P and 3P excitation across the rotor-speed range. At rated speed, 1P is approximately 0.126 Hz and 3P approximately 0.378 Hz. The final surrogate search imposes a minimum flapwise 3P margin of about 0.145 Hz.

## 16. Simplified gust

The study uses a +20% frozen-control gust at 12.708 m/s with 7.56 rpm and 0° pitch held fixed. This is not an IEC extreme-operating-gust simulation; it is a consistent reduced-order load-alleviation comparison.

## 17. AEP proxy

A Weibull distribution with shape k=2 and mean wind speed 9 m/s is used to weight the controlled aerodynamic power curve. The corresponding scale is about 10.155 m/s. One-metre-per-second bins from 4–25 m/s represented approximately 88.6% of the selected Weibull probability. Electrical losses, availability, wakes, curtailment and site-specific losses are not included.

## 18. Unified four-variable design model

Each candidate is parameterized by peak smooth twist, aerodynamic start, structural start and local flapwise EI increase. The design ranges are 0–2°, 70–77 m, 70–85 m, and 0–30%, respectively. For every candidate, the unified physics evaluator returns rated aerodynamics, rotating structural response, simplified gust response, gravity amplitude, DEL10 proxy, first flap/edge frequencies, and 3P margins.

## 19. Physics-generated ML database

A 300-point four-dimensional Latin Hypercube DOE (seed 42) is evaluated with the physics model. The resulting table is a physics-generated supervised-learning database.

## 20. Surrogate models

Three regressors are compared: Random Forest with 400 trees, Extra Trees with 400 trees, and Gradient Boosting with 300 estimators, learning rate 0.04 and max depth 3. The 300 designs are split 80/20 into 240 training and 60 holdout designs. Metrics include R², MAE and RMSE. Five-fold shuffled cross-validation with seed 42 is then used to select the best model independently for each target response.

## 21. Surrogate-assisted search

A second 100,000-point Latin Hypercube sample (seed 123) is evaluated with the selected target-specific surrogates. Hard constraints include approximately Cp >= 0.99*Cp_baseline, added mass <= 1000 kg/blade, and flapwise 3P margin >= 0.145 Hz. The core Pareto objectives are rated root moment, rated rotating tip deflection, DEL10 proxy and added structural mass.

## 22. Full physics re-verification

The core surrogate Pareto set contained 152 designs. Every one was passed back through the reduced-order physics evaluator. After exact physics filtering, 102 remained feasible and 54 remained on the physics-verified Pareto front. A final fatigue filter required no more than 1% DEL10-proxy penalty, leaving 17 candidates.

## 23. Balanced final selection

The four final objectives are min-max normalized and treated with equal importance. The selected candidate minimizes Euclidean distance to the normalized utopia point. The resulting candidate is approximately 1.4993° peak smooth twist, 76.911 m aerodynamic start, 81.856 m structural start, 0.0609% EI increase, and 2.01 kg/blade added mass. The near-zero structural reinforcement is an emergent result: within this reduced-order design space, the useful trade-off is predominantly aerodynamic.

## 24. Final verification

The final candidate is rerun with the same controller as the baseline across 4–25 m/s. Final reported reduced-order results are approximately 5.65% rated root-moment reduction, 7.23% rated rotating tip-deflection reduction, 4.99% simplified gust root-moment reduction, +0.01% DEL10-proxy change, and -0.078% aerodynamic AEP-proxy change.

At 22–25 m/s the outboard load-reversal regime produces a somewhat larger negative deflection magnitude for the optimized blade. This is treated as a real trade-off rather than discarded.

## 25. Interpretation boundary

The study produces a **reduced-order design hypothesis**. It does not establish certification, manufacturability, ultimate/fatigue safety, or superiority of a complete turbine system. The next fidelity step would be full aeroelastic load-case validation, detailed composite design and, where justified, higher-fidelity aerodynamic analysis.
