# References and Upstream Data

This project separates its own analysis code, generated results and optimization workflow from the public reference turbine inputs used as the engineering baseline.

## Primary turbine reference

**Gaertner, E., Rinker, J., Sethuraman, L., Zahle, F., Anderson, B., Barter, G., Abbas, N., Meng, F., Bortolotti, P., Skrzypinski, W., Scott, G., Feil, R., Bredmose, H., Dykes, K., Shields, M., Allen, C., and Viselli, A.**  
*Definition of the IEA 15-Megawatt Offshore Reference Wind Turbine.*  
NREL/TP-5000-75698, National Renewable Energy Laboratory, 2020.

## Public reference repository

IEA Wind Systems / IEA Wind Task 37 reference model:

- Repository: `https://github.com/IEAWindSystems/IEA-15-240-RWT`
- Model family: IEA-15-240-RWT

The public repository provides reference geometry, structural properties and AeroDyn/OpenFAST inputs used as source material for this study. The local fetch workflow records the upstream license with downloaded files.

## Methods used in this repository

The implementation combines established engineering methods rather than claiming invention of the underlying physical theories:

- Blade Element Momentum theory for rotor aerodynamics;
- Prandtl tip/hub loss corrections;
- Buhl-type high-induction treatment;
- Euler-Bernoulli beam mechanics;
- finite-element geometric stiffness from centrifugal axial tension;
- eigenvalue-based reduced-order modal analysis;
- Weibull-distribution annual-energy proxy;
- Latin Hypercube Sampling for design-of-experiments;
- Random Forest, Extra Trees and Gradient Boosting regression;
- non-dominated Pareto filtering and normalized utopia-distance selection.

## Attribution boundary

The following are external/public reference inputs:

- IEA 15-MW blade geometry;
- IEA/OpenFAST structural distributions;
- AeroDyn airfoil polar data;
- selected reference design-point values used for baseline comparison.

The following are project-generated:

- Python BEM implementation;
- load integration and rotating-beam FEM workflow;
- controller approximation;
- structural/aerodynamic design parameterization;
- gust, gravity, fatigue-proxy and modal screening logic;
- physics database generation;
- surrogate-model comparison and validation;
- large design-space search;
- Pareto filtering and physics re-verification;
- generated plots, tables and final candidate metrics.

## Citation

If this repository is referenced externally, cite both this software repository and the upstream IEA 15-MW reference source. See the root `CITATION.cff` file for the software citation metadata.
