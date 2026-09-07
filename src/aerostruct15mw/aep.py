from __future__ import annotations

from math import gamma

import numpy as np
import pandas as pd


def weibull_cdf(u, k, c):
    u = np.asarray(u, dtype=float)
    return 1.0 - np.exp(-(u / c) ** k)


def weibull_scale_from_mean(mean_wind_mps: float, k: float = 2.0) -> float:
    return mean_wind_mps / gamma(1.0 + 1.0 / k)


def wind_bin_probabilities(wind_speeds, k=2.0, mean_wind_mps=9.0, bin_width=1.0):
    wind_speeds = np.asarray(wind_speeds, dtype=float)
    c = weibull_scale_from_mean(mean_wind_mps, k)
    lo = np.maximum(wind_speeds - bin_width / 2.0, 0.0)
    hi = wind_speeds + bin_width / 2.0
    return weibull_cdf(hi, k, c) - weibull_cdf(lo, k, c)


def aerodynamic_aep_proxy(power_curve: pd.DataFrame, probability, hours_per_year=8760.0):
    probability = np.asarray(probability, dtype=float)
    power = power_curve["power_MW"].to_numpy(dtype=float)
    if len(power) != len(probability):
        raise ValueError("Power curve and probability arrays must have equal length")
    energy_gwh = power * probability * hours_per_year / 1000.0
    return float(energy_gwh.sum()), energy_gwh


def annual_1p_cycle_count(rpm_values, probability, hours_per_year=8760.0):
    rpm_values = np.asarray(rpm_values, dtype=float)
    probability = np.asarray(probability, dtype=float)
    return float(np.sum(probability * hours_per_year * 60.0 * rpm_values))
