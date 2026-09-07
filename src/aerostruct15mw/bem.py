from __future__ import annotations

from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from .config import TurbineConfig
from .io import read_aerodyn_polar


def solve_bem_station(
    station_index: int,
    geometry: pd.DataFrame,
    polar_folder: str | Path,
    wind_speed_mps: float = 10.59,
    rotor_rpm: float = 7.56,
    pitch_deg: float = 0.0,
    config: TurbineConfig | None = None,
    polar_reader: Callable = read_aerodyn_polar,
):
    """Solve one BEM station with Prandtl losses and Buhl high-induction correction."""
    cfg = config or TurbineConfig()
    polar_folder = Path(polar_folder)
    blade_length_m = float(geometry["span_m"].max())
    hub_radius_m = cfg.rotor_radius_m - blade_length_m
    span_m = float(geometry["span_m"].iloc[station_index])
    chord_m = float(geometry["chord_m"].iloc[station_index])
    twist_deg = float(geometry["twist_deg"].iloc[station_index])
    r = hub_radius_m + span_m
    omega = rotor_rpm * 2.0 * np.pi / 60.0

    if station_index == 0 or station_index == len(geometry) - 1:
        return {"station": station_index, "span_m": span_m, "r_m": r, "a": np.nan, "a_prime": np.nan, "F": 0.0, "phi_deg": np.nan, "alpha_deg": np.nan, "Cl": np.nan, "Cd": np.nan, "normal_Npm": 0.0, "tangential_Npm": 0.0, "iterations": 0, "converged": True}

    sigma = cfg.blades * chord_m / (2.0 * np.pi * r)
    polar_file = polar_folder / f"IEA-15-240-RWT_AeroDyn15_Polar_{station_index:02d}.dat"
    polar = polar_reader(polar_file)
    a = 0.30
    a_prime = 0.01
    converged = False
    Vrel = phi = 0.0
    phi_deg = alpha_deg = Cl = Cd = F = 0.0

    for iteration in range(cfg.bem_max_iterations):
        v_axial = wind_speed_mps * (1.0 - a)
        v_tangential = omega * r * (1.0 + a_prime)
        Vrel = np.sqrt(v_axial**2 + v_tangential**2)
        phi = np.arctan2(v_axial, v_tangential)
        phi_deg = np.degrees(phi)
        alpha_deg = phi_deg - twist_deg - pitch_deg
        Cl = np.interp(alpha_deg, polar["alpha_deg"], polar["Cl"])
        Cd = np.interp(alpha_deg, polar["alpha_deg"], polar["Cd"])
        cn = Cl * np.cos(phi) + Cd * np.sin(phi)
        ct = Cl * np.sin(phi) - Cd * np.cos(phi)
        sin_phi = max(abs(np.sin(phi)), 1e-6)
        cos_phi = np.cos(phi)
        f_tip = (cfg.blades / 2.0) * (cfg.rotor_radius_m - r) / (r * sin_phi)
        f_hub = (cfg.blades / 2.0) * (r - hub_radius_m) / (hub_radius_m * sin_phi)
        f_tip_loss = 2.0 / np.pi * np.arccos(np.exp(-max(f_tip, 0.0)))
        f_hub_loss = 2.0 / np.pi * np.arccos(np.exp(-max(f_hub, 0.0)))
        F = max(f_tip_loss * f_hub_loss, 1e-4)
        cn_safe = np.sign(cn) * max(abs(cn), 1e-8)
        k = sigma * cn_safe / (4.0 * F * sin_phi**2)
        if k <= 2.0 / 3.0:
            a_new = k / (1.0 + k)
        else:
            gamma1 = 2.0 * F * k - (10.0 / 9.0 - F)
            gamma2 = 2.0 * F * k - (4.0 / 3.0 - F) * F
            gamma3 = 2.0 * F * k - (25.0 / 9.0 - 2.0 * F)
            gamma2 = max(gamma2, 0.0)
            a_new = (gamma1 - np.sqrt(gamma2)) / gamma3 if abs(gamma3) > 1e-8 else a
        ct_safe = np.sign(ct) * max(abs(ct), 1e-8)
        denominator = 4.0 * F * sin_phi * cos_phi
        k_prime = sigma * ct_safe / denominator
        a_prime_new = k_prime / (1.0 - k_prime) if abs(1.0 - k_prime) > 1e-8 else a_prime
        a_new = np.clip(a_new, 0.0, 0.95)
        a_prime_new = np.clip(a_prime_new, -0.5, 0.5)
        a_updated = (1.0 - cfg.bem_relaxation) * a + cfg.bem_relaxation * a_new
        ap_updated = (1.0 - cfg.bem_relaxation) * a_prime + cfg.bem_relaxation * a_prime_new
        error_a = abs(a_updated - a)
        error_ap = abs(ap_updated - a_prime)
        a, a_prime = a_updated, ap_updated
        if error_a < cfg.bem_tolerance and error_ap < cfg.bem_tolerance:
            converged = True
            break

    q = 0.5 * cfg.air_density_kgpm3 * Vrel**2
    lift_npm = q * chord_m * Cl
    drag_npm = q * chord_m * Cd
    normal_npm = lift_npm * np.cos(phi) + drag_npm * np.sin(phi)
    tangential_npm = lift_npm * np.sin(phi) - drag_npm * np.cos(phi)
    return {"station": station_index, "span_m": span_m, "r_m": r, "a": a, "a_prime": a_prime, "F": F, "phi_deg": phi_deg, "alpha_deg": alpha_deg, "Cl": Cl, "Cd": Cd, "normal_Npm": normal_npm, "tangential_Npm": tangential_npm, "iterations": iteration + 1, "converged": converged}


def evaluate_bem_geometry(
    geometry: pd.DataFrame,
    polar_folder: str | Path,
    label: str = "Design",
    wind_speed_mps: float = 10.59,
    rotor_rpm: float = 7.56,
    pitch_deg: float = 0.0,
    config: TurbineConfig | None = None,
):
    """Evaluate all blade stations and integrate thrust, torque, power and root moment."""
    cfg = config or TurbineConfig()
    rows = [solve_bem_station(i, geometry, polar_folder, wind_speed_mps, rotor_rpm, pitch_deg, cfg) for i in range(len(geometry))]
    results = pd.DataFrame(rows)
    span = results["span_m"].to_numpy()
    normal = results["normal_Npm"].to_numpy()
    tangential = results["tangential_Npm"].to_numpy()
    hub_radius_m = cfg.rotor_radius_m - float(geometry["span_m"].max())
    radius = span + hub_radius_m
    omega = rotor_rpm * 2.0 * np.pi / 60.0
    area = np.pi * cfg.rotor_radius_m**2
    thrust_n = cfg.blades * np.trapezoid(normal, span)
    torque_nm = cfg.blades * np.trapezoid(tangential * radius, span)
    power_w = torque_nm * omega
    available_w = 0.5 * cfg.air_density_kgpm3 * area * wind_speed_mps**3
    cp = power_w / available_w
    ct = thrust_n / (0.5 * cfg.air_density_kgpm3 * area * wind_speed_mps**2)
    root_moment_nm = np.trapezoid(normal * span, span)
    summary = {"label": label, "wind_speed_mps": wind_speed_mps, "rotor_rpm": rotor_rpm, "pitch_deg": pitch_deg, "Cp": cp, "Ct": ct, "power_MW": power_w / 1e6, "thrust_MN": thrust_n / 1e6, "torque_MNm": torque_nm / 1e6, "root_moment_MNm": root_moment_nm / 1e6}
    return results, summary
