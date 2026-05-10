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
| Selected Model | Hyunmoo-2B-class SRBM |
| Propulsion Type | Two-stage solid + ramjet |
| Vehicle Length | 12.000 m |
| Vehicle Diameter | 0.900 m |
| Launch Mass | 5400.0 kg |
| Dry Mass | 2268.0 kg |
| Propellant Mass | 3132.0 kg |
| Solid Fuel Ratio | 0.70 |
| Gas Generator Ratio | 0.30 |
| Reference Area | 0.6362 m² |
| Solid Thrust | 119445.0 N |
| Ramjet Reference Thrust | 36789.1 N |
| Final Time | 120.000 s |

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
| Hydrogen | 96.690 | 449.976 | 8.017 | 3143.061 |
| Methane | 93.637 | 416.962 | 7.710 | 3135.267 |
| Ethylene | 93.220 | 412.489 | 7.731 | 3136.060 |
| Kerosene | 92.740 | 407.149 | 7.809 | 3137.042 |

---

## Detailed Trajectory Summary

| Fuel Type | Initial Velocity [m/s] | Max Velocity [m/s] | Terminal Velocity [m/s] | Min Gamma [deg] | Max Gamma [deg] | Min Alpha [deg] | Max Alpha [deg] | Min Throttle | Max Throttle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hydrogen | 552.986 | 1143.694 | 449.976 | -10.000 | 30.000 | -2.000 | 2.000 | 0.240 | 1.000 |
| Methane | 552.986 | 1137.975 | 416.962 | -10.000 | 30.000 | -2.000 | 2.000 | 0.240 | 1.000 |
| Ethylene | 552.986 | 1138.140 | 412.489 | -10.000 | 30.000 | -2.000 | 2.000 | 0.240 | 1.000 |
| Kerosene | 552.986 | 1139.073 | 407.149 | -10.000 | 30.000 | -2.000 | 2.000 | 0.240 | 1.000 |

---

## Performance Ranking

### Final Range

| Rank | Fuel Type | Final Range [km] |
|---:|---|---:|
| 1 | Hydrogen | 96.690 |
| 2 | Methane | 93.637 |
| 3 | Ethylene | 93.220 |
| 4 | Kerosene | 92.740 |

### Terminal Velocity

| Rank | Fuel Type | Terminal Velocity [m/s] |
|---:|---|---:|
| 1 | Hydrogen | 449.976 |
| 2 | Methane | 416.962 |
| 3 | Ethylene | 412.489 |
| 4 | Kerosene | 407.149 |

---

## Interpretation

The hydrogen case produced the highest final range and terminal velocity among the tested fuel types.

Compared with kerosene, hydrogen showed:

- Higher final range
- Higher terminal velocity
- Higher maximum altitude
- Higher ramjet specific impulse

This result is mainly related to the higher lower heating value and ramjet specific impulse of hydrogen.

However, the current result should be interpreted as a trajectory optimization result under the same vehicle configuration and gas-generator ratio. Additional analysis is required to evaluate practical design factors such as fuel storage, system mass, volume constraints, and implementation complexity.

---

## Solver Information

The optimization was solved using `mpopt` and `CasADi`.

During the optimization process, CasADi generated warnings related to `NaN` detection in the NLP Jacobian calculation. However, the solver returned feasible optimized results for all tested fuel types.

Typical solver time was approximately:

| Fuel Type | Total Solve Time [ms] |
|---|---:|
| Hydrogen | 1489.373 |
| Methane | 1367.533 |
| Ethylene | 1370.463 |
| Kerosene | 1353.384 |

---

## Conclusion

The fuel comparison result indicates that hydrogen provides the best performance in this simulation condition.

Final range ranking:

```text
Hydrogen > Methane > Ethylene > Kerosene
