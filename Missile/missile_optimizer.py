from mpopt import mp
import numpy as np
import casadi as ca

# ============================================================
# 0. 실행 설정
# ============================================================
# 선택 가능:
# "ATACMS", "LORA", "HYUNMOO_2B", "TOCHKA"
MODEL_NAME = "TOCHKA"

# 가스화연료 비율
# 0.0이면 기존 고체로켓-only baseline에 가까움
# 0.1~0.5 정도로 바꿔가며 사거리/종속도 비교
# 연료 타입별 영향을 확인하려면 0.0이 아닌 값을 설정해야 함
GAS_RATIO = 0.30

# 연료 타입 선택
# "hydrogen", "methane", "ethylene", "kerosene"
FUEL_TYPE = "hydrogen"

# 목적함수 선택
# "range" 또는 "range_terminal_velocity"
OBJECTIVE = "range"

# 결과 plot 여부 (커스텀 플롯 표시 여부)
PLOT_RESULT = True


# ============================================================
# 1. 공개 제원 기반 기준 미사일 데이터베이스
# ============================================================
# 주의:
# - length, diameter, launch_mass, public_range는 공개 제원
# - dry_fraction, Cd, burn_time, Isp 등은 공개 제원 기반 해석을 위한 연구용 가정값
# - 실제 무기체계 성능 재현 목적이 아니라 비교 연구용 개념 모델임

MISSILE_DB = {
    "ATACMS": {
        "name": "ATACMS-class SRBM",
        "length": 3.98,                 # m
        "diameter": 0.61,               # m
        "launch_mass": 1673.0,          # kg, Block 1 기준
        "public_range": 300e3,          # m, 공개 최대 사거리 기준
        "propulsion": "single-stage solid",
        "dry_fraction": 0.38,           # 연구용 가정
        "cd": 0.38,                     # 연구용 가정
        "isp_solid": 245.0,             # s, 연구용 가정
        "isp_ramjet": 750.0,            # s, 등가 Isp 연구용 가정
        "solid_burn_time": 28.0,        # s, 연구용 가정
        "max_altitude": 60000.0,        # m
        "max_velocity": 1800.0,         # m/s
        #"max_q": 100000.0,              # Pa, dynamic pressure limit 연구용 가정
        "tf_min": 100.0,
        "tf_max": 350.0,
    },

    "LORA": {
        "name": "LORA-class SRBM",
        "length": 5.20,
        "diameter": 0.624,
        "launch_mass": 1600.0,
        "public_range": 280e3,
        "propulsion": "solid",
        "dry_fraction": 0.40,
        "cd": 0.36,
        "isp_solid": 245.0,
        "isp_ramjet": 760.0,
        "solid_burn_time": 32.0,
        "max_altitude": 60000.0,
        "max_velocity": 1800.0,
        #"max_q": 100000.0,
        "tf_min": 100.0,
        "tf_max": 350.0,
    },

    "HYUNMOO_2B": {
        "name": "Hyunmoo-2B-class SRBM",
        "length": 12.0,                 # >12 m 이므로 12 m를 보수적 기준값으로 사용
        "diameter": 0.90,
        "launch_mass": 5400.0,
        "public_range": 500e3,
        "propulsion": "two-stage solid",
        "dry_fraction": 0.42,
        "cd": 0.40,
        "isp_solid": 250.0,
        "isp_ramjet": 780.0,
        "solid_burn_time": 45.0,
        "max_altitude": 80000.0,
        "max_velocity": 2200.0,
        #"max_q": 100000.0,
        "tf_min": 120.0,
        "tf_max": 600.0,
    },

    "TOCHKA": {
        "name": "OTR-21 Tochka-class SRBM",
        "length": 6.40,
        "diameter": 0.655,
        "launch_mass": 2000.0,
        "public_range": 120e3,
        "propulsion": "single-stage solid",
        "dry_fraction": 0.42,
        "cd": 0.42,
        "isp_solid": 235.0,
        "isp_ramjet": 720.0,
        "solid_burn_time": 25.0,
        "max_altitude": 40000.0,
        "max_velocity": 1700.0,
        #"max_q": 100000.0,
        "tf_min": 80.0,
        "tf_max": 220.0,
    },
}


# ============================================================
# 2. 상수 정의
# ============================================================
G0 = 9.80665
R_EARTH = 6371000.0
RHO0 = 1.225

# 공력 제어 단순 모델
# alpha에 의해 양력 계수가 선형으로 변한다고 가정
CL_ALPHA = 2.5

# 램제트 작동 가능 마하수 범위에 대한 연구용 가정
RAMJET_MIN_MACH = 2.0
RAMJET_MAX_MACH = 5.5

# smooth step 폭
# 너무 작으면 if_else처럼 뾰족해져서 solver가 어려워질 수 있음
MASS_SMOOTH_WIDTH = 10.0
MACH_SMOOTH_WIDTH = 0.15
ALT_SMOOTH_WIDTH = 1000.0

# 연료별 저위 발열량 LHV [J/kg]
# 이 값으로 surrogate ramjet Isp를 계산
FUEL_LHV = {
    "hydrogen": 120.0e6,   # J/kg
    "methane": 50.0e6,     # J/kg
    "ethylene": 47.0e6,    # J/kg
    "kerosene": 43.0e6,    # J/kg
}

# LHV 기반 램제트 Isp 계산 상수
# 실제 램제트는 대기 공기 유입과 비행 에너지로 추가 성능을 얻으므로
# 단순 연료 LHV만으로는 매우 낮게 나온다. 연구용 surrogate로 보정.
RAMJET_LHV_EFFICIENCY = 0.70
RAMJET_LHV_SCALE = 3.2


# ============================================================
# 3. 유틸 함수
# ============================================================
def smooth_step(z, width):
    """
    CasADi 호환 smooth step 함수.
    z > 0이면 1에 가까워지고, z < 0이면 0에 가까워짐.
    """
    return 0.5 * (1.0 + ca.tanh(z / width))


def smooth_gate_between(value, low, high, width):
    """
    value가 low~high 사이에 있을 때 1에 가까워지는 smooth gate.
    """
    return smooth_step(value - low, width) * smooth_step(high - value, width)


def get_atmosphere(h):
    """
    간단한 지수 대기 모델.
    h: altitude [m]
    return:
        rho: air density [kg/m^3]
        a: speed of sound [m/s]
    """
    h_safe = ca.fmax(h, 0.0)

    rho = RHO0 * ca.exp(-h_safe / 7400.0)

    # 고도 11 km 이하에서는 음속 감소, 이후에는 단순 상수 가정
    a = ca.if_else(h_safe < 11000.0, 340.0 - 0.004 * h_safe, 295.0)

    return rho, a


def gravity(h):
    """
    고도에 따른 중력 변화.
    """
    return G0 * (R_EARTH / (R_EARTH + h)) ** 2


def build_model_params(model_name, gas_ratio, fuel_type):
    """
    공개 제원 + 연구용 가정값으로 해석 파라미터 구성.
    gas_ratio:
        전체 추진제 중 가스화연료로 배분하는 비율
    fuel_type:
        연료 타입 ("hydrogen", "methane", "ethylene", "kerosene")
    """
    base = MISSILE_DB[model_name].copy()

    m0 = base["launch_mass"]
    dry_mass = m0 * base["dry_fraction"]
    prop_mass = m0 - dry_mass

    gas_ratio = float(np.clip(gas_ratio, 0.0, 0.8))
    solid_ratio = 1.0 - gas_ratio

    solid_prop_mass = prop_mass * solid_ratio
    gas_prop_mass = prop_mass * gas_ratio

    area = np.pi * (base["diameter"] / 2.0) ** 2

    # 고체로켓 추력은 "추진제 질량, Isp, 연소시간"으로부터 역산한 연구용 값
    if solid_prop_mass > 1e-6:
        solid_thrust = solid_prop_mass * G0 * base["isp_solid"] / base["solid_burn_time"]
    else:
        solid_thrust = 0.0

    # 램제트 보조 추력은 고체로켓 추력 대비 비율로 둔 surrogate 값
    # 실제 엔진 모델이 들어오면 이 부분을 Cantera/quasi-1D table로 대체
    ramjet_ref_thrust = 0.35 * solid_thrust * (0.7 + 0.6 * gas_ratio)

    # 연료 LHV를 기반으로 램제트 equivalent Isp 계산
    if fuel_type not in FUEL_LHV:
        raise ValueError(f"Unknown fuel_type: {fuel_type}")

    lhv = FUEL_LHV[fuel_type]
    isp_ramjet = (
        RAMJET_LHV_SCALE
        * np.sqrt(2.0 * RAMJET_LHV_EFFICIENCY * lhv)
        / G0
    )

    base.update({
        "m0": m0,
        "dry_mass": dry_mass,
        "prop_mass": prop_mass,
        "solid_prop_mass": solid_prop_mass,
        "gas_prop_mass": gas_prop_mass,
        "solid_ratio": solid_ratio,
        "gas_ratio": gas_ratio,
        "fuel_type": fuel_type,
        "area": area,
        "solid_thrust": solid_thrust,
        "ramjet_ref_thrust": ramjet_ref_thrust,
        "isp_ramjet": isp_ramjet,
        "lhv": lhv,
    })

    return base


def ramjet_efficiency_surrogate(mach, gas_ratio, lhv):
    """
    가스발생기 램제트 연소 효율 surrogate 모델.
    실제 연구에서는 이 함수를 논문 기반 quasi-1D / Cantera 결과 테이블로 대체하면 됨.

    특징:
    - 특정 마하수 근처에서 효율이 좋아지는 형태
    - gas_ratio가 너무 낮거나 너무 높으면 효율이 떨어지는 형태
    - 연료 LHV에 따라 램제트 연소 효율도 달라진다고 가정
    """
    mach_eff = 0.55 + 0.30 * ca.exp(-((mach - 3.2) / 1.1) ** 2)

    # gas_ratio = 0.35~0.45 근처가 상대적으로 좋다고 가정한 단순 모델
    ratio_eff = 1.0 - 0.8 * (gas_ratio - 0.40) ** 2
    ratio_eff = ca.fmax(0.65, ca.fmin(1.0, ratio_eff))

    # 연료 LHV가 높을수록 램제트 화학/열역학 성능이 더 좋다고 가정
    fuel_eff = ca.sqrt(lhv / FUEL_LHV["kerosene"])
    fuel_eff = ca.fmax(0.80, ca.fmin(1.25, fuel_eff))

    return mach_eff * ratio_eff * fuel_eff


def propulsion_model(x, u, params):
    """
    추진 모델.
    상태:
        x[0] = R      range [m]
        x[1] = h      altitude [m]
        x[2] = v      velocity [m/s]
        x[3] = gamma  flight path angle [rad]
        x[4] = m      mass [kg]

    제어:
        u[0] = alpha    angle of attack [rad]
        u[1] = throttle ramjet throttle [0~1]
    """
    h = x[1]
    v = x[2]
    m = x[4]

    throttle = u[1]

    rho, a_sound = get_atmosphere(h)
    mach = v / a_sound

    # 연료 구간 분리 기준
    # m > dry + gas_prop 이면 고체로켓 boost 구간
    # dry < m < dry + gas_prop 이면 가스발생기 램제트 sustain 구간
    solid_boundary_mass = params["dry_mass"] + params["gas_prop_mass"]

    solid_on = smooth_step(m - solid_boundary_mass, MASS_SMOOTH_WIDTH)

    # 가스 연료가 있을 때만 ramjet 활성화
    # GAS_RATIO = 0.0이면 ramjet은 완전히 비활성화됨
    gas_fuel_available = smooth_step(m - params["dry_mass"], MASS_SMOOTH_WIDTH)
    has_gas_fuel = ca.fmin(1.0, params["gas_prop_mass"] * 1000.0)  # gas_prop_mass > 0.001 이면 1.0에 근접
    after_solid = 1.0 - solid_on

    # 램제트 작동 가능 조건: Mach, altitude gate
    mach_gate = smooth_gate_between(
        mach,
        RAMJET_MIN_MACH,
        RAMJET_MAX_MACH,
        MACH_SMOOTH_WIDTH
    )

    altitude_gate = smooth_gate_between(
        h,
        1000.0,
        params["max_altitude"],
        ALT_SMOOTH_WIDTH
    )

    # 가스 연료가 있을 때만 ramjet 활성화
    ramjet_on = has_gas_fuel * after_solid * gas_fuel_available * mach_gate * altitude_gate

    # 고체로켓 추력
    T_solid = solid_on * params["solid_thrust"]

    # 램제트 surrogate 추력
    eta_ram = ramjet_efficiency_surrogate(mach, params["gas_ratio"], params["lhv"])

    # 고도 증가에 따른 밀도 감소 효과를 약하게 반영
    density_ratio = ca.fmax(0.05, rho / RHO0)

    T_ramjet = (
        ramjet_on
        * throttle
        * params["ramjet_ref_thrust"]
        * eta_ram
        * density_ratio ** 0.20
    )

    Thrust = T_solid + T_ramjet

    # 질량 소모율
    mdot_solid = T_solid / (G0 * params["isp_solid"] + 1e-9)
    mdot_ramjet = T_ramjet / (G0 * params["isp_ramjet"] + 1e-9)

    mdot_total = mdot_solid + mdot_ramjet

    return Thrust, mdot_total, mach, eta_ram, solid_on, ramjet_on


# ============================================================
# 4. 동역학 방정식
# ============================================================
def missile_dynamics(x, u, t, params):
    R = x[0]
    h = x[1]
    v = x[2]
    gamma = x[3]
    m = x[4]

    alpha = u[0]

    rho, a_sound = get_atmosphere(h)
    g = gravity(h)

    q = 0.5 * rho * v ** 2

    # 항력
    Drag = q * params["area"] * params["cd"]

    # 양력 surrogate
    CL = CL_ALPHA * alpha
    Lift = q * params["area"] * CL

    Thrust, mdot, mach, eta_ram, solid_on, ramjet_on = propulsion_model(x, u, params)

    # 수치 안정성용 속도
    v_safe = ca.sqrt(v ** 2 + 1.0)

    dRdt = v * ca.cos(gamma)
    dhdt = v * ca.sin(gamma)

    dvdt = (Thrust - Drag) / m - g * ca.sin(gamma)

    # 간단한 point-mass flight path angle dynamics
    dgamdt = Lift / (m * v_safe) - g * ca.cos(gamma) / v_safe

    dmdt = -mdot

    return [dRdt, dhdt, dvdt, dgamdt, dmdt]


# ============================================================
# 5. OCP 생성 함수
# ============================================================
def create_ocp(params):
    """
    기존 코드의 단일 phase 구조를 유지하되,
    내부에서 boost / ramjet sustain / coast를 mass 기반으로 부드럽게 분리함.

    진짜 mpopt n_phases=3 구조는 다음 단계에서 확장 가능.
    """
    ocp = mp.OCP(n_states=5, n_controls=2, n_phases=1)

    # ---------------------------
    # 목적함수
    # ---------------------------
    if OBJECTIVE == "range":
        ocp.terminal_costs[0] = lambda xf, tf, x0, t0: -xf[0]

    elif OBJECTIVE == "range_terminal_velocity":
        # 단위 스케일 보정을 위해 range는 km 단위, velocity는 m/s 단위로 약하게 반영
        ocp.terminal_costs[0] = lambda xf, tf, x0, t0: -((xf[0] / 1000.0) + 0.05 * xf[2])

    else:
        raise ValueError("OBJECTIVE는 'range' 또는 'range_terminal_velocity'만 가능")

    # ---------------------------
    # 동역학
    # ---------------------------
    ocp.dynamics[0] = lambda x, u, t: missile_dynamics(x, u, t, params)

    # ---------------------------
    # 종단 조건
    # ---------------------------
    # 최종 고도 h(tf) = 0
    # 즉, 지면에 도달했을 때의 downrange를 사거리로 해석
    ocp.terminal_constraints[0] = lambda xf, tf, x0, t0: [xf[1]]

    # ---------------------------
    # Running cost: control effort 및 고도 비용 추가
    # ---------------------------
    ocp.running_costs[0] = lambda x, u, t: (
        1e-4 * u[0] ** 2
        + 1e-5 * u[1] ** 2
        + 1e-8 * x[1] ** 2
        + 1e-2 * x[3] ** 2
        + 1e-4 * ca.fmax(0.0, 50.0 - x[1]) ** 2
    )

    # ---------------------------
    # 초기 조건
    # ---------------------------
    # 지표면 근처에서 초기 속도를 조금 부여한 상태로 시작
    # 너무 낮은 속도 0에서 시작하면 gamma dynamics의 v 분모 때문에 solver가 어려워질 수 있음
    initial_gamma_deg = 30.0

    # 초기 속도를 더 현실적으로 설정 (고체로켓 boost 후 진입 속도 가정)
    v0_estimate = params["solid_thrust"] / params["m0"] * params["solid_burn_time"] / 1.8
    v0_estimate = np.clip(v0_estimate, 500.0, 1200.0)
    
    ocp.x00[0] = [
        0.0,                         # R0 [m]
        10.0,                        # h0 [m]
        v0_estimate,                 # v0 [m/s] - 부스트 후 진입 속도
        np.radians(initial_gamma_deg),# gamma0 [rad]
        params["m0"],                # m0 [kg]
    ]

    # ---------------------------
    # 초기 제어값 (모든 연료 타입에서 동일하게 설정)
    # u = [alpha, throttle]
    # ---------------------------
    ocp.u00[0] = [
        0.0,    # alpha0 = 0 rad (초기에는 수평)
        0.0,    # throttle0 = 0 (고체로켓만 작동)
    ]

    # ---------------------------
    # 상태변수 bounds
    # x = [R, h, v, gamma, m]
    # ---------------------------
    ocp.lbx[0] = [
        0.0,
        0.0,
        10.0,
        np.radians(-10.0),  # 실제 비행 경로에 가까운 gamma 범위
        params["dry_mass"],
    ]

    ocp.ubx[0] = [
        max(3.0 * params["public_range"], 200e3),
        params["max_altitude"],
        params["max_velocity"],
        np.radians(25.0),   # 실제 비행 경로에 가까운 gamma 범위
        params["m0"],
    ]

    # ---------------------------
    # 제어변수 bounds
    # u = [alpha, throttle]
    # ---------------------------
    ocp.lbu[0] = [
        np.radians(-2.0),  # alpha lower - 더 현실적이고 안정적으로
        0.0,               # throttle lower
    ]

    ocp.ubu[0] = [
        np.radians(2.0),   # alpha upper - 더 현실적이고 안정적으로
        1.0,               # throttle upper
    ]



    # ---------------------------
    # 시간 bounds
    # ---------------------------
    ocp.t00[0] = 0.0
    ocp.lbtf[0] = params["tf_min"]
    ocp.ubtf[0] = params["tf_max"]

    return ocp


# ============================================================
# 6. 결과 데이터 추출 함수
# ============================================================
def extract_solution_data(post):
    """
    mpopt 버전에 따라 post processor 함수 이름이 다를 수 있어 fallback 처리.
    """
    if hasattr(post, "get_data"):
        return post.get_data()

    if hasattr(post, "get_original_data"):
        return post.get_original_data()

    raise AttributeError("mpopt post processor에서 get_data 또는 get_original_data를 찾을 수 없습니다.")


# ============================================================
# 7. 단일 모델 실행 함수
# ============================================================
def solve_one_model(model_name, gas_ratio, fuel_type, plot=True):
    if gas_ratio == 0.0:
        print("\n[Warning] GAS_RATIO is 0.0: fuel_type will not affect trajectory because ramjet fuel is disabled.")
    params = build_model_params(model_name, gas_ratio, fuel_type)

    print("\n============================================================")
    print(f"Selected Model : {params['name']}")
    print(f"Propulsion     : {params['propulsion']}")
    print(f"Fuel Type      : {params['fuel_type']}")
    print(f"Length         : {params['length']:.3f} m")
    print(f"Diameter       : {params['diameter']:.3f} m")
    print(f"Launch mass    : {params['m0']:.1f} kg")
    print(f"Dry mass       : {params['dry_mass']:.1f} kg")
    print(f"Prop mass      : {params['prop_mass']:.1f} kg")
    print(f"Solid ratio    : {params['solid_ratio']:.2f}")
    print(f"Gas ratio      : {params['gas_ratio']:.2f}")
    print(f"Area           : {params['area']:.4f} m^2")
    print(f"Solid thrust   : {params['solid_thrust']:.1f} N")
    print(f"Ramjet T_ref   : {params['ramjet_ref_thrust']:.1f} N")
    print(f"Ramjet LHV     : {params['lhv'] / 1e6:.2f} MJ/kg")
    print(f"Ramjet Isp     : {params['isp_ramjet']:.1f} s")
    print("============================================================\n")

    ocp = create_ocp(params)

    n_segments = 20  # 최적화 속도 개선: 40 → 20
    poly_orders = [3] * n_segments

    mpo = mp.mpopt(
        ocp,
        n_segments=n_segments,
        poly_orders=poly_orders,
        scheme="LGR"
    )

    # Solver tolerance 강화: 수치 안정성 개선
    # 기본값보다 엄격한 tolerance로 설정하여 수렴성 개선
    solution = mpo.solve(
        ipopt_options={
            "tol": 1e-7,                    # 주 tolerance
            "constr_viol_tol": 1e-7,       # 제약 위반 tolerance
            "dual_inf_tol": 1e-7,          # Dual infeasibility tolerance
            "compl_inf_tol": 1e-7,         # Complementarity infeasibility
            "max_iter": 1500,              # 최대 반복 횟수 증가
            "acceptable_tol": 1e-6,        # Acceptable tolerance (빠른 수렴용)
            "acceptable_constr_viol_tol": 1e-6,
        }
    )

    post = mpo.process_results(
        solution,
        plot=plot,
        residual_dx=False,
        residual_x=False
    )

    x_data, u_data, t_data, _ = extract_solution_data(post)

    # 결과 출력
    xf = x_data[-1, :]
    uf = u_data[-1, :] if len(u_data) > 0 else [np.nan, np.nan]

    print("\n==================== Result Summary ====================")
    print(f"Model              : {params['name']}")
    print(f"Fuel Type          : {params['fuel_type']}")
    print(f"Gas ratio          : {params['gas_ratio']:.2f}")
    print(f"Final range        : {xf[0] / 1000.0:.3f} km")
    print(f"Final altitude     : {xf[1]:.3f} m")
    print(f"Terminal velocity  : {xf[2]:.3f} m/s")
    print(f"Terminal gamma     : {np.degrees(xf[3]):.3f} deg")
    print(f"Final mass         : {xf[4]:.3f} kg")
    print(f"Final time         : {np.asarray(t_data[-1]).item():.3f} s")
    print("========================================================\n")

    # ===============================
    # Trajectory Summary 추가
    # ===============================
    R = x_data[:, 0]
    h = x_data[:, 1]
    V = x_data[:, 2]
    gamma = x_data[:, 3]
    m = x_data[:, 4]

    alpha = u_data[:, 0]
    throttle = u_data[:, 1]

    print("\n========== Trajectory Summary ==========")
    print(f"Final time              : {np.asarray(t_data[-1]).item():.3f} s")
    print(f"Final range             : {R[-1] / 1000:.3f} km")
    print(f"Max altitude            : {np.max(h) / 1000:.3f} km")
    print(f"Terminal altitude       : {h[-1]:.3f} m")
    print(f"Initial velocity        : {V[0]:.3f} m/s")
    print(f"Max velocity            : {np.max(V):.3f} m/s")
    print(f"Terminal velocity       : {V[-1]:.3f} m/s")
    print(f"Initial mass            : {m[0]:.3f} kg")
    print(f"Final mass              : {m[-1]:.3f} kg")
    print(f"Min gamma               : {np.degrees(np.min(gamma)):.3f} deg")
    print(f"Max gamma               : {np.degrees(np.max(gamma)):.3f} deg")
    print(f"Min alpha               : {np.degrees(np.min(alpha)):.3f} deg")
    print(f"Max alpha               : {np.degrees(np.max(alpha)):.3f} deg")
    print(f"Min throttle            : {np.min(throttle):.3f}")
    print(f"Max throttle            : {np.max(throttle):.3f}")
    print("========================================\n")

    return params, solution, post, x_data, u_data, t_data


def plot_trajectory_results(x_data, u_data, t_data, save_path=None):
    """
    궤적 결과를 더 보기 좋게 시각화.
    save_path: 플롯을 저장할 경로 (None이면 저장 안 함)
    """
    import matplotlib.pyplot as plt
    
    R = x_data[:, 0]
    h = x_data[:, 1]
    V = x_data[:, 2]
    gamma = x_data[:, 3]
    m = x_data[:, 4]

    alpha = u_data[:, 0]
    throttle = u_data[:, 1]

    # Plot 1: 3D Trajectory (Range vs Altitude)
    plt.figure(figsize=(12, 5))
    plt.plot(R / 1000, h / 1000, "o-", linewidth=2, markersize=4)
    plt.xlabel("Downrange [km]", fontsize=11)
    plt.ylabel("Altitude [km]", fontsize=11)
    plt.title("Missile Trajectory", fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(f"{save_path}_01_trajectory.png", dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}_01_trajectory.png")
    plt.show()

    # Plot 2: Velocity History
    plt.figure(figsize=(12, 5))
    plt.plot(t_data, V, "o-", linewidth=2, markersize=4, color='tab:orange')
    plt.xlabel("Time [s]", fontsize=11)
    plt.ylabel("Velocity [m/s]", fontsize=11)
    plt.title("Velocity History", fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(f"{save_path}_02_velocity.png", dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}_02_velocity.png")
    plt.show()

    # Plot 3: Mass History
    plt.figure(figsize=(12, 5))
    plt.plot(t_data, m, "o-", linewidth=2, markersize=4, color='tab:green')
    plt.xlabel("Time [s]", fontsize=11)
    plt.ylabel("Mass [kg]", fontsize=11)
    plt.title("Mass History", fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(f"{save_path}_03_mass.png", dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}_03_mass.png")
    plt.show()

    # Plot 4: Flight Path Angle and Control Angle
    plt.figure(figsize=(12, 5))
    plt.plot(t_data, np.degrees(gamma), "o-", linewidth=2, markersize=4, label="Flight Path Angle (γ)")
    plt.plot(t_data, np.degrees(alpha), "s-", linewidth=2, markersize=4, label="Angle of Attack (α)")
    plt.xlabel("Time [s]", fontsize=11)
    plt.ylabel("Angle [deg]", fontsize=11)
    plt.title("Flight Path Angle and Control Angle", fontsize=12, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(f"{save_path}_04_angles.png", dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}_04_angles.png")
    plt.show()

    # Plot 5: Throttle History
    plt.figure(figsize=(12, 5))
    plt.plot(t_data, throttle, "o-", linewidth=2, markersize=4, color='tab:red')
    plt.xlabel("Time [s]", fontsize=11)
    plt.ylabel("Throttle", fontsize=11)
    plt.title("Throttle History", fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(f"{save_path}_05_throttle.png", dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}_05_throttle.png")
    plt.show()

    return None


# ============================================================
# 8. 실행
# ============================================================
if __name__ == "__main__":
    import datetime
    
    # 여러 연료 타입으로 테스트
    fuel_types = ["hydrogen", "methane", "ethylene", "kerosene"]
    
    for fuel in fuel_types:
        print(f"\n{'='*60}")
        print(f"Testing with Fuel: {fuel.upper()}")
        print(f"{'='*60}")
        
        params, solution, post, x_data, u_data, t_data = solve_one_model(
            MODEL_NAME,
            GAS_RATIO,
            fuel,
            plot=PLOT_RESULT
        )
        
        # 커스텀 플롯 표시 및 저장 (PLOT_RESULT가 True일 때)
        if PLOT_RESULT:
            # 결과 저장 경로
            save_dir = f"{MODEL_NAME}_Plot"
            import os
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(save_dir, f"trajectory_{MODEL_NAME}_{fuel}_{GAS_RATIO:.2f}_{timestamp}")
            
            plot_trajectory_results(x_data, u_data, t_data, save_path=save_path)
    
    mp.plt.show()