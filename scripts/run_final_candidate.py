#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from aerostruct15mw.aep import aerodynamic_aep_proxy, wind_bin_probabilities
from aerostruct15mw.bem import evaluate_bem_geometry
from aerostruct15mw.config import FinalDesign, TurbineConfig
from aerostruct15mw.control import rotor_rpm_schedule, solve_pitch_for_target_power
from aerostruct15mw.design import build_aerostruct_candidate
from aerostruct15mw.io import load_processed_reference_data
from aerostruct15mw.plotting import plot_power_curve, plot_root_moment_envelope, plot_tip_deflection_envelope
from aerostruct15mw.structures import centrifugal_tension_from_rpm, solve_rotating_beam_fem
ROOT = Path(__file__).resolve().parents[1]

def structural_arrays(geometry, structural):
    span = geometry["span_m"].to_numpy()
    struct_span = structural["span_fraction"].to_numpy() * geometry["span_m"].max()
    flap_ei = np.interp(span, struct_span, structural["flap_EI_Nm2"])
    edge_ei = np.interp(span, struct_span, structural["edge_EI_Nm2"])
    mass = np.interp(span, struct_span, structural["mass_density_kgpm"])
    return span, flap_ei, edge_ei, mass

def evaluate_operating_point(geometry, polars, u, target_power, cfg):
    rpm = rotor_rpm_schedule(u, cfg)
    if u <= cfg.rated_wind_mps:
        pitch = 0.0
        bem, summary = evaluate_bem_geometry(geometry, polars, wind_speed_mps=u, rotor_rpm=rpm, pitch_deg=0.0, config=cfg)
    else:
        pitch, _ = solve_pitch_for_target_power(geometry, polars, u, rpm, target_power, cfg)
        bem, summary = evaluate_bem_geometry(geometry, polars, wind_speed_mps=u, rotor_rpm=rpm, pitch_deg=pitch, config=cfg)
    return bem, summary, rpm, pitch

def main():
    cfg = TurbineConfig(); final = FinalDesign()
    geometry, structural = load_processed_reference_data(ROOT / "data" / "processed")
    polars = ROOT / "data" / "reference" / "airfoils"
    span, flap_ei, _, mass = structural_arrays(geometry, structural)
    candidate = build_aerostruct_candidate(geometry, span, flap_ei, mass, final.peak_twist_deg, final.aero_start_m, final.struct_start_m, final.ei_increase_percent)
    base_bem, base_rated = evaluate_bem_geometry(geometry, polars, label="IEA baseline", wind_speed_mps=cfg.rated_wind_mps, rotor_rpm=cfg.rpm_rated, pitch_deg=0.0, config=cfg)
    opt_bem, opt_rated = evaluate_bem_geometry(candidate.geometry, polars, label="Optimized", wind_speed_mps=cfg.rated_wind_mps, rotor_rpm=cfg.rpm_rated, pitch_deg=0.0, config=cfg)
    target_power = base_rated["power_MW"]
    base_ncf = centrifugal_tension_from_rpm(span, mass, cfg.rpm_rated, cfg.rotor_radius_m)
    opt_ncf = centrifugal_tension_from_rpm(span, candidate.mass_density, cfg.rpm_rated, cfg.rotor_radius_m)
    base_struct = solve_rotating_beam_fem(span, base_bem["normal_Npm"], flap_ei, base_ncf)
    opt_struct = solve_rotating_beam_fem(span, opt_bem["normal_Npm"], candidate.ei, opt_ncf)
    winds = np.arange(4.0, 26.0, 1.0)
    rows = []
    for u in winds:
        b_bem, b_sum, b_rpm, b_pitch = evaluate_operating_point(geometry, polars, float(u), target_power, cfg)
        o_bem, o_sum, o_rpm, o_pitch = evaluate_operating_point(candidate.geometry, polars, float(u), target_power, cfg)
        b_ncf = centrifugal_tension_from_rpm(span, mass, b_rpm, cfg.rotor_radius_m)
        o_ncf = centrifugal_tension_from_rpm(span, candidate.mass_density, o_rpm, cfg.rotor_radius_m)
        b_st = solve_rotating_beam_fem(span, b_bem["normal_Npm"].to_numpy(), flap_ei, b_ncf)
        o_st = solve_rotating_beam_fem(span, o_bem["normal_Npm"].to_numpy(), candidate.ei, o_ncf)
        rows.append({"wind_mps": u, "baseline_rpm": b_rpm, "optimized_rpm": o_rpm, "baseline_pitch_deg": b_pitch, "optimized_pitch_deg": o_pitch, "baseline_power_MW": b_sum["power_MW"], "optimized_power_MW": o_sum["power_MW"], "baseline_root_MNm": b_sum["root_moment_MNm"], "optimized_root_MNm": o_sum["root_moment_MNm"], "baseline_tip_m": b_st["tip_deflection_m"], "optimized_tip_m": o_st["tip_deflection_m"]})
    envelope = pd.DataFrame(rows)
    probability = wind_bin_probabilities(winds, k=2.0, mean_wind_mps=9.0)
    base_curve = pd.DataFrame({"power_MW": envelope["baseline_power_MW"]}); opt_curve = pd.DataFrame({"power_MW": envelope["optimized_power_MW"]})
    base_aep, _ = aerodynamic_aep_proxy(base_curve, probability); opt_aep, _ = aerodynamic_aep_proxy(opt_curve, probability)
    tables = ROOT / "results" / "tables"; figs = ROOT / "results" / "figures"
    tables.mkdir(parents=True, exist_ok=True); figs.mkdir(parents=True, exist_ok=True)
    envelope.to_csv(tables / "recomputed_operating_envelope.csv", index=False)
    plot_power_curve(envelope, figs / "recomputed_power_curve.png")
    plot_root_moment_envelope(envelope, cfg.rated_wind_mps, figs / "recomputed_root_moment_envelope.png")
    plot_tip_deflection_envelope(envelope, cfg.rated_wind_mps, figs / "recomputed_tip_deflection_envelope.png")
    print("FINAL PHYSICS-VERIFIED CANDIDATE")
    print("--------------------------------")
    print(f"Peak smooth twist: {final.peak_twist_deg:.6f} deg")
    print(f"Aerodynamic start: {final.aero_start_m:.3f} m")
    print(f"EI increase: {final.ei_increase_percent:.6f}%")
    print(f"Added mass: {candidate.added_mass_kg:.3f} kg/blade")
    print(f"Rated Cp: {opt_rated['Cp']:.6f}")
    print(f"Rated root moment reduction: {(1-opt_rated['root_moment_MNm']/base_rated['root_moment_MNm'])*100:.3f}%")
    print(f"Rated rotating tip reduction: {(1-opt_struct['tip_deflection_m']/base_struct['tip_deflection_m'])*100:.3f}%")
    print(f"Aerodynamic AEP proxy change: {(opt_aep/base_aep-1)*100:.3f}%")

if __name__ == "__main__":
    main()
