# Results summary

## Final candidate

| Variable | Value |
|---|---:|
| peak smooth twist | 1.499301° |
| aerodynamic start | 76.911309 m |
| structural start | 81.856218 m |
| local EI increase | 0.060948% |
| added mass | 2.010238 kg/blade |

The near-zero EI/mass result means that the balanced optimum is predominantly an aerodynamic load-alleviation solution within the modeled design space.

## Rated-point comparison

| Metric | Baseline | Optimized | Change |
|---|---:|---:|---:|
| \(C_P\) | 0.492409 | 0.487522 | −0.992% |
| flapwise root moment | 63.108 MN·m | 59.543 MN·m | −5.650% |
| rotating tip deflection | 15.570 m | 14.444 m | −7.230% |

## Gust comparison

A simplified +20% frozen-control gust at 12.708 m/s, 7.56 rpm and 0° pitch gives approximately 75.169 MN·m baseline root moment and 71.419 MN·m optimized, a reduction of about 4.99%.

## Fatigue-proxy comparison

The final DEL10 proxy changes only slightly: 16.388323 MN·m baseline versus 16.389937 MN·m optimized, approximately +0.01%.

## Aerodynamic energy proxy

For the selected Weibull distribution and 4–25 m/s bins, the baseline aerodynamic AEP proxy is 75.863 GWh/year and the optimized value is 75.803 GWh/year, a change of approximately −0.078%.

## Final envelope

The final controlled envelope is stored in `results/tables/operating_envelope_comparison.csv`. Root-moment reduction is positive at every sampled operating point. Maximum sampled deflection magnitude is also lower, but the optimized blade has a larger negative displacement magnitude at 22–25 m/s after high-wind load reversal. This limitation is visible in the final envelope plot and should be retained in any portfolio/report narrative.
