from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def _save(fig, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    return path


def plot_power_curve(df, path=None):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["wind_mps"], df["baseline_power_MW"], marker="o", label="IEA baseline")
    ax.plot(df["wind_mps"], df["optimized_power_MW"], marker="o", label="Physics-verified optimized design")
    ax.set_xlabel("Wind speed [m/s]")
    ax.set_ylabel("Aerodynamic power [MW]")
    ax.set_title("Baseline vs Physics-Verified Optimized Power Curve")
    ax.grid(True)
    ax.legend()
    if path:
        _save(fig, path)
    return fig, ax


def plot_root_moment_envelope(df, rated_wind_mps=10.59, path=None):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["wind_mps"], df["baseline_root_MNm"], marker="o", label="IEA baseline")
    ax.plot(df["wind_mps"], df["optimized_root_MNm"], marker="o", label="Physics-verified optimized design")
    ax.axvline(rated_wind_mps, linestyle="--", label="Rated wind speed")
    ax.set_xlabel("Wind speed [m/s]")
    ax.set_ylabel("Flapwise root bending moment [MN·m]")
    ax.set_title("Baseline vs Optimized Flapwise Root-Moment Envelope")
    ax.grid(True)
    ax.legend()
    if path:
        _save(fig, path)
    return fig, ax


def plot_tip_deflection_envelope(df, rated_wind_mps=10.59, path=None):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["wind_mps"], df["baseline_tip_m"], marker="o", label="IEA baseline")
    ax.plot(df["wind_mps"], df["optimized_tip_m"], marker="o", label="Physics-verified optimized design")
    ax.axvline(rated_wind_mps, linestyle="--", label="Rated wind speed")
    ax.axhline(0.0, linestyle="--")
    ax.set_xlabel("Wind speed [m/s]")
    ax.set_ylabel("Rotating flapwise tip displacement [m]")
    ax.set_title("Baseline vs Optimized Rotating Tip-Deflection Envelope")
    ax.grid(True)
    ax.legend()
    if path:
        _save(fig, path)
    return fig, ax
