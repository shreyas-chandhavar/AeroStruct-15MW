from __future__ import annotations

import numpy as np
import pandas as pd
from paretoset import paretoset

from .config import BASELINE_CP_MODEL

CORE_OBJECTIVES = ["rated_root_moment_MNm", "rated_tip_deflection_m", "DEL10_proxy_MNm", "added_mass_kg"]


def apply_engineering_constraints(
    df: pd.DataFrame,
    cp_fraction_min=0.99,
    mass_max_kg=1000.0,
    flap_3p_margin_min_hz=0.145,
    baseline_cp=BASELINE_CP_MODEL,
):
    return df[
        (df["rated_Cp"] >= cp_fraction_min * baseline_cp)
        & (df["added_mass_kg"] <= mass_max_kg)
        & (df["flap_3P_margin_Hz"] >= flap_3p_margin_min_hz)
    ].copy()


def core_pareto_front(df: pd.DataFrame, objectives=CORE_OBJECTIVES):
    mask = paretoset(df[list(objectives)], sense=["min"] * len(objectives))
    return df.loc[mask].copy()


def select_utopia_design(df: pd.DataFrame, objectives=CORE_OBJECTIVES):
    """Equal-weight Euclidean distance from the normalized ideal origin."""
    work = df.copy()
    norm_cols = []
    for col in objectives:
        lo = work[col].min()
        hi = work[col].max()
        norm = f"{col}_norm"
        work[norm] = 0.0 if hi == lo else (work[col] - lo) / (hi - lo)
        norm_cols.append(norm)
    work["utopia_distance"] = np.sqrt((work[norm_cols] ** 2).sum(axis=1))
    return work.loc[work["utopia_distance"].idxmin()], work
