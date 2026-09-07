from __future__ import annotations

import numpy as np


def reverse_cumulative_trapezoid(y, x):
    """Integrate from each station to the tip using trapezoidal segments."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    if y.shape != x.shape:
        raise ValueError("x and y must have the same shape")
    result = np.zeros_like(y)
    for i in range(len(x) - 2, -1, -1):
        dx = x[i + 1] - x[i]
        result[i] = result[i + 1] + 0.5 * (y[i] + y[i + 1]) * dx
    return result


def forward_cumulative_trapezoid(y, x):
    """Integrate from the root to each station using trapezoidal segments."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    if y.shape != x.shape:
        raise ValueError("x and y must have the same shape")
    result = np.zeros_like(y)
    for i in range(1, len(x)):
        dx = x[i] - x[i - 1]
        result[i] = result[i - 1] + 0.5 * (y[i - 1] + y[i]) * dx
    return result
