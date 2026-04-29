## Public Baseline Missile Parameters for mpopt Model

본 연구에서는 공개 제원 기반의 전술 탄도미사일을 baseline model로 사용한다.  
목적은 실제 무기체계의 상세 성능을 재현하는 것이 아니라, 공개된 길이, 직경, 질량, 추진 방식, 사거리 정보를 바탕으로  
mpopt 기반 multi-phase trajectory optimization에 사용할 수 있는 개념적 기준 모델을 구성하는 것이다.

---

## 1. Candidate Baseline Missile Models

| Priority | Model | Reason | mpopt Suitability |
|---:|---|---|---|
| 1 | LORA-class model | ATACMS와 질량·직경이 비슷한 단거리 탄도미사일 | Very good |
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

## 3. Model Assumption Values Used in mpopt Code

아래 값들은 공개 제원이 아니라, mpopt 기반 개념 모델을 구성하기 위해 설정한 연구용 가정값이다.  
실제 미사일 성능을 의미하지 않으며, 모델 비교와 민감도 분석을 위한 surrogate parameter로 사용한다.

| Model | Dry Mass Fraction | Cd | Solid Isp [s] | Ramjet Equivalent Isp [s] | Solid Burn Time [s] | Max Altitude Bound [km] | Max Velocity Bound [m/s] | Time Bound [s] |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| LORA | 0.40 | 0.36 | 245 | 760 | 32 | 60 | 1,800 | 30~350 |
| ATACMS | 0.38 | 0.38 | 245 | 750 | 28 | 60 | 1,800 | 30~350 |
| Hyunmoo-2B | 0.42 | 0.40 | 250 | 780 | 45 | 80 | 2,200 | 40~600 |
| OTR-21 Tochka-U | 0.42 | 0.42 | 235 | 720 | 25 | 40 | 1,700 | 20~220 |

---

## 4. Fuel Ratio Assumption

본 연구에서는 전체 추진제 질량을 고체연료와 가스화연료로 나누어 계산한다.

```text
gas_ratio   = gasified fuel ratio
solid_ratio = 1 - gas_ratio