from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class CandidateDesign:
    geometry: pd.DataFrame
    ei: np.ndarray
    mass_density: np.ndarray
    added_mass_kg: float
    smooth_shape: np.ndarray
    aero_end_m: float
    struct_end_m: float


def smooth_twist_shape(span_m, aero_start_m: float):
    """10 m half-cosine ramp + 20 m plateau + 10 m half-cosine ramp."""
    span = np.asarray(span_m, dtype=float)
    ramp_up_start = aero_start_m
    ramp_up_end = aero_start_m + 10.0
    plateau_end = aero_start_m + 30.0
    ramp_down_end = aero_start_m + 40.0
    shape = np.zeros_like(span)

    mask_up = (span >= ramp_up_start) & (span < ramp_up_end)
    xi_up = (span[mask_up] - ramp_up_start) / 10.0
    shape[mask_up] = 0.5 * (1.0 - np.cos(np.pi * xi_up))

    mask_plateau = (span >= ramp_up_end) & (span <= plateau_end)
    shape[mask_plateau] = 1.0

    mask_down = (span > plateau_end) & (span <= ramp_down_end)
    xi_down = (span[mask_down] - plateau_end) / 10.0
    shape[mask_down] = 0.5 * (1.0 + np.cos(np.pi * xi_down))
    return shape, ramp_down_end


def build_aerostruct_candidate(
    geometry: pd.DataFrame,
    span_m,
    baseline_flap_ei,
    baseline_mass_density,
    peak_twist_deg: float,
    aero_start_m: float,
    struct_start_m: float,
    ei_increase_percent: float,
) -> CandidateDesign:
    """Build the same four-variable candidate used in the ML design study."""
    geometry_candidate = geometry.copy()
    span = geometry_candidate["span_m"].to_numpy()
    shape, aero_end = smooth_twist_shape(span, aero_start_m)
    geometry_candidate["twist_deg"] = geometry_candidate["twist_deg"] + peak_twist_deg * shape

    span_m = np.asarray(span_m, dtype=float)
    ei = np.asarray(baseline_flap_ei, dtype=float).copy()
    mass = np.asarray(baseline_mass_density, dtype=float).copy()
    struct_end = struct_start_m + 30.0
    mask = (span_m >= struct_start_m) & (span_m <= struct_end)
    frac = ei_increase_percent / 100.0
    ei[mask] *= 1.0 + frac

    # Development-study mass proxy: local relative mass increase ~= relative EI increase.
    mass[mask] *= 1.0 + frac
    added_mass = np.trapezoid(mass - np.asarray(baseline_mass_density, dtype=float), span_m)

    return CandidateDesign(
        geometry=geometry_candidate,
        ei=ei,
        mass_density=mass,
        added_mass_kg=float(added_mass),
        smooth_shape=shape,
        aero_end_m=float(aero_end),
        struct_end_m=float(struct_end),
    )
