# Assumptions and limitations

The credibility of this project depends on being explicit about what the models do and do not represent.

| Area | Study assumption | Consequence |
|---|---|---|
| Aerodynamics | steady BEM | no transient wake/aeroelastic dynamics |
| Inflow | axisymmetric, quasi-steady | no turbulent realization, shear, yaw or veer |
| Air density | 1.225 kg/m³ | fixed standard-density comparison |
| Airfoil data | station-specific 2D AeroDyn polars | no 3D rotational correction beyond what is implicit in source data |
| Finite-blade effects | Prandtl hub/tip losses | reduced-order loss model |
| High induction | Buhl-type correction | avoids classical momentum breakdown in high-loading region |
| Dynamic stall | not modeled | high-rate transient response is outside scope |
| Aeroelastic feedback | no iterative deformed-geometry BEM | aerodynamic loads are not recomputed on the deflected blade |
| Structural model | Euler-Bernoulli beam | no shear deformation or detailed shell behavior |
| Torsion | neglected | no bend-twist/torsional aeroelastic coupling |
| Composite structure | not modeled explicitly | no ply-level stresses, failure indices or buckling |
| EI tailoring | prescribed local percentage change | concept-level rather than laminate-level design |
| Added mass | local mass fraction ≈ local EI fraction | screening proxy, not structural sizing |
| Rotation | centrifugal tension/geometric stiffness included | first-order rotating-blade stiffening captured |
| Gravity | sinusoidal 1P edgewise approximation | not a full rotating aeroelastic load history |
| Gust | +20% frozen-control steady gust | comparison metric, not an IEC DLC |
| Fatigue | DEL10-style gravity proxy | not rainflow counting or certified fatigue life |
| Modes | reduced-order blade-only modal FEM | no full turbine coupled modes |
| Controller | steady rpm/pitch schedule | no actuator/generator/control-loop dynamics |
| Power | aerodynamic rotor power | not electrical net power |
| AEP | Weibull aerodynamic-energy proxy | no wakes, downtime, losses, availability or curtailment |
| ML validity | interpolation within sampled design bounds | no extrapolation claim |
| Final verification | same reduced-order physics model | not independent OpenFAST/CFD/experimental validation |

## High-wind load reversal

Above-rated pitch control drives the outboard blade into negative angle-of-attack conditions at high wind speeds. The final rotating-deflection envelope therefore crosses zero and becomes negative. The optimized candidate has a somewhat larger absolute negative tip displacement at 22–25 m/s. Because the absolute values near the zero crossing are small compared with the maximum below-rated deflection, percentage “reduction” metrics become misleading there; the repository reports signed and absolute displacement instead.

## Claims that are supported

It is appropriate to state that the project:

- developed and validated a reduced-order BEM baseline against selected reference design-point quantities;
- coupled distributed BEM loads to non-rotating and rotating beam models;
- quantified structural, aerodynamic, gust, fatigue-proxy and modal trade-offs;
- trained accurate surrogate models on a physics-generated DOE;
- used the surrogates to screen a large bounded design space;
- re-ran the Pareto candidates through the reduced-order physics solver;
- identified a candidate that improves selected modeled load/deflection metrics with a small aerodynamic performance penalty.

## Claims that are not supported

Do **not** describe the project as:

- an IEC-certified turbine redesign;
- proof that the IEA 15-MW reference design is inferior;
- a complete aeroelastic optimization;
- a validated fatigue-life prediction;
- a composite blade design;
- a bankable AEP study;
- an AI system that independently designed a turbine.
