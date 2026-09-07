#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import numpy as np
from aerostruct15mw.bem import evaluate_bem_geometry
from aerostruct15mw.config import REFERENCE_AERO_POWER_MW, REFERENCE_CP, REFERENCE_CT, TurbineConfig
from aerostruct15mw.io import load_processed_reference_data
from aerostruct15mw.structures import centrifugal_tension_from_rpm, solve_rotating_beam_fem
ROOT = Path(__file__).resolve().parents[1]

def main():
    cfg = TurbineConfig()
    geometry, structural = load_processed_reference_data(ROOT / "data" / "processed")
    polars = ROOT / "data" / "reference" / "airfoils"
    bem, summary = evaluate_bem_geometry(geometry, polars, label="IEA baseline", wind_speed_mps=cfg.rated_wind_mps, rotor_rpm=cfg.rpm_rated, pitch_deg=0.0, config=cfg)
    span = bem["span_m"].to_numpy()
    struct_span = structural["span_fraction"].to_numpy() * geometry["span_m"].max()
    flap_ei = np.interp(span, struct_span, structural["flap_EI_Nm2"])
    mass = np.interp(span, struct_span, structural["mass_density_kgpm"])
    ncf = centrifugal_tension_from_rpm(span, mass, cfg.rpm_rated, cfg.rotor_radius_m)
    rotating = solve_rotating_beam_fem(span, bem["normal_Npm"], flap_ei, ncf)
    print("IEA 15-MW REDUCED-ORDER BASELINE")
    print("--------------------------------")
    print(f"Cp: {summary['Cp']:.6f}  | reference {REFERENCE_CP:.3f} | error {(summary['Cp']/REFERENCE_CP-1)*100:.3f}%")
    print(f"Ct: {summary['Ct']:.6f}  | reference {REFERENCE_CT:.3f} | error {(summary['Ct']/REFERENCE_CT-1)*100:.3f}%")
    print(f"Aerodynamic power: {summary['power_MW']:.3f} MW | reference {REFERENCE_AERO_POWER_MW:.3f} MW")
    print(f"Flapwise root moment: {summary['root_moment_MNm']:.3f} MN·m")
    print(f"Rotating FEM tip deflection: {rotating['tip_deflection_m']:.3f} m")
    print(f"Rotating FEM tip rotation: {rotating['tip_rotation_deg']:.2f} deg")

if __name__ == "__main__":
    main()
