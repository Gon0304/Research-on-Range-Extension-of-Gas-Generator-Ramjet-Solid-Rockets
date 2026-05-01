## Public Baseline Missile Parameters for mpopt Model

본 연구에서는 공개 제원 기반의 전술 탄도미사일을 baseline model로 사용한다.  
목적은 실제 무기체계의 상세 성능을 재현하는 것이 아니라, 공개된 길이, 직경, 질량, 추진 방식, 사거리 정보를 바탕으로  
mpopt 기반 multi-phase trajectory optimization에 사용할 수 있는 개념적 기준 모델을 구성하는 것이다.


로라(미사일) [이스라엘 항공 우주산업에서 개발한 전술용 준탄도 미사일]
<img width="960" height="345" alt="image" src="https://github.com/user-attachments/assets/744dbf00-6fe1-4d2f-8097-60147895db04" />

ATACMS(미사일) [미국 방산산업체 LTV에서 설계 및 제조한 단거리 초음속 전술 탄도 미사일]
<img width="250" height="375" alt="image" src="https://github.com/user-attachments/assets/d43ea3c6-6298-4d52-90d0-759c677f44e1" />

현무-II(미사일) [대한민국 육군 미사일전략사령부에서 운용하는 전역 탄도 미사일]
<img width="500" height="423" alt="image" src="https://github.com/user-attachments/assets/f405a248-4eb6-4d35-b119-1295e8c5a377" />

OTR-21 Tochka-U(미사일) [소련의 전술 탄도 미사일]
<img width="1024" height="683" alt="image" src="https://github.com/user-attachments/assets/6ea8badd-6ae3-4e71-a296-245c3b0edb26" />



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
```


---
## ATACMS plot

### plot 1: Missile Trajectory (미사일 궤적)
<img width="1786" height="734" alt="image" src="https://github.com/user-attachments/assets/c5b21b92-158b-404b-94dc-a5465320dde8" />

- X축: 수평 거리 (Downrange, km)
- Y축: 고도 (Altitude, km)
- 설명:
  - 발사점: (0, 0) 근처에서 시작 
  - 상승 단계: 0~35km 수평거리에서 빠르게 상승
  - 최고점: 약 31.5km 고도, 35km 거리
  - 하강 단계: 35~73km 거리에서 서서히 하강
  - 착지점: 약 73km 거리에서 지표면 도달
  - 형태: 이상적인 포물선 미사일 궤적

### plot 2: Velocity History (속도 이력)
<img width="1786" height="734" alt="image" src="https://github.com/user-attachments/assets/d2aae4cb-b981-4b2b-9308-1e4bcf53e399" />

- X축: 시간 (0~100초)
- Y축: 미사일 속도 (m/s)
- 설명:
  - 0초: 초기 속도 579 m/s (부스트 후 진입)
  - ~25초: 최대 속도 1201 m/s (고체로켓 최고 추력 단계)
  - 25~60초: 속도 감소 (램제트 가동, 상승 단계)
  - 60~100초: 속도 재상승 후 하강 (재진입)
  - 100초: 종말 속도 619 m/s

### plot 3: Mass History (질량 이력)
<img width="1786" height="734" alt="image" src="https://github.com/user-attachments/assets/2d9d8488-45e2-4238-aeda-aaf94e7524f8" />

- X축: 시간 (0~100초)
- Y축: 미사일 질량 (kg)
- 설명:
  - 0초: 초기 질량 1673 kg (발사체 총질량)
  - 0~28초: 급격한 감소 (고체로켓 연소)
  - 약 673 kg의 고체 추진제 소비
  - 추진제 연소량: 0~28초에 대부분 소비
  - 28~100초: 거의 일정 (약 930 kg)
  - 고체로켓 완전 연소 후 구조체만 남음
  - 램제트 연소로 인한 질량 감소는 모델에서 무시
  - 100초: 최종 질량 900.659 kg

### plot 4: Flight Path Angle and Control Angle(비행경로각 및 제어각)
<img width="1786" height="734" alt="image" src="https://github.com/user-attachments/assets/0949f4d9-b317-484a-952b-b47eeaed977a" />

- **X-axis:** Time [s]  
- **Y-axis:** Angle [deg]

#### Blue Line: γ = Flight Path Angle

`γ`는 미사일의 비행 방향이 수평선과 이루는 각도를 의미한다.

| Time [s] | Trend | Interpretation |
|---:|---|---|
| 0~3 | +10° → +60°로 급격히 증가 | 초기 부스트 단계에서 빠르게 상승각 형성 |
| 3~40 | 약 +50°~+60° 유지 | 상승 단계, 거의 수직에 가까운 고각 상승 |
| 40~50 | 급격히 감소 | 최고점 통과 후 하강 궤적으로 전환 |
| 50~90 | 약 -40° 부근 유지 | 하강 단계에서 안정적인 재진입 궤적 형성 |
| 90~100 | -40° → -12°로 증가 | 지면 접근 시 하강각 완화 |

#### Orange Line: α = Angle of Attack

`α`는 미사일의 공격각 또는 궤적 제어 입력을 의미한다.

| Item | Description |
|---|---|
| Control range | 약 -5° ~ +5° |
| Initial behavior | 초기 구간에서 작은 진동 발생 |
| Main flight phase | 대부분 0° 근처 유지 |
| Terminal phase | 90~100초 구간에서 약간 양수 방향으로 증가 |
| Interpretation | 제어 입력이 작게 유지되므로, 현재 모델에서는 큰 자세 변화 없이 궤적을 형성하는 것으로 해석 가능 |

> 현재 결과에서 `γ`는 상승, 최고점 통과, 하강 단계의 전형적인 비행경로각 변화를 보여준다.  
> 반면 `α`는 제어 한계 내에서 대부분 작은 값을 유지하므로, 최적화 과정에서 비교적 작은 조종 입력으로 궤적을 구성한 것으로 볼 수 있다.

### plot 5: Throttle History (스로틀/추력 제어 이력)
<img width="1786" height="734" alt="image" src="https://github.com/user-attachments/assets/35ff6306-a46f-45c0-87b5-b5eab9b843d3" />

- X축: 시간 (0~100초)
- Y축: 스로틀 값 (0~1, 정규화된 값)
  - 0 = 엔진 OFF
  - 1 = 최대 추력 (100%)

- 단계별 분석:

|시간	| 스로틀	| 엔진	| 설명 |
|---|---:|---:|---|
| 0~25초	| ~0.50 |	고체로켓	| 일정한 고체 추진제 연소 |
| 25~30초	| 0.50→0	| 고체로켓	| 고체 연소 종료 (급격히 감소) |
| 30~55초	| ~0	|  | 부양	엔진 OFF, 관성 비행 |
| 55~75초	| 0→0.77	| | 램제트	램제트 점화 및 가속 |
| 75~90초 |	0.77→0.4	| | 램제트	램제트 출력 감소 시작 |
| 90~100초	| ~0.5	| | 램제트	하강 단계 유지 |

- 의미:
  - 최대 사거리를 위해 초반 고체로켓 강력 가속 후 후반 램제트로 상승 단계 보조
  - 최종 단계에서 약 50% 스로틀로 대기 재진입 준비
