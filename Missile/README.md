# Public Baseline Missile Parameters for mpopt Model

본 연구에서는 공개 제원 기반의 전술 탄도미사일을 baseline model로 사용한다.  
목적은 실제 무기체계의 상세 성능을 재현하는 것이 아니라, 공개된 길이, 직경, 질량, 추진 방식, 사거리 정보를 바탕으로 mpopt 기반 trajectory optimization에 사용할 수 있는 개념적 기준 모델을 구성하는 것이다.

현재 코드는 단순 다단 운용이 아니라 **Mach 기반 mode change**를 사용한다.

- `M < 2`: rocket / boost mode
- `M > 2`: ducted ramjet mode
- 각 결과는 발사 직후 전체 궤적이 아니라 **Mach 2 근처 boost handoff 이후 궤적**으로 해석한다.

---

## Baseline Missile Images

### LORA

로라(미사일): 이스라엘 항공 우주산업에서 개발한 전술용 준탄도 미사일

<img width="960" height="345" alt="LORA" src="https://github.com/user-attachments/assets/744dbf00-6fe1-4d2f-8097-60147895db04" />

### ATACMS

ATACMS(미사일): 미국 방산산업체 LTV에서 설계 및 제조한 단거리 초음속 전술 탄도 미사일

<img width="250" height="375" alt="ATACMS" src="https://github.com/user-attachments/assets/d43ea3c6-6298-4d52-90d0-759c677f44e1" />

### Hyunmoo-II

현무-II(미사일): 대한민국 육군 미사일전략사령부에서 운용하는 전역 탄도 미사일

<img width="500" height="423" alt="Hyunmoo-II" src="https://github.com/user-attachments/assets/f405a248-4eb6-4d35-b119-1295e8c5a377" />

### OTR-21 Tochka-U

OTR-21 Tochka-U(미사일): 소련의 전술 탄도 미사일

<img width="1024" height="683" alt="OTR-21 Tochka-U" src="https://github.com/user-attachments/assets/6ea8badd-6ae3-4e71-a296-245c3b0edb26" />

---

## 1. Candidate Baseline Missile Models

| Priority | Model | Reason | mpopt Suitability |
|---:|---|---|---|
| 1 | LORA-class model | ATACMS와 질량, 직경이 비슷한 단거리 탄도미사일 | Very good |
| 2 | ATACMS-class model | 초기 기준 모델, 공개 제원이 비교적 잘 정리됨 | Very good |
| 3 | Hyunmoo-2B-class model | 한국형 SRBM 계열, 질량이 커서 확장 모델에 적합 | Good |
| 4 | OTR-21 Tochka-class model | 오래된 단거리 탄도미사일, 단순 boost-coast 검증에 적합 | Good |

---

## 2. Public Specification Values

아래 값들은 공개 자료를 바탕으로 정리한 baseline missile specification이다.

| Model | Length [m] | Diameter [m] | Launch Mass [kg] | Public Range [km] | Propulsion |
|---|---:|---:|---:|---:|---|
| LORA | 5.20 | 0.624 | 1,600 | 280~430 | Solid propellant |
| ATACMS | 3.98 | 0.610 | 1,673 | 300 | Single-stage solid propellant |
| Hyunmoo-2B | >12.0 | 0.900 | ~5,400 | 500 | Two-stage solid propellant |
| OTR-21 Tochka-U | 6.40 | 0.655 | ~2,000 | 70~120 | Single-stage solid propellant |

---

## 3. Current Optimizer Structure

이전에는 하나의 optimizer 파일에서 여러 미사일을 함께 비교했지만, 현재는 각 모델별로 다른 초기조건과 constraint tuning이 필요하므로 네 개의 전용 Python 파일로 분리하였다.

| File | Model | Purpose |
|---|---|---|
| `missile_optimizer_ATACMS.py` | ATACMS | ATACMS 전용 mode-change trajectory optimizer |
| `missile_optimizer_LORA.py` | LORA | LORA 전용 mode-change trajectory optimizer |
| `missile_optimizer_HYUNMOO_2B.py` | HYUNMOO_2B | HYUNMOO_2B 전용 mode-change trajectory optimizer |
| `missile_optimizer_TOCHKA.py` | TOCHKA | TOCHKA 전용 mode-change trajectory optimizer |

모든 전용 파일은 다음 구조를 공유한다.

| Setting | Current Value | Meaning |
|---|---:|---|
| `GAS_RATIO` | `0.30` | 전체 추진제 중 gas-generator / ramjet fuel 비율 |
| `FUEL_TYPE` | `"hydrogen"` | 현재 validation에 사용한 기본 연료 |
| `OBJECTIVE` | `"range"` | terminal downrange 최대화 |
| `RUN_ALL_FUELS` | `False` | 기본적으로 선택 연료 하나만 실행 |
| `PLOT_RESULT` | `True` | custom plot 저장 |
| `USE_TWO_PHASE` | `False` | phase boundary artifact를 피하기 위해 single-phase 사용 |
| `REPLAY_DYNAMICS_FOR_PLOTS` | `True` | collocation 결과를 ODE로 다시 적분하여 plot 생성 |
| `RAMJET_MIN_MACH` | `2.0` | ramjet mode 진입 기준 |
| `RAMJET_MAX_MACH` | `5.5` | ramjet mode 상한 gate |
| `CL_ALPHA` | `0.0` | 현재 validation에서는 lift steering 비활성화 |

---

## 4. Model-Specific Mode-Change Settings

각 모델은 Mach 2 근처의 boost handoff 상태에서 시작하도록 설정하였다. 따라서 plot 제목도 `After Boost Handoff`로 표시된다.

| Model | Script | Active `MODEL_NAMES` | Handoff Mach | Handoff Altitude | `tf_min` | `tf_max` | `max_q` |
|---|---|---|---:|---:|---:|---:|---:|
| ATACMS | `missile_optimizer_ATACMS.py` | `["ATACMS"]` | `2.10` | `3000 m` | `30 s` | `80 s` | `300 kPa` |
| LORA | `missile_optimizer_LORA.py` | `["LORA"]` | `2.10` | `3000 m` | `30 s` | `80 s` | `300 kPa` |
| HYUNMOO_2B | `missile_optimizer_HYUNMOO_2B.py` | `["HYUNMOO_2B"]` | `2.10` | `5000 m` | `55 s` | `180 s` | `300 kPa` |
| TOCHKA | `missile_optimizer_TOCHKA.py` | `["TOCHKA"]` | `2.05` | `1500 m` | `55 s` | `140 s` | `300 kPa` |

---

## 5. Model Assumption Values Used in mpopt Code

아래 값들은 공개 제원이 아니라, mpopt 기반 개념 모델을 구성하기 위해 설정한 연구용 가정값이다. 실제 미사일 성능을 의미하지 않으며, 모델 비교와 민감도 분석을 위한 surrogate parameter로 사용한다.

| Model | Dry Mass Fraction | Cd | Solid Isp [s] | Solid Burn Time [s] | Max Altitude Bound [km] | Max Velocity Bound [m/s] |
|---|---:|---:|---:|---:|---:|---:|
| LORA | 0.40 | 0.36 | 245 | 32 | 60 | 1,800 |
| ATACMS | 0.38 | 0.38 | 245 | 28 | 60 | 1,800 |
| Hyunmoo-2B | 0.42 | 0.40 | 250 | 45 | 80 | 2,200 |
| OTR-21 Tochka-U | 0.42 | 0.42 | 235 | 25 | 40 | 1,700 |

Ramjet equivalent Isp는 코드 내부에서 fuel LHV 기반 surrogate model로 계산한다. 현재 기본 연료는 hydrogen이다.

---

## 6. Fuel Ratio Assumption

본 연구에서는 전체 추진제 질량을 고체연료와 가스화연료로 나누어 계산한다.

```text
gas_ratio   = gasified fuel ratio
solid_ratio = 1 - gas_ratio
```

현재 validation에서는 다음 값을 사용하였다.

```text
GAS_RATIO = 0.30
FUEL_TYPE = "hydrogen"
```

`GAS_RATIO = 0.0`이면 ramjet fuel이 비활성화되므로 fuel type 변화가 trajectory에 영향을 주지 않는다.

---

## 7. Latest Validation Results

최신 validation에서는 네 모델 모두 다음 조건을 만족하였다.

- 중간 지면 접촉 없음
- 지면 접촉 후 재상승 없음
- ramjet mode 진입 확인
- dynamic pressure limit 초과 warning 없음
- velocity plot은 `After Boost Handoff` 기준으로 해석 가능

| Model | Final Range [km] | Max Altitude [km] | Initial V [m/s] | Max V [m/s] | Terminal V [m/s] | Max Mach | Max q [kPa] |
|---|---:|---:|---:|---:|---:|---:|---:|
| ATACMS | 40.851 | 5.961 | 688.800 | 717.001 | 690.153 | 2.223 | 291.741 |
| LORA | 38.197 | 5.811 | 688.800 | 695.889 | 684.717 | 2.128 | 287.163 |
| HYUNMOO_2B | 41.287 | 7.743 | 672.000 | 698.336 | 693.600 | 2.156 | 294.662 |
| TOCHKA | 36.713 | 4.410 | 684.700 | 695.432 | 684.895 | 2.129 | 287.312 |

---

## 8. Plot Output

각 스크립트는 모델별 plot directory에 결과를 저장한다.

| Model | Plot Directory |
|---|---|
| ATACMS | `ATACMS_Modechange_Plot/` |
| LORA | `LORA_Modechange_Plot/` |
| HYUNMOO_2B | `HYUNMOO_2B_Modechange_Plot/` |
| TOCHKA | `TOCHKA_Modechange_Plot/` |

생성되는 plot은 다음과 같다.

| Suffix | Plot Title | Meaning |
|---|---|---|
| `_01_trajectory.png` | `Missile Trajectory After Boost Handoff` | boost handoff 이후 downrange-altitude 궤적 |
| `_02_velocity.png` | `Velocity History After Boost Handoff` | boost handoff 이후 속도 이력 |
| `_03_mass.png` | `Mass History` | 질량 변화 |
| `_04_angles.png` | `Flight Path Angle and Control Angle` | 비행경로각 및 제어각 |
| `_05_throttle.png` | `Throttle History` | ramjet throttle history |
| `_06_modes.png` | `Mach / Dynamic Pressure / Propulsion Mode` | Mach, dynamic pressure, rocket/ramjet mode gate |

---

## 9. Running

각 모델별 optimizer는 아래와 같이 실행한다.

```bash
python missile_optimizer_ATACMS.py
python missile_optimizer_LORA.py
python missile_optimizer_HYUNMOO_2B.py
python missile_optimizer_TOCHKA.py
```

---

## 10. Interpretation Notes

이 모델은 공개 제원과 연구용 surrogate parameter를 사용한 개념 모델이다. 실제 무기체계 성능 재현 목적이 아니다.

해석 시 주의할 점은 다음과 같다.

- 현재 trajectory는 발사 직후 전체 궤적이 아니라 Mach 2 근처 boost handoff 이후 궤적이다.
- velocity plot의 초반 감속은 post-boost 상승 상태에서 gravity/drag가 ramjet acceleration보다 순간적으로 클 수 있기 때문에 발생한다.
- 따라서 velocity plot은 `Velocity History After Boost Handoff`로 해석해야 한다.
- ramjet 성능은 `Max Mach > 2`이고 ramjet mode sample이 존재할 때만 의미 있게 해석한다.
- q plot에서 dynamic pressure는 `max_q` line 아래에 있어야 한다.
- midcourse ground contact, reclimb, ramjet non-entry, q-limit exceedance warning이 나오면 해당 결과는 재튜닝 후 사용해야 한다.
