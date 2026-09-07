from __future__ import annotations

import numpy as np
from scipy.linalg import eigh

from .numerics import forward_cumulative_trapezoid, reverse_cumulative_trapezoid


def structural_response_from_bem(bem_results, ei_profile):
    span = bem_results["span_m"].to_numpy()
    normal = bem_results["normal_Npm"].to_numpy()
    ei_profile = np.asarray(ei_profile, dtype=float)
    if len(ei_profile) != len(span):
        raise ValueError("EI profile and BEM span must contain the same number of stations")
    shear_n = reverse_cumulative_trapezoid(normal, span)
    moment_nm = reverse_cumulative_trapezoid(shear_n, span)
    curvature = moment_nm / ei_profile
    theta = forward_cumulative_trapezoid(curvature, span)
    x_m = forward_cumulative_trapezoid(np.cos(theta), span)
    y_m = forward_cumulative_trapezoid(np.sin(theta), span)
    return {"shear_N": shear_n, "moment_Nm": moment_nm, "curvature_1pm": curvature, "theta_rad": theta, "x_m": x_m, "y_m": y_m, "tip_deflection_m": y_m[-1], "tip_rotation_deg": np.degrees(theta[-1])}


def centrifugal_tension_from_rpm(span_m, mass_density_kgpm, rpm, rotor_radius_m=120.0):
    span_m = np.asarray(span_m, dtype=float)
    mass_density_kgpm = np.asarray(mass_density_kgpm, dtype=float)
    hub_radius_m = rotor_radius_m - span_m.max()
    radius_m = hub_radius_m + span_m
    omega = rpm * 2.0 * np.pi / 60.0
    centrifugal_load_npm = mass_density_kgpm * omega**2 * radius_m
    return reverse_cumulative_trapezoid(centrifugal_load_npm, span_m)


def solve_rotating_beam_fem(span_m, normal_load_npm, ei_nm2, axial_tension_n=None):
    span_m = np.asarray(span_m, dtype=float)
    normal_load_npm = np.asarray(normal_load_npm, dtype=float)
    ei_nm2 = np.asarray(ei_nm2, dtype=float)
    n_nodes = len(span_m)
    n_dof = 2 * n_nodes
    axial_tension_n = np.zeros(n_nodes) if axial_tension_n is None else np.asarray(axial_tension_n, dtype=float)
    k_global = np.zeros((n_dof, n_dof))
    f_global = np.zeros(n_dof)
    for e in range(n_nodes - 1):
        le = span_m[e + 1] - span_m[e]
        ei = 0.5 * (ei_nm2[e] + ei_nm2[e + 1])
        q = 0.5 * (normal_load_npm[e] + normal_load_npm[e + 1])
        n = 0.5 * (axial_tension_n[e] + axial_tension_n[e + 1])
        k_elastic = (ei / le**3) * np.array([[12, 6 * le, -12, 6 * le],[6 * le, 4 * le**2, -6 * le, 2 * le**2],[-12, -6 * le, 12, -6 * le],[6 * le, 2 * le**2, -6 * le, 4 * le**2]])
        k_geo = (n / (30 * le)) * np.array([[36, 3 * le, -36, 3 * le],[3 * le, 4 * le**2, -3 * le, -le**2],[-36, -3 * le, 36, -3 * le],[3 * le, -le**2, -3 * le, 4 * le**2]])
        f_element = (q * le / 12.0) * np.array([6, le, 6, -le])
        dofs = np.array([2 * e, 2 * e + 1, 2 * (e + 1), 2 * (e + 1) + 1])
        f_global[dofs] += f_element
        k_global[np.ix_(dofs, dofs)] += k_elastic + k_geo
    free = np.arange(2, n_dof)
    disp = np.zeros(n_dof)
    disp[free] = np.linalg.solve(k_global[np.ix_(free, free)], f_global[free])
    y_m = disp[0::2]
    theta_rad = disp[1::2]
    return {"y_m": y_m, "theta_rad": theta_rad, "tip_deflection_m": y_m[-1], "tip_rotation_deg": np.degrees(theta_rad[-1])}


def assemble_rotating_beam_matrices(span_m, ei_nm2, mass_density_kgpm, axial_tension_n=None):
    span_m = np.asarray(span_m, dtype=float)
    ei_nm2 = np.asarray(ei_nm2, dtype=float)
    mass_density_kgpm = np.asarray(mass_density_kgpm, dtype=float)
    n_nodes = len(span_m)
    n_dof = 2 * n_nodes
    axial_tension_n = np.zeros(n_nodes) if axial_tension_n is None else np.asarray(axial_tension_n, dtype=float)
    k_global = np.zeros((n_dof, n_dof))
    m_global = np.zeros((n_dof, n_dof))
    for e in range(n_nodes - 1):
        le = span_m[e + 1] - span_m[e]
        ei = 0.5 * (ei_nm2[e] + ei_nm2[e + 1])
        m = 0.5 * (mass_density_kgpm[e] + mass_density_kgpm[e + 1])
        n = 0.5 * (axial_tension_n[e] + axial_tension_n[e + 1])
        k_elastic = (ei / le**3) * np.array([[12, 6 * le, -12, 6 * le],[6 * le, 4 * le**2, -6 * le, 2 * le**2],[-12, -6 * le, 12, -6 * le],[6 * le, 2 * le**2, -6 * le, 4 * le**2]])
        k_geo = (n / (30 * le)) * np.array([[36, 3 * le, -36, 3 * le],[3 * le, 4 * le**2, -3 * le, -le**2],[-36, -3 * le, 36, -3 * le],[3 * le, -le**2, -3 * le, 4 * le**2]])
        m_element = (m * le / 420.0) * np.array([[156, 22 * le, 54, -13 * le],[22 * le, 4 * le**2, 13 * le, -3 * le**2],[54, 13 * le, 156, -22 * le],[-13 * le, -3 * le**2, -22 * le, 4 * le**2]])
        dofs = np.array([2 * e, 2 * e + 1, 2 * (e + 1), 2 * (e + 1) + 1])
        k_global[np.ix_(dofs, dofs)] += k_elastic + k_geo
        m_global[np.ix_(dofs, dofs)] += m_element
    free = np.arange(2, n_dof)
    return k_global[np.ix_(free, free)], m_global[np.ix_(free, free)]


def solve_beam_modes(span_m, ei_nm2, mass_density_kgpm, axial_tension_n=None, n_modes=5):
    k, m = assemble_rotating_beam_matrices(span_m, ei_nm2, mass_density_kgpm, axial_tension_n)
    eigenvalues, eigenvectors = eigh(k, m)
    valid = eigenvalues > 1e-10
    eigenvalues = eigenvalues[valid]
    eigenvectors = eigenvectors[:, valid]
    freq_hz = np.sqrt(eigenvalues) / (2.0 * np.pi)
    return freq_hz[:n_modes], eigenvectors[:, :n_modes]


def run_rotating_structural_envelope(bem_envelope_results, span_m, ei_profile, mass_density_kgpm, rpm_values, rotor_radius_m=120.0):
    rows = []
    for bem_results, rpm in zip(bem_envelope_results, rpm_values):
        ncf = centrifugal_tension_from_rpm(span_m, mass_density_kgpm, rpm, rotor_radius_m)
        rows.append(solve_rotating_beam_fem(span_m, bem_results["normal_Npm"].to_numpy(), ei_profile, axial_tension_n=ncf))
    return rows
