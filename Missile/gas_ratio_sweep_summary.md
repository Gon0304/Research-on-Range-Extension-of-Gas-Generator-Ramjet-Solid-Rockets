# 1-Phase Gas Ratio Sweep Summary

Condition:
- Files: `Missile/missile_optimizer_*`
- Fuel: `gas_generator`
- Sweep: coarse `0.00-0.80` by `0.05`, refined near optimum by `0.01`
- Solver segments: `n_segments=18`
- Dynamic pressure replay check uses the tuned 1-phase files.

| Model | Baseline ratio | Baseline range [km] | Best gas ratio | Best range [km] | Increase [km] | Increase [%] | qmax / limit [kPa] |
|---|---:|---:|---:|---:|---:|---:|---:|
| ATACMS | 0.00 | 184.292 | 0.11 | 284.816 | 100.524 | 54.55 | 202.5 / 300 |
| LORA | 0.00 | 179.191 | 0.12 | 289.086 | 109.896 | 61.33 | 206.3 / 300 |
| HYUNMOO_2B | 0.00 | 418.236 | 0.08 | 426.657 | 8.420 | 2.01 | 205.6 / 300 |
| TOCHKA | 0.00 | 90.231 | 0.12 | 202.332 | 112.101 | 124.24 | 157.1 / 240 |

Notes:
- ATACMS/LORA/TOCHKA show a clear optimum near `gas_ratio = 0.11-0.12`.
- HYUNMOO_2B is already strong in the baseline boost condition, so the range gain from ramjet gas allocation is small; its best refined point is `0.08`.
- High gas ratios around `0.65+` are poor because the reduced solid boost can no longer hand off near useful ramjet Mach conditions.
