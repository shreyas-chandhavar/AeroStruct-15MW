# Reproducibility Guide

This document gives the shortest reproducible path from a fresh clone to the key AeroStruct-15MW results.

## 1. Clone and install

```bash
git clone https://github.com/shreyas-chandhavar/AeroStruct-15MW.git
cd AeroStruct-15MW
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .
```

## 2. Fetch public IEA reference inputs

```bash
python scripts/fetch_reference_data.py
```

Expected outcome:

- public IEA-15-240-RWT geometry and structural files are downloaded;
- the required AeroDyn polar files are placed under `data/reference/`;
- processed geometry/structural CSVs are generated under `data/processed/`;
- upstream licensing information is retained locally.

## 3. Reproduce the aerodynamic baseline

```bash
python scripts/run_baseline.py
```

Reference checkpoints from the completed study are approximately:

- `Cp ≈ 0.4924`
- `Ct ≈ 0.8021`
- aerodynamic power `≈ 16.204 MW`
- flapwise root moment `≈ 63.108 MN·m`

These should be interpreted as reduced-order design-point checks rather than certification quantities.

## 4. Recompute the final candidate and controlled envelope

```bash
python scripts/run_final_candidate.py
```

The final physics-verified design parameters are approximately:

- peak smooth outboard twist: `1.499°`
- aerodynamic modification start: `76.91 m`
- structural modification start: `81.86 m`
- flapwise EI increase: `0.061%`
- added mass: `≈2.01 kg/blade`

Representative final-study checkpoints are approximately:

- rated flapwise root moment reduction: `5.65%`
- rated rotating-tip-deflection reduction: `7.23%`
- simplified +20% frozen-control gust root-moment reduction: `4.99%`
- DEL10 proxy change: `≈ +0.01%`
- aerodynamic AEP proxy change: `≈ -0.078%`

The script also regenerates the final operating-envelope comparison data and plots.

## 5. Re-run the surrogate workflow

```bash
python scripts/run_ml_pipeline.py
```

The workflow uses:

- 300-point Latin Hypercube physics DOE;
- 240/60 train/test split;
- Random Forest, Extra Trees and Gradient Boosting models;
- holdout metrics and five-fold cross-validation;
- 100,000-design surrogate screening;
- engineering feasibility constraints;
- core Pareto filtering.

For full reduced-order physics verification of surrogate Pareto candidates:

```bash
python scripts/run_ml_pipeline.py --verify-pareto
```

Completed-study checkpoints:

- surrogate core Pareto candidates: `152`
- physics-feasible after exact re-evaluation: `102`
- final physics Pareto designs: `54`
- designs satisfying the final ≤1% DEL-proxy penalty: `17`

## 6. Run the test suite

```bash
pytest
```

GitHub Actions also executes the tests on Python 3.10, 3.11 and 3.12.

## 7. Public notebook

The cleaned notebook entry point is:

```text
notebooks/01_end_to_end_workflow.ipynb
```

It intentionally calls the modular package instead of duplicating the original exploratory Colab development history.

## Reproducibility scope

The repository reproduces the reduced-order workflow documented here. It does not reproduce a full IEC/OpenFAST load campaign, CFD validation, detailed composite sizing or experimental certification. See `docs/assumptions_and_limitations.md` for the complete scope boundary.
