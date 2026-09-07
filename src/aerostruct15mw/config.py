from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TurbineConfig:
    """Reduced-order turbine and operating parameters used in the study."""

    blades: int = 3
    rotor_radius_m: float = 120.0
    air_density_kgpm3: float = 1.225
    rated_wind_mps: float = 10.59
    rpm_min: float = 5.0
    rpm_rated: float = 7.56
    lambda_opt: float = 9.0
    gravity_mps2: float = 9.81
    bem_tolerance: float = 1e-5
    bem_max_iterations: int = 300
    bem_relaxation: float = 0.25
    pitch_low_deg: float = 0.0
    pitch_high_deg: float = 35.0
    pitch_power_tolerance_mw: float = 0.002
    pitch_max_iterations: int = 40


@dataclass(frozen=True)
class DesignBounds:
    """Four-dimensional design space used for the surrogate study."""

    peak_twist_deg: tuple[float, float] = (0.0, 2.0)
    aero_start_m: tuple[float, float] = (70.0, 77.0)
    struct_start_m: tuple[float, float] = (70.0, 85.0)
    ei_increase_percent: tuple[float, float] = (0.0, 30.0)


@dataclass(frozen=True)
class FinalDesign:
    """Physics-verified balanced design selected at the end of the study."""

    peak_twist_deg: float = 1.499301
    aero_start_m: float = 76.911309
    struct_start_m: float = 81.856218
    ei_increase_percent: float = 0.060948


REFERENCE_CP = 0.489
REFERENCE_CT = 0.799
REFERENCE_AERO_POWER_MW = 16.092
BASELINE_CP_MODEL = 0.4924088224
BASELINE_ROOT_MOMENT_MNM = 63.10808228
BASELINE_DEL10_PROXY_MNM = 16.388323
ANNUAL_1P_CYCLES = 2_964_827.0
FATIGUE_REFERENCE_CYCLES = 1.0e7
