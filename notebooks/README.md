# Notebooks

This directory contains the cleaned public notebook entry point for AeroStruct-15MW.

## `01_end_to_end_workflow.ipynb`

This notebook demonstrates the complete public workflow using the modular `aerostruct15mw` Python package:

1. install the package;
2. fetch the public IEA 15-MW reference inputs;
3. reproduce the BEM baseline;
4. solve the rotating structural response;
5. reconstruct the final physics-verified design;
6. compare rated baseline and optimized metrics;
7. regenerate the 4–25 m/s controlled envelope;
8. optionally re-run the surrogate-assisted optimization.

The original exploratory Colab notebook is intentionally not part of the main branch. It contains the development history, discarded experiments and intermediate debugging cells. Keeping it out of the public repository makes the final project easier to audit and reproduce.

For the detailed derivation and project history, use:

- `../docs/methodology.md`
- `../docs/model_validation.md`
- `../docs/ml_surrogate_workflow.md`
- `../docs/assumptions_and_limitations.md`
- `../docs/reproducibility.md`
