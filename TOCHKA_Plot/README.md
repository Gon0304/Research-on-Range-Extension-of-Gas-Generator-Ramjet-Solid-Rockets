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
| Selected Model | OTR-21 Tochka-class SRBM |
| Propulsion Type | Single-stage solid + ramjet-assisted model |
| Vehicle Length | 6.400 m |
| Vehicle Diameter | 0.655 m |
| Launch Mass | 2000.0 kg |
| Dry Mass | 840.0 kg |
| Propellant Mass | 1160.0 kg |
| Solid Fuel Ratio | 0.70 |
| Gas Generator Ratio | 0.30 |
| Reference Area | 0.3370 m² |
| Solid Thrust | 74852.2 N |
| Ramjet Reference Thrust | 23054.5 N |
| Final Time | 80.000 s |

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
| Hydrogen | 39.539 | 246.942 | 2.211 | 1158.210 |
| Methane | 46.113 | 268.979 | 2.058 | 1157.503 |
| Ethylene | 52.409 | 307.385 | 4.416 | 1153.199 |
| Kerosene | 51.971 | 303.947 | 4.357 | 1153.596 |

---

## Detailed Trajectory Summary

| Fuel Type | Initial Velocity [m/s] | Max Velocity [m/s] | Terminal Velocity [m/s] | Min Gamma [deg] | Max Gamma [deg] | Min Alpha [deg] | Max Alpha [deg] | Min Throttle | Max Throttle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hydrogen | 519.807 | 848.318 | 246.942 | -10.000 | 30.000 | -1.999 | 2.000 | 0.000 | 1.000 |
| Methane | 519.807 | 947.454 | 268.979 | -10.000 | 30.000 | -2.000 | 2.000 | 0.467 | 1.000 |
| Ethylene | 519.807 | 1041.681 | 307.385 | -10.000 | 30.000 | -2.000 | 2.000 | 0.466 | 1.000 |
| Kerosene | 519.807 | 1040.747 | 303.947 | -10.000 | 30.000 | -2.000 | 2.000 | 0.465 | 1.000 |

---

## Performance Ranking

### Final Range

| Rank | Fuel Type | Final Range [km] |
|---:|---|---:|
| 1 | Ethylene | 52.409 |
| 2 | Kerosene | 51.971 |
| 3 | Methane | 46.113 |
| 4 | Hydrogen | 39.539 |

### Terminal Velocity

| Rank | Fuel Type | Terminal Velocity [m/s] |
|---:|---|---:|
| 1 | Ethylene | 307.385 |
| 2 | Kerosene | 303.947 |
| 3 | Methane | 268.979 |
| 4 | Hydrogen | 246.942 |

### Maximum Altitude

| Rank | Fuel Type | Max Altitude [km] |
|---:|---|---:|
| 1 | Ethylene | 4.416 |
| 2 | Kerosene | 4.357 |
| 3 | Hydrogen | 2.211 |
| 4 | Methane | 2.058 |

---

## Interpretation

In this simulation case, ethylene produced the highest final range, terminal velocity, and maximum altitude among the tested fuel types.

Kerosene showed very similar performance to ethylene, especially in final range and terminal velocity. The difference between ethylene and kerosene was relatively small compared with the difference between the other fuel cases.

Unlike the previous models, hydrogen showed the lowest final range and terminal velocity in this OTR-21 Tochka-class simulation case, even though it has the highest lower heating value and ramjet specific impulse.

This indicates that the best-performing fuel can vary depending on the vehicle model, mass properties, aerodynamic conditions, trajectory constraints, and optimization result.

Therefore, this result should be interpreted as a numerical trajectory optimization result under the given simulation assumptions, not as a universal fuel performance conclusion.

---

## Solver Information

The optimization was solved using `mpopt` and `CasADi`.

During the optimization process, CasADi generated warnings related to `NaN` detection in the NLP Jacobian calculation. However, the solver returned optimized results for all tested fuel types.

| Fuel Type | Total Solve Time [ms] | OCP Transcription Time [ms] | NLP Solution Time [ms] |
|---|---:|---:|---:|
| Hydrogen | 4683.415 | 359.026 | 4324.389 |
| Methane | 3928.601 | 164.421 | 3764.180 |
| Ethylene | 3872.458 | 165.118 | 3707.339 |
| Kerosene | 3398.126 | 164.333 | 3233.793 |

---

## Conclusion

The fuel comparison result shows that ethylene achieved the best overall numerical performance in this simulation condition.

Final range ranking:

```text
Ethylene > Kerosene > Methane > Hydrogen
```

Terminal velocity ranking:

```text
Ethylene > Kerosene > Methane > Hydrogen
```

Maximum altitude ranking:

```text
Ethylene > Kerosene > Hydrogen > Methane
```

Therefore, ethylene showed the most favorable result in terms of final range, terminal velocity, and maximum altitude under the given simulation assumptions.
