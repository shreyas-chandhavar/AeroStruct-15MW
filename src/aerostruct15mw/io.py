from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_aerodyn_polar(file_path: str | Path) -> pd.DataFrame:
    """Read an AeroDyn airfoil polar table by locating the NumAlf block."""
    file_path = Path(file_path)
    lines = file_path.read_text().splitlines()

    number_of_points = None
    table_start = None
    for i, line in enumerate(lines):
        if "NumAlf" in line:
            number_of_points = int(line.split()[0])
            table_start = i + 1
            break

    if number_of_points is None or table_start is None:
        raise ValueError(f"NumAlf not found in polar file: {file_path}")

    polar_data: list[list[float]] = []
    for line in lines[table_start:]:
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        try:
            alpha, cl, cd, cm = map(float, parts[:4])
        except ValueError:
            continue
        polar_data.append([alpha, cl, cd, cm])
        if len(polar_data) == number_of_points:
            break

    if len(polar_data) != number_of_points:
        raise ValueError(f"Expected {number_of_points} aerodynamic rows but found {len(polar_data)}")

    return pd.DataFrame(polar_data, columns=["alpha_deg", "Cl", "Cd", "Cm"])


def parse_aerodyn_blade(file_path: str | Path) -> pd.DataFrame:
    """Parse the public IEA AeroDyn blade table into the geometry used here."""
    lines = Path(file_path).read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if "BlSpn" in line) + 2
    rows = []
    for line in lines[start:]:
        parts = line.split()
        if len(parts) < 7:
            continue
        try:
            vals = [float(parts[j]) for j in range(6)]
            afid = int(float(parts[6]))
        except ValueError:
            continue
        rows.append([vals[0], vals[4], vals[5], afid])
    if not rows:
        raise ValueError(f"No AeroDyn blade rows found in {file_path}")
    return pd.DataFrame(rows, columns=["span_m", "twist_deg", "chord_m", "airfoil_id"])


def parse_elastodyn_blade(file_path: str | Path) -> pd.DataFrame:
    """Parse mass and flap/edge stiffness from the IEA ElastoDyn blade file."""
    lines = Path(file_path).read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if "BlFract" in line) + 2
    rows = []
    for line in lines[start:]:
        parts = line.split()
        if len(parts) < 6:
            continue
        try:
            vals = [float(parts[j]) for j in range(6)]
        except ValueError:
            continue
        rows.append(vals)
        if len(rows) == 50:
            break
    if not rows:
        raise ValueError(f"No ElastoDyn blade rows found in {file_path}")
    return pd.DataFrame(rows, columns=["span_fraction", "pitch_axis", "struct_twist_deg", "mass_density_kgpm", "flap_EI_Nm2", "edge_EI_Nm2"])


def load_processed_reference_data(data_dir: str | Path):
    """Load the two processed CSV files produced by fetch_reference_data.py."""
    data_dir = Path(data_dir)
    geometry = pd.read_csv(data_dir / "iea15_geometry.csv")
    structural = pd.read_csv(data_dir / "iea15_structural_properties.csv")
    return geometry, structural
