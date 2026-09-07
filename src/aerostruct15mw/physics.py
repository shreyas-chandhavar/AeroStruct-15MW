from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .bem import evaluate_bem_geometry
from .config import ANNUAL_1P_CYCLES, FATIGUE_REFERENCE_CYCLES, TurbineConfig
from .design import build_aerostruct_candidate
from .structures import centrifugal_tension_from_rpm, solve_beam_modes, solve_rotating_beam_fem


@dataclass
class PhysicsEvaluator:
    """Unified reduced-order evaluator used to create surrogate training data."""

    geometry: object
    span_m: np.ndarray
    flap_ei: np.ndarray
    edge_ei: np.ndarray
    mass_density: np.ndarray
    polar_folder: str | Path
    config: TurbineConfig = TurbineConfig()
    annual_1p_cycles: float = ANNUAL_1P_CYCLES
    fatigue_reference_cycles: float = FATIGUE_REFERENCE_CYCLES

    def evaluate(self, peak_twist_deg, aero_start_m, struct_start_m, ei_increase_percent):
        c = build_aerostruct_candidate(self.geometry, self.span_m, self.flap_ei, self.mass_density, peak_twist_deg, aero_start_m, struct_start_m, ei_increase_percent)
        bem_rated, rated = evaluate_bem_geometry(c.geometry, self.polar_folder, label="ML candidate", wind_speed_mps=self.config.rated_wind_mps, rotor_rpm=self.config.rpm_rated, pitch_deg=0.0, config=self.config)
        ncf = centrifugal_tension_from_rpm(self.span_m, c.mass_density, self.config.rpm_rated, self.config.rotor_radius_m)
        struct_rated = solve_rotating_beam_fem(self.span_m, bem_rated["normal_Npm"].to_numpy(), c.ei, axial_tension_n=ncf)
        u_gust = 1.20 * self.config.rated_wind_mps
        bem_gust, gust = evaluate_bem_geometry(c.geometry, self.polar_folder, label="20% frozen-control gust", wind_speed_mps=u_gust, rotor_rpm=self.config.rpm_rated, pitch_deg=0.0, config=self.config)
        struct_gust = solve_rotating_beam_fem(self.span_m, bem_gust["normal_Npm"].to_numpy(), c.ei, axial_tension_n=ncf)
        gravity_amp_mnm = np.trapezoid(c.mass_density * self.config.gravity_mps2 * self.span_m, self.span_m) / 1e6
        m_fatigue = 10
        damage_sum = self.annual_1p_cycles * gravity_amp_mnm**m_fatigue
        del10 = (damage_sum / self.fatigue_reference_cycles) ** (1.0 / m_fatigue)
        f_flap, _ = solve_beam_modes(self.span_m, c.ei, c.mass_density, ncf, n_modes=1)
        f_edge, _ = solve_beam_modes(self.span_m, self.edge_ei, c.mass_density, ncf, n_modes=1)
        rated_3p = 3.0 * self.config.rpm_rated / 60.0
        return {"peak_twist_deg": peak_twist_deg, "aero_start_m": aero_start_m, "struct_start_m": struct_start_m, "EI_increase_percent": ei_increase_percent, "added_mass_kg": c.added_mass_kg, "rated_Cp": rated["Cp"], "rated_power_MW": rated["power_MW"], "rated_thrust_MN": rated["thrust_MN"], "rated_root_moment_MNm": rated["root_moment_MNm"], "rated_tip_deflection_m": struct_rated["tip_deflection_m"], "rated_tip_rotation_deg": struct_rated["tip_rotation_deg"], "gust_root_moment_MNm": gust["root_moment_MNm"], "gust_tip_deflection_m": struct_gust["tip_deflection_m"], "gravity_1P_amplitude_MNm": gravity_amp_mnm, "DEL10_proxy_MNm": del10, "flap1_Hz": f_flap[0], "edge1_Hz": f_edge[0], "flap_3P_margin_Hz": f_flap[0] - rated_3p, "edge_3P_margin_Hz": f_edge[0] - rated_3p}
