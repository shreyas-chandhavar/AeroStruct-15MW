# Reference data

The public repository intentionally does **not** commit a second copy of the upstream IEA 15-MW reference data by default.

Run:

```bash
python scripts/fetch_reference_data.py
```

The script downloads the required files from the official IEA Wind Systems `IEA-15-240-RWT` repository, including blade geometry, ElastoDyn structural properties, 50 AeroDyn polar files, and the upstream license. It then generates `data/processed/iea15_geometry.csv` and `data/processed/iea15_structural_properties.csv`.

## Attribution

Official source: https://github.com/IEAWindSystems/IEA-15-240-RWT

The reference turbine inputs are not original work of AeroStruct-15MW. The analysis code, numerical models, optimization workflow, surrogate modelling and generated study results are separate project work.

The upstream IEA repository is licensed under Apache License 2.0. The fetch script stores a local copy of that upstream license beside the downloaded reference files.
