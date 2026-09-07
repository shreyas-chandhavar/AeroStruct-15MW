import numpy as np
from aerostruct15mw.numerics import forward_cumulative_trapezoid, reverse_cumulative_trapezoid

def test_forward_linear_function():
    x = np.linspace(0.0, 1.0, 11); y = x; result = forward_cumulative_trapezoid(y, x); assert np.isclose(result[-1], 0.5, atol=1e-12)

def test_reverse_constant_function():
    x = np.linspace(0.0, 2.0, 5); y = np.ones_like(x); result = reverse_cumulative_trapezoid(y, x); assert np.isclose(result[0], 2.0); assert np.isclose(result[-1], 0.0)
