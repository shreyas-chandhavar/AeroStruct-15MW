import numpy as np
import pandas as pd
from aerostruct15mw.design import build_aerostruct_candidate, smooth_twist_shape

def test_smooth_twist_profile():
    span = np.linspace(0, 120, 121); shape, end = smooth_twist_shape(span, 75.0); assert end == 115.0; assert np.isclose(shape[75], 0.0); assert np.isclose(shape[85], 1.0); assert np.isclose(shape[105], 1.0); assert np.isclose(shape[115], 0.0)

def test_zero_ei_change_adds_no_mass():
    span = np.linspace(0, 117, 50); geometry = pd.DataFrame({"span_m": span, "twist_deg": np.zeros(50), "chord_m": np.ones(50)}); ei = np.ones(50) * 1e9; mass = np.ones(50) * 100.0; c = build_aerostruct_candidate(geometry, span, ei, mass, 1.0, 75.0, 80.0, 0.0); assert np.isclose(c.added_mass_kg, 0.0); assert c.geometry["twist_deg"].max() > 0.9
