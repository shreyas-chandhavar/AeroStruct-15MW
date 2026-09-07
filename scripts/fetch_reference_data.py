#!/usr/bin/env python3
"""Fetch only the public IEA 15-MW inputs required by this repository."""
from __future__ import annotations
from pathlib import Path
import requests
from aerostruct15mw.io import parse_aerodyn_blade, parse_elastodyn_blade
ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "reference"
PROCESSED = ROOT / "data" / "processed"
BASE = "https://raw.githubusercontent.com/IEAWindSystems/IEA-15-240-RWT/master/"
OPENFAST = BASE + "OpenFAST/IEA-15-240-RWT/"

def download(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    dest.write_bytes(response.content)
    print(f"Downloaded {dest.relative_to(ROOT)}")

def main():
    REFERENCE.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    aero_raw = REFERENCE / "IEA-15-240-RWT_AeroDyn15_blade.dat"
    struct_raw = REFERENCE / "IEA-15-240-RWT_ElastoDyn_blade.dat"
    download(OPENFAST + aero_raw.name, aero_raw)
    download(OPENFAST + struct_raw.name, struct_raw)
    download(BASE + "LICENSE", REFERENCE / "IEA15_UPSTREAM_LICENSE.txt")
    polar_dir = REFERENCE / "airfoils"
    for i in range(50):
        name = f"IEA-15-240-RWT_AeroDyn15_Polar_{i:02d}.dat"
        download(OPENFAST + "Airfoils/" + name, polar_dir / name)
    geometry = parse_aerodyn_blade(aero_raw)
    structural = parse_elastodyn_blade(struct_raw)
    geometry.to_csv(PROCESSED / "iea15_geometry.csv", index=False)
    structural.to_csv(PROCESSED / "iea15_structural_properties.csv", index=False)
    source_note = """# IEA 15-MW reference data\n\nSource: IEA Wind Systems — IEA-15-240-RWT\n\nOfficial repository: https://github.com/IEAWindSystems/IEA-15-240-RWT\n\nThis project uses the public blade geometry, ElastoDyn distributed structural properties, and AeroDyn polar tables as reference inputs. These inputs are not original work of AeroStruct-15MW. The upstream repository is licensed under Apache License 2.0; the downloaded license is stored alongside the fetched data.\n\nRecommended technical reference: Gaertner et al., *Definition of the IEA 15-Megawatt Offshore Reference Wind Turbine*, NREL/TP-5000-75698, 2020.\n"""
    (REFERENCE / "DATA_SOURCE.md").write_text(source_note)
    print("Processed CSV files written to data/processed/")

if __name__ == "__main__":
    main()
