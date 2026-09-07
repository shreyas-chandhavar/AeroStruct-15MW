from __future__ import annotations

import numpy as np
import pandas as pd

from .bem import evaluate_bem_geometry
from .config import TurbineConfig


def below_rated_rpm(wind_speed_mps: float, config: TurbineConfig | None = None) -> float:
    cfg = config or TurbineConfig()
    omega_target = cfg.lambda_opt * wind_speed_mps / cfg.rotor_radius_m
    rpm_target = omega_target * 60.0 / (2.0 * np.pi)
    return float(np.clip(rpm_target, cfg.rpm_min, cfg.rpm_rated))


def rotor_rpm_schedule(wind_speed_mps: float, config: TurbineConfig | None = None) -> float:
    cfg = config or TurbineConfig()
    return below_rated_rpm(wind_speed_mps, cfg) if wind_speed_mps <= cfg.rated_wind_mps else cfg.rpm_rated


def solve_pitch_for_target_power(
    geometry: pd.DataFrame,
    polar_folder,
    wind_speed_mps: float,
    rotor_rpm: float,
    target_power_mw: float,
    config: TurbineConfig | None = None,
):
    """Steady-state bisection pitch controller used above rated."""
    cfg = config or TurbineConfig()
    low, high = cfg.pitch_low_deg, cfg.pitch_high_deg

    _, summary_low = evaluate_bem_geometry(
        geometry,
        polar_folder,
        label="Pitch search",
        wind_speed_mps=wind_speed_mps,
        rotor_rpm=rotor_rpm,
        pitch_deg=low,
        config=cfg,
    )
    if summary_low["power_MW"] <= target_power_mw:
        return low, summary_low

    _, summary_high = evaluate_bem_geometry(
        geometry,
        polar_folder,
        label="Pitch search",
        wind_speed_mps=wind_speed_mps,
        rotor_rpm=rotor_rpm,
        pitch_deg=high,
        config=cfg,
    )
    if summary_high["power_MW"] > target_power_mw:
        raise ValueError(f"Pitch range does not bracket target power at U={wind_speed_mps:.2f} m/s")

    summary_mid = summary_high
    pitch_mid = high
    for _ in range(cfg.pitch_max_iterations):
        pitch_mid = 0.5 * (low + high)
        _, summary_mid = evaluate_bem_geometry(
            geometry,
            polar_folder,
            label="Pitch search",
            wind_speed_mps=wind_speed_mps,
            rotor_rpm=rotor_rpm,
            pitch_deg=pitch_mid,
            config=cfg,
        )
        power_mid = summary_mid["power_MW"]
        if abs(power_mid - target_power_mw) <= cfg.pitch_power_tolerance_mw:
            return pitch_mid, summary_mid
        if power_mid > target_power_mw:
            low = pitch_mid
        else:
            high = pitch_mid
    return pitch_mid, summary_mid


def run_controlled_envelope(
    geometry: pd.DataFrame,
    polar_folder,
    wind_speeds,
    target_power_mw: float,
    config: TurbineConfig | None = None,
    label: str = "Design",
) -> pd.DataFrame:
    """Run the final steady variable-speed / pitch-controlled aerodynamic envelope."""
    cfg = config or TurbineConfig()
    rows = []
    for u in np.asarray(wind_speeds, dtype=float):
        rpm = rotor_rpm_schedule(float(u), cfg)
        if u <= cfg.rated_wind_mps:
            pitch = 0.0
            _, summary = evaluate_bem_geometry(
                geometry,
                polar_folder,
                label=label,
                wind_speed_mps=float(u),
                rotor_rpm=rpm,
                pitch_deg=pitch,
                config=cfg,
            )
        else:
            pitch, summary = solve_pitch_for_target_power(
                geometry,
                polar_folder,
                wind_speed_mps=float(u),
                rotor_rpm=rpm,
                target_power_mw=target_power_mw,
                config=cfg,
            )
        rows.append(
            {
                "wind_mps": float(u),
                "rpm": rpm,
                "pitch_deg": pitch,
                "Cp": summary["Cp"],
                "Ct": summary["Ct"],
                "power_MW": summary["power_MW"],
                "thrust_MN": summary["thrust_MN"],
                "root_moment_MNm": summary["root_moment_MNm"],
            }
        )
    return pd.DataFrame(rows)
