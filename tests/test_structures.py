import numpy as np
from aerostruct15mw.structures import centrifugal_tension_from_rpm, solve_beam_modes, solve_rotating_beam_fem

def synthetic_beam():
    span = np.linspace(0.0, 100.0, 21); ei = np.full_like(span, 1e10); mass = np.full_like(span, 500.0); return span, ei, mass

def test_zero_load_zero_deflection():
    span, ei, _ = synthetic_beam(); response = solve_rotating_beam_fem(span, np.zeros_like(span), ei); assert np.allclose(response["y_m"], 0.0)

def test_centrifugal_tension_positive_and_zero_at_tip():
    span, _, mass = synthetic_beam(); ncf = centrifugal_tension_from_rpm(span, mass, rpm=7.56, rotor_radius_m=120.0); assert ncf[0] > 0.0; assert np.isclose(ncf[-1], 0.0)

def test_first_mode_is_positive():
    span, ei, mass = synthetic_beam(); ncf = centrifugal_tension_from_rpm(span, mass, 7.56, 120.0); f, _ = solve_beam_modes(span, ei, mass, ncf, n_modes=2); assert len(f) == 2; assert np.all(f > 0.0)
