## Fuel Comparison Simulation Result

This section summarizes the trajectory optimization results obtained using `mpopt` for different ramjet fuel types.

The simulation compares four fuel candidates:

- Hydrogen
- Methane
- Ethylene
- Kerosene

All cases use the same reference vehicle model and the same gas-generator ratio.

---

## Simulation Model

| Parameter | Value |
|---|---:|
| Selected Model | ATACMS-class SRBM |
| Propulsion Type | Single-stage solid + ramjet-assisted model |
| Vehicle Length | 3.980 m |
| Vehicle Diameter | 0.610 m |
| Launch Mass | 1673.0 kg |
| Dry Mass | 635.7 kg |
| Propellant Mass | 1037.3 kg |
| Solid Fuel Ratio | 0.70 |
| Gas Generator Ratio | 0.30 |
| Reference Area | 0.2922 m² |
| Solid Thrust | 62303.8 N |
| Ramjet Reference Thrust | 19189.6 N |
| Final Time | 100.000 s |

---

## Fuel Property Comparison

| Fuel Type | LHV [MJ/kg] | Ramjet Isp [s] |
|---|---:|---:|
| Hydrogen | 120.00 | 4229.5 |
| Methane | 50.00 | 2730.1 |
| Ethylene | 47.00 | 2646.9 |
| Kerosene | 43.00 | 2531.8 |

---

## Result Summary

| Fuel Type | Final Range [km] | Terminal Velocity [m/s] | Max Altitude [km] | Final Mass [kg] |
|---|---:|---:|---:|---:|
| Hydrogen | 70.392 | 303.242 | 5.440 | 910.357 |
| Methane | 71.401 | 294.864 | 6.337 | 907.468 |
| Ethylene | 65.378 | 271.648 | 4.791 | 910.967 |
| Kerosene | 64.509 | 267.397 | 4.678 | 911.609 |

---

## Detailed Trajectory Summary

| Fuel Type | Initial Velocity [m/s] | Max Velocity [m/s] | Terminal Velocity [m/s] | Min Gamma [deg] | Max Gamma [deg] | Min Alpha [deg] | Max Alpha [deg] | Min Throttle | Max Throttle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hydrogen | 579.301 | 1070.495 | 303.242 | -10.000 | 30.000 | -2.000 | 2.000 | 0.439 | 1.000 |
| Methane | 579.301 | 1163.624 | 294.864 | -10.000 | 30.000 | -2.000 | 2.000 | 0.453 | 1.000 |
| Ethylene | 579.301 | 1063.021 | 271.648 | -10.000 | 30.000 | -2.000 | 2.000 | 0.439 | 1.000 |
| Kerosene | 579.301 | 1060.130 | 267.397 | -10.000 | 30.000 | -2.000 | 2.000 | 0.446 | 1.000 |

---

## Performance Ranking

### Final Range

| Rank | Fuel Type | Final Range [km] |
|---:|---|---:|
| 1 | Methane | 71.401 |
| 2 | Hydrogen | 70.392 |
| 3 | Ethylene | 65.378 |
| 4 | Kerosene | 64.509 |

### Terminal Velocity

| Rank | Fuel Type | Terminal Velocity [m/s] |
|---:|---|---:|
| 1 | Hydrogen | 303.242 |
| 2 | Methane | 294.864 |
| 3 | Ethylene | 271.648 |
| 4 | Kerosene | 267.397 |

### Maximum Altitude

| Rank | Fuel Type | Max Altitude [km] |
|---:|---|---:|
| 1 | Methane | 6.337 |
| 2 | Hydrogen | 5.440 |
| 3 | Ethylene | 4.791 |
| 4 | Kerosene | 4.678 |

---

## Interpretation

In this simulation case, methane produced the highest final range and maximum altitude.

Hydrogen produced the highest terminal velocity and had the highest ramjet specific impulse due to its high lower heating value.

Compared with kerosene:

- Methane showed a higher final range.
- Methane showed a higher maximum altitude.
- Hydrogen showed a higher terminal velocity.
- Hydrogen showed the highest ramjet specific impulse.

Unlike the previous cases, hydrogen did not produce the longest final range in this ATACMS-class model. This indicates that the best-performing fuel can vary depending on the vehicle model, mass properties, aerodynamic conditions, and optimized trajectory.

Therefore, the result should be interpreted as a numerical trajectory optimization result under the given simulation assumptions, not as a universal fuel performance conclusion.

---

## Solver Information

The optimization was solved using `mpopt` and `CasADi`.

During the optimization process, CasADi generated warnings related to `NaN` detection in the NLP Jacobian calculation. However, the solver returned optimized results for all tested fuel types.

| Fuel Type | Total Solve Time [ms] | OCP Transcription Time [ms] | NLP Solution Time [ms] |
|---|---:|---:|---:|
| Hydrogen | 3717.588 | 360.615 | 3356.973 |
| Methane | 3429.385 | 171.734 | 3257.651 |
| Ethylene | 2176.608 | 165.041 | 2011.567 |
| Kerosene | 3122.132 | 148.936 | 2973.195 |

---

## Conclusion

The fuel comparison result shows that methane achieved the longest final range in this simulation condition, while hydrogen achieved the highest terminal velocity.

Final range ranking:

```text
Methane > Hydrogen > Ethylene > Kerosene
