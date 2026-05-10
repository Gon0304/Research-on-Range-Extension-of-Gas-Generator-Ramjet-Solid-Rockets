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
| Selected Model | LORA-class SRBM |
| Propulsion Type | Solid + ramjet |
| Vehicle Length | 5.200 m |
| Vehicle Diameter | 0.624 m |
| Launch Mass | 1600.0 kg |
| Dry Mass | 640.0 kg |
| Propellant Mass | 960.0 kg |
| Solid Fuel Ratio | 0.70 |
| Gas Generator Ratio | 0.30 |
| Reference Area | 0.3058 m² |
| Solid Thrust | 50455.2 N |
| Ramjet Reference Thrust | 15540.2 N |
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
| Hydrogen | 63.258 | 274.130 | 4.695 | 897.777 |
| Methane | 60.475 | 260.383 | 4.177 | 897.934 |
| Ethylene | 60.125 | 258.836 | 4.112 | 898.069 |
| Kerosene | 59.611 | 256.675 | 4.009 | 898.254 |

---

## Detailed Trajectory Summary

| Fuel Type | Initial Velocity [m/s] | Max Velocity [m/s] | Terminal Velocity [m/s] | Min Gamma [deg] | Max Gamma [deg] | Min Alpha [deg] | Max Alpha [deg] | Min Throttle | Max Throttle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hydrogen | 560.613 | 982.600 | 274.130 | -10.000 | 30.000 | -2.000 | 2.000 | 0.366 | 1.000 |
| Methane | 560.613 | 969.103 | 260.383 | -10.000 | 30.000 | -2.000 | 2.000 | 0.375 | 1.000 |
| Ethylene | 560.613 | 967.985 | 258.836 | -10.000 | 30.000 | -2.000 | 2.000 | 0.314 | 1.000 |
| Kerosene | 560.613 | 965.533 | 256.675 | -10.000 | 30.000 | -2.000 | 2.000 | 0.361 | 1.000 |

---

## Performance Ranking

### Final Range

| Rank | Fuel Type | Final Range [km] |
|---:|---|---:|
| 1 | Hydrogen | 63.258 |
| 2 | Methane | 60.475 |
| 3 | Ethylene | 60.125 |
| 4 | Kerosene | 59.611 |

### Terminal Velocity

| Rank | Fuel Type | Terminal Velocity [m/s] |
|---:|---|---:|
| 1 | Hydrogen | 274.130 |
| 2 | Methane | 260.383 |
| 3 | Ethylene | 258.836 |
| 4 | Kerosene | 256.675 |

### Maximum Altitude

| Rank | Fuel Type | Max Altitude [km] |
|---:|---|---:|
| 1 | Hydrogen | 4.695 |
| 2 | Methane | 4.177 |
| 3 | Ethylene | 4.112 |
| 4 | Kerosene | 4.009 |

---

## Interpretation

The hydrogen case produced the highest final range, terminal velocity, and maximum altitude among the tested fuel types.

Compared with kerosene, hydrogen showed:

- Higher final range
- Higher terminal velocity
- Higher maximum altitude
- Higher ramjet specific impulse

This result is mainly related to the higher lower heating value and ramjet specific impulse of hydrogen.

However, this result should be interpreted only as a numerical trajectory optimization result under the same vehicle configuration and gas-generator ratio. Additional analysis would be required to evaluate practical constraints such as storage condition, system mass, volume limitation, and implementation complexity.

---

## Solver Information

The optimization was solved using `mpopt` and `CasADi`.

During the optimization process, CasADi generated warnings related to `NaN` detection in the NLP Jacobian calculation. However, the solver returned optimized results for all tested fuel types.

| Fuel Type | Total Solve Time [ms] | OCP Transcription Time [ms] | NLP Solution Time [ms] |
|---|---:|---:|---:|
| Hydrogen | 1626.999 | 364.621 | 1262.378 |
| Methane | 1469.099 | 163.290 | 1305.809 |
| Ethylene | 2391.716 | 167.134 | 2224.582 |
| Kerosene | 1566.888 | 165.188 | 1401.699 |

---

## Conclusion

The fuel comparison result indicates that hydrogen showed the best performance in this simulation condition.

Final range ranking:

```text
Hydrogen > Methane > Ethylene > Kerosene
