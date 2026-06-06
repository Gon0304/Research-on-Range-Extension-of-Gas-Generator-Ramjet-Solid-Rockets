import os

os.makedirs(os.path.join(os.getcwd(), ".matplotlib"), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), ".cache"), exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.getcwd(), ".matplotlib"))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("XDG_CACHE_HOME", os.path.join(os.getcwd(), ".cache"))

from mpopt import mp
import numpy as np
import casadi as ca

# ============================================================
# 0. 실행 설정
# ============================================================
# 선택 가능:
# "ATACMS", "LORA", "HYUNMOO_2B", "TOCHKA"
# LORA 전용 mode-change optimizer.
MODEL_NAMES = ["LORA"]

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

# True이면 네 연료를 모두 비교, False이면 FUEL_TYPE 하나만 실행
RUN_ALL_FUELS = False

# Collocation state에 gamma jump가 남는 경우가 있어, 최종 plot/summary는
# 최적화된 throttle history를 실제 ODE에 다시 넣어 forward replay한 결과를 사용한다.
REPLAY_DYNAMICS_FOR_PLOTS = True

# 단일 phase를 기본으로 쓴다.
# 2-phase는 phase boundary artifact로 두 봉우리 궤도가 생길 수 있어 기본 비활성화한다.
USE_TWO_PHASE = False

# 단일 phase에서 terminal impact만 허용하는 효과를 주기 위한 soft constraint 설정.
MIDCOURSE_GROUND_CLEARANCE = 300.0  # m
MIDCOURSE_GROUND_PENALTY = 2.0e-7


# Ramjet 연구용 trajectory라면 M=2 직전 boost-handoff에서 시작하는 것이 안정적이다.
BOOST_HANDOFF_MACH_BY_MODEL = {
    "ATACMS": 2.10,
    "LORA": 2.10,
    "HYUNMOO_2B": 1.85,
    "TOCHKA": 1.85,
}

BOOST_HANDOFF_ALTITUDE_BY_MODEL = {
    "ATACMS": 3000.0,
    "LORA": 3000.0,
    "HYUNMOO_2B": 1000.0,
    "TOCHKA": 1000.0,
}


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
        "max_q": 300000.0,              # Pa, dynamic pressure limit 연구용 가정
        "tf_min": 30.0,
        "tf_max": 80.0,
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
        "max_q": 300000.0,
        "tf_min": 30.0,
        "tf_max": 80.0,
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
        "max_q": 300000.0,
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
        "max_q": 240000.0,
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
# mode-change 검증 파일에서는 비현실적 재상승을 막기 위해 lift steering을 끈다.
# 필요하면 이후 별도 guidance 모델을 넣고 다시 활성화한다.
CL_ALPHA = 0.0

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


def smooth_positive(z, width):
    """
    fmax(0, z)의 미분 가능한 근사.
    """
    return 0.5 * (z + ca.sqrt(z ** 2 + width ** 2))


def smooth_lower_bound(value, lower, width):
    """
    fmax(lower, value)의 미분 가능한 근사.
    """
    return lower + smooth_positive(value - lower, width)


def smooth_upper_bound(value, upper, width):
    """
    fmin(upper, value)의 미분 가능한 근사.
    """
    return upper - smooth_positive(upper - value, width)


def smooth_clip(value, lower, upper, width):
    """
    lower <= value <= upper clamp의 미분 가능한 근사.
    """
    return smooth_upper_bound(smooth_lower_bound(value, lower, width), upper, width)


def smooth_gate_between(value, low, high, width):
    """
    value가 low~high 사이에 있을 때 1에 가까워지는 smooth gate.
    """
    return smooth_step(value - low, width) * smooth_step(high - value, width)


def np_smooth_step(z, width):
    """
    Plot/post-process용 NumPy smooth step.
    """
    return 0.5 * (1.0 + np.tanh(np.asarray(z) / width))


def np_smooth_gate_between(value, low, high, width):
    """
    Plot/post-process용 NumPy interval gate.
    """
    value = np.asarray(value)
    return np_smooth_step(value - low, width) * np_smooth_step(high - value, width)


def np_atmosphere(h):
    """
    초기 guess와 post-process용 NumPy 대기 모델.
    """
    h_safe = np.maximum(np.asarray(h), 0.0)
    rho = RHO0 * np.exp(-h_safe / 7400.0)
    a_sound = np.where(h_safe < 11000.0, 340.0 - 0.004 * h_safe, 295.0)
    return rho, a_sound


def get_atmosphere(h):
    """
    간단한 지수 대기 모델.
    h: altitude [m]
    return:
        rho: air density [kg/m^3]
        a: speed of sound [m/s]
    """
    h_safe = smooth_lower_bound(h, 0.0, 1.0)

    rho = RHO0 * ca.exp(-h_safe / 7400.0)

    # 고도 11 km 이하에서는 음속 감소, 이후에는 단순 상수 가정
    a = ca.if_else(h_safe < 11000.0, 340.0 - 0.004 * h_safe, 295.0)

    return rho, a


def boost_handoff_initial_state(params):
    """
    ATACMS/LORA처럼 기존 thrust/mass 추정만으로 M=2에 못 가는 모델을 위해
    Mach 기준 boost handoff 초기조건을 만든다.
    """
    h0 = BOOST_HANDOFF_ALTITUDE_BY_MODEL.get(params["model_name"], 1000.0)
    _, a_sound = np_atmosphere(h0)
    target_mach = BOOST_HANDOFF_MACH_BY_MODEL.get(params["model_name"], 1.85)
    mach_based_v0 = target_mach * float(a_sound)

    thrust_based_v0 = params["solid_thrust"] / params["m0"] * params["solid_burn_time"] / 2.0
    v0 = max(mach_based_v0, thrust_based_v0)
    v0 = np.clip(v0, 450.0, 0.95 * params["max_velocity"])

    gamma0 = np.radians(20.0)
    return [0.0, h0, v0, gamma0, params["m0"]]


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
        "model_name": model_name,
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
    ratio_eff = smooth_clip(ratio_eff, 0.65, 1.0, 1e-3)

    # 연료 LHV가 높을수록 램제트 화학/열역학 성능이 더 좋다고 가정
    fuel_eff = ca.sqrt(lhv / FUEL_LHV["kerosene"])
    fuel_eff = smooth_clip(fuel_eff, 0.80, 1.25, 1e-3)

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

    # 추진제 잔량 surrogate.
    # 단일 mass state만 유지하므로 고체/가스 연료량은 mass window로 근사한다.
    solid_boundary_mass = params["dry_mass"] + params["gas_prop_mass"]
    solid_fuel_available = smooth_step(m - solid_boundary_mass, MASS_SMOOTH_WIDTH)
    gas_fuel_available = smooth_step(m - params["dry_mass"], MASS_SMOOTH_WIDTH)

    # 교수님 코멘트 반영:
    # M < 2에서는 rocket/boost mode, M > 2에서는 ducted ramjet mode로 부드럽게 전환한다.
    # if_else hard switch 대신 tanh gate를 써서 NLP solver가 미분 가능한 문제를 보게 한다.
    ramjet_mach_on = smooth_step(mach - RAMJET_MIN_MACH, MACH_SMOOTH_WIDTH)
    rocket_mach_on = 1.0 - ramjet_mach_on
    high_mach_limit = smooth_step(RAMJET_MAX_MACH - mach, MACH_SMOOTH_WIDTH)

    altitude_gate = smooth_gate_between(
        h,
        1000.0,
        params["max_altitude"],
        ALT_SMOOTH_WIDTH
    )

    has_gas_fuel = min(1.0, params["gas_prop_mass"] * 1000.0)
    ramjet_on = has_gas_fuel * gas_fuel_available * ramjet_mach_on * high_mach_limit * altitude_gate
    rocket_on = solid_fuel_available * rocket_mach_on

    # 고체로켓 추력
    T_solid = rocket_on * params["solid_thrust"]

    # 램제트 surrogate 추력
    eta_ram = ramjet_efficiency_surrogate(mach, params["gas_ratio"], params["lhv"])

    # 고도 증가에 따른 밀도 감소 효과를 약하게 반영
    density_ratio = smooth_lower_bound(rho / RHO0, 0.05, 1e-3)

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

    return Thrust, mdot_total, mach, eta_ram, rocket_on, ramjet_on


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
    Mode-change 실험용 OCP.
    기본은 단일 phase이며, 상승-정점-하강 형태를 보존하기 위해
    Mach 기반 boost handoff와 soft low-altitude penalty/warning을 사용한다.
    """
    n_phases = 2 if USE_TWO_PHASE else 1
    terminal_phase = n_phases - 1
    ocp = mp.OCP(n_states=5, n_controls=2, n_phases=n_phases)

    # ---------------------------
    # 목적함수
    # ---------------------------
    def range_terminal_cost(xf, tf, x0, t0):
        if OBJECTIVE == "range":
            return (
                -xf[0] / 1000.0
                + 35.0 * smooth_positive(xf[3], 1e-3) ** 2
                + 2.0e-3 * tf
            )
        if OBJECTIVE == "range_terminal_velocity":
            return (
                -((xf[0] / 1000.0) + 0.05 * xf[2])
                + 35.0 * smooth_positive(xf[3], 1e-3) ** 2
                + 2.0e-3 * tf
            )
        raise ValueError("OBJECTIVE는 'range' 또는 'range_terminal_velocity'만 가능")

    if OBJECTIVE == "range":
        ocp.terminal_costs[terminal_phase] = range_terminal_cost

    elif OBJECTIVE == "range_terminal_velocity":
        ocp.terminal_costs[terminal_phase] = range_terminal_cost

    else:
        raise ValueError("OBJECTIVE는 'range' 또는 'range_terminal_velocity'만 가능")

    # ---------------------------
    # 동역학
    # ---------------------------
    for phase in range(n_phases):
        ocp.dynamics[phase] = lambda x, u, t, params=params: missile_dynamics(x, u, t, params)

    # ---------------------------
    # 종단 조건
    # ---------------------------
    # 최종 고도 h(tf) = 0
    # 즉, 지면에 도달했을 때의 downrange를 사거리로 해석
    ocp.terminal_constraints[terminal_phase] = lambda xf, tf, x0, t0: [xf[1]]

    # ---------------------------
    # 경로 제약
    # ---------------------------
    # 동압 제한을 명시해서 저고도 고속 비행으로 range만 억지로 키우는 해를 막는다.
    # mpopt 기본 path constraint bound는 g(x,u,t) <= 0 형태이다.
    ocp.path_constraints[terminal_phase] = lambda x, u, t: [
        0.5 * get_atmosphere(x[1])[0] * x[2] ** 2 - params["max_q"],
    ]
    if USE_TWO_PHASE:
        ocp.path_constraints[0] = lambda x, u, t: [
            0.5 * get_atmosphere(x[1])[0] * x[2] ** 2 - params["max_q"],
            MIDCOURSE_GROUND_CLEARANCE - x[1],
        ]

    # ---------------------------
    # Running cost: control effort 및 고도 비용 추가
    # ---------------------------
    def running_cost(x, u, t):
        return (
            1.2e1 * u[0] ** 2
            + 2e-3 * u[1] ** 2
            + 8e-2 * x[3] ** 2
            + MIDCOURSE_GROUND_PENALTY * smooth_positive(MIDCOURSE_GROUND_CLEARANCE - x[1], 5.0) ** 2
            + 1e-12 * (0.5 * get_atmosphere(x[1])[0] * x[2] ** 2) ** 2
        )

    for phase in range(n_phases):
        ocp.running_costs[phase] = running_cost

    # ---------------------------
    # 초기 조건
    # ---------------------------
    x00 = boost_handoff_initial_state(params)
    ocp.x00[0] = x00
    ocp.xf0[0] = [
        0.35 * params["public_range"],
        0.0,
        0.75 * x00[2],
        np.radians(-25.0),
        max(params["dry_mass"], params["m0"] - 0.75 * params["solid_prop_mass"]),
    ]
    if USE_TWO_PHASE:
        ocp.x00[1] = ocp.xf0[0]
        ocp.xf0[1] = [
            0.80 * params["public_range"],
            0.0,
            0.55 * x00[2],
            np.radians(-35.0),
            max(params["dry_mass"], params["m0"] - params["solid_prop_mass"]),
        ]

    # ---------------------------
    # 초기 제어값 (모든 연료 타입에서 동일하게 설정)
    # u = [alpha, throttle]
    # ---------------------------
    for phase in range(n_phases):
        ocp.u00[phase] = [
            0.0,
            0.75,
        ]

    # ---------------------------
    # 상태변수 bounds
    # x = [R, h, v, gamma, m]
    # ---------------------------
    for phase in range(n_phases):
        ocp.lbx[phase] = [
            0.0,
            MIDCOURSE_GROUND_CLEARANCE if USE_TWO_PHASE and phase == 0 else 0.0,
            50.0,
            np.radians(-80.0),
            params["dry_mass"],
        ]

        ocp.ubx[phase] = [
            max(3.0 * params["public_range"], 200e3),
            params["max_altitude"],
            params["max_velocity"],
            np.radians(30.0),
            params["m0"],
        ]

    # ---------------------------
    # 제어변수 bounds
    # u = [alpha, throttle]
    # ---------------------------
    for phase in range(n_phases):
        ocp.lbu[phase] = [
            -1.0e-6,
            0.0,
        ]

        ocp.ubu[phase] = [
            1.0e-6,
            1.0,
        ]



    # ---------------------------
    # 시간 bounds
    # ---------------------------
    ocp.t00[0] = 0.0
    if USE_TWO_PHASE:
        ocp.t00[1] = 0.0
        ocp.lbtf[0] = 0.45 * params["tf_min"]
        ocp.ubtf[0] = 0.70 * params["tf_max"]
        ocp.lbtf[1] = 0.35 * params["tf_min"]
        ocp.ubtf[1] = 0.70 * params["tf_max"]
    else:
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


def sort_solution_by_time(x_data, u_data, t_data):
    """
    mpopt post data가 collocation 내부 순서로 섞여 나오는 경우가 있어
    plot/diagnostics 전에 시간순으로 정렬한다.
    """
    t_flat = np.asarray(t_data).reshape(-1)
    order = np.argsort(t_flat, kind="mergesort")
    return x_data[order, :], u_data[order, :], t_flat[order]


def numeric_propulsion_model(x, u, params):
    """
    Forward replay용 NumPy 추진 모델.
    """
    h = x[1]
    v = x[2]
    m = x[4]
    throttle = float(np.clip(u[1], 0.0, 1.0))

    rho, a_sound = np_atmosphere(h)
    rho = float(rho)
    a_sound = float(a_sound)
    mach = v / a_sound

    solid_boundary_mass = params["dry_mass"] + params["gas_prop_mass"]
    solid_fuel_available = np_smooth_step(m - solid_boundary_mass, MASS_SMOOTH_WIDTH)
    gas_fuel_available = np_smooth_step(m - params["dry_mass"], MASS_SMOOTH_WIDTH)

    ramjet_mach_on = np_smooth_step(mach - RAMJET_MIN_MACH, MACH_SMOOTH_WIDTH)
    rocket_mach_on = 1.0 - ramjet_mach_on
    high_mach_limit = np_smooth_step(RAMJET_MAX_MACH - mach, MACH_SMOOTH_WIDTH)
    altitude_gate = np_smooth_gate_between(h, 1000.0, params["max_altitude"], ALT_SMOOTH_WIDTH)
    has_gas_fuel = min(1.0, params["gas_prop_mass"] * 1000.0)

    rocket_on = solid_fuel_available * rocket_mach_on
    ramjet_on = has_gas_fuel * gas_fuel_available * ramjet_mach_on * high_mach_limit * altitude_gate

    eta_ram = 0.55 + 0.30 * np.exp(-((mach - 3.2) / 1.1) ** 2)
    ratio_eff = np.clip(1.0 - 0.8 * (params["gas_ratio"] - 0.40) ** 2, 0.65, 1.0)
    fuel_eff = np.clip(np.sqrt(params["lhv"] / FUEL_LHV["kerosene"]), 0.80, 1.25)
    eta_ram = eta_ram * ratio_eff * fuel_eff

    density_ratio = max(0.05, rho / RHO0)
    thrust_solid = rocket_on * params["solid_thrust"]
    thrust_ramjet = (
        ramjet_on
        * throttle
        * params["ramjet_ref_thrust"]
        * eta_ram
        * density_ratio ** 0.20
    )

    thrust = thrust_solid + thrust_ramjet
    mdot = (
        thrust_solid / (G0 * params["isp_solid"] + 1e-9)
        + thrust_ramjet / (G0 * params["isp_ramjet"] + 1e-9)
    )

    return thrust, mdot


def numeric_missile_dynamics(x, u, params):
    """
    Forward replay용 point-mass dynamics.
    """
    h = x[1]
    v = max(float(x[2]), 1.0)
    gamma = x[3]
    m = max(float(x[4]), params["dry_mass"])
    alpha = float(u[0])

    rho, _ = np_atmosphere(h)
    rho = float(rho)
    g = G0 * (R_EARTH / (R_EARTH + max(h, 0.0))) ** 2
    q = 0.5 * rho * v ** 2

    drag = q * params["area"] * params["cd"]
    lift = q * params["area"] * CL_ALPHA * alpha
    thrust, mdot = numeric_propulsion_model(x, u, params)

    v_safe = np.sqrt(v ** 2 + 1.0)
    return np.array([
        v * np.cos(gamma),
        v * np.sin(gamma),
        (thrust - drag) / m - g * np.sin(gamma),
        lift / (m * v_safe) - g * np.cos(gamma) / v_safe,
        -mdot,
    ], dtype=float)


def replay_solution_dynamics(x_data, u_data, t_data, params, dt=0.25):
    """
    최적화 control을 실제 ODE에 재적분해서 동역학적으로 일관된 plot data를 만든다.
    """
    t_src = np.asarray(t_data).reshape(-1)
    u_src = np.asarray(u_data)
    x = np.asarray(x_data[0], dtype=float).copy()
    x[1] = max(x[1], 1.0)

    t_end = max(float(t_src[-1]), params["tf_min"])
    t_limit = min(max(params["tf_max"], t_end), 180.0)

    ts = [0.0]
    xs = [x.copy()]
    us = [u_src[0].copy()]

    def interp_u(t):
        alpha = np.interp(t, t_src, u_src[:, 0])
        throttle = np.interp(t, t_src, u_src[:, 1])
        return np.array([alpha, throttle], dtype=float)

    t = 0.0
    while t < t_limit and x[1] > 0.0:
        h_prev = x[1]
        t_prev = t
        x_prev = x.copy()
        step = min(dt, t_limit - t)
        u1 = interp_u(t)
        u2 = interp_u(t + 0.5 * step)
        u4 = interp_u(t + step)

        k1 = numeric_missile_dynamics(x, u1, params)
        k2 = numeric_missile_dynamics(x + 0.5 * step * k1, u2, params)
        k3 = numeric_missile_dynamics(x + 0.5 * step * k2, u2, params)
        k4 = numeric_missile_dynamics(x + step * k3, u4, params)
        x = x + (step / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        x[4] = max(x[4], params["dry_mass"])
        t += step

        if h_prev > 0.0 and x[1] <= 0.0:
            frac = h_prev / (h_prev - x[1] + 1e-12)
            x = x_prev + frac * (x - x_prev)
            x[1] = 0.0
            t = t_prev + frac * step

        ts.append(t)
        xs.append(x.copy())
        us.append(interp_u(t))

    return np.asarray(xs), np.asarray(us), np.asarray(ts)


def postprocess_propulsion_history(x_data, u_data, params):
    """
    최적화 결과를 NumPy로 재계산해서 Mach, q, mode history를 확인한다.
    """
    h = x_data[:, 1]
    v = x_data[:, 2]
    m = x_data[:, 4]
    throttle = u_data[:, 1]

    h_safe = np.maximum(h, 0.0)
    rho = RHO0 * np.exp(-h_safe / 7400.0)
    a_sound = np.where(h_safe < 11000.0, 340.0 - 0.004 * h_safe, 295.0)
    mach = v / a_sound
    q = 0.5 * rho * v ** 2

    solid_boundary_mass = params["dry_mass"] + params["gas_prop_mass"]
    solid_fuel_available = np_smooth_step(m - solid_boundary_mass, MASS_SMOOTH_WIDTH)
    gas_fuel_available = np_smooth_step(m - params["dry_mass"], MASS_SMOOTH_WIDTH)

    ramjet_mach_on = np_smooth_step(mach - RAMJET_MIN_MACH, MACH_SMOOTH_WIDTH)
    rocket_mach_on = 1.0 - ramjet_mach_on
    high_mach_limit = np_smooth_step(RAMJET_MAX_MACH - mach, MACH_SMOOTH_WIDTH)
    altitude_gate = np_smooth_gate_between(h, 1000.0, params["max_altitude"], ALT_SMOOTH_WIDTH)
    has_gas_fuel = min(1.0, params["gas_prop_mass"] * 1000.0)

    rocket_on = solid_fuel_available * rocket_mach_on
    ramjet_on = has_gas_fuel * gas_fuel_available * ramjet_mach_on * high_mach_limit * altitude_gate

    eta_ram = (
        0.55
        + 0.30 * np.exp(-((mach - 3.2) / 1.1) ** 2)
    )
    ratio_eff = np.clip(1.0 - 0.8 * (params["gas_ratio"] - 0.40) ** 2, 0.65, 1.0)
    fuel_eff = np.clip(np.sqrt(params["lhv"] / FUEL_LHV["kerosene"]), 0.80, 1.25)
    eta_ram = eta_ram * ratio_eff * fuel_eff

    density_ratio = np.maximum(0.05, rho / RHO0)
    thrust_solid = rocket_on * params["solid_thrust"]
    thrust_ramjet = (
        ramjet_on
        * throttle
        * params["ramjet_ref_thrust"]
        * eta_ram
        * density_ratio ** 0.20
    )

    return {
        "rho": rho,
        "a_sound": a_sound,
        "mach": mach,
        "q": q,
        "rocket_on": rocket_on,
        "ramjet_on": ramjet_on,
        "thrust_solid": thrust_solid,
        "thrust_ramjet": thrust_ramjet,
    }


def print_solution_diagnostics(x_data, u_data, t_data, params):
    """
    Spectral/collocation wiggle 여부와 모드 전환을 간단히 진단한다.
    """
    history = postprocess_propulsion_history(x_data, u_data, params)
    R = x_data[:, 0]
    h = x_data[:, 1]
    gamma = x_data[:, 3]
    alpha = u_data[:, 0]

    curvature = np.diff(h / 1000.0, n=2)
    max_curvature = np.max(np.abs(curvature)) if len(curvature) else 0.0
    gamma_step = np.diff(np.degrees(gamma))
    alpha_step = np.diff(np.degrees(alpha))
    alpha_sign_changes = np.count_nonzero(np.diff(np.signbit(alpha)))

    ramjet_active = history["ramjet_on"] > 0.5
    rocket_active = history["rocket_on"] > 0.5
    terminal_guard_idx = max(1, int(0.85 * len(h)))
    midcourse_h = h[:terminal_guard_idx]
    midcourse_ground_touch = len(midcourse_h) > 0 and np.min(midcourse_h) < 50.0
    max_mach = np.max(history["mach"])
    ramjet_never_reached = max_mach < RAMJET_MIN_MACH or not np.any(ramjet_active)
    suspicious_reclimb = False
    if len(h) > 8:
        min_idx = int(np.argmin(h[:terminal_guard_idx]))
        suspicious_reclimb = h[min_idx] < 100.0 and np.max(h[min_idx:-3]) > 500.0

    print("\n========== Numerical / Mode Diagnostics ==========")
    print(f"Max dynamic pressure     : {np.max(history['q']) / 1000.0:.3f} kPa")
    print(f"Dynamic pressure limit   : {params['max_q'] / 1000.0:.3f} kPa")
    print(f"Max Mach                 : {max_mach:.3f}")
    print(f"Rocket mode samples      : {np.count_nonzero(rocket_active)} / {len(R)}")
    print(f"Ramjet mode samples      : {np.count_nonzero(ramjet_active)} / {len(R)}")
    if np.any(ramjet_active):
        first_idx = np.argmax(ramjet_active)
        print(f"Ramjet starts near       : t={np.asarray(t_data[first_idx]).item():.3f} s, M={history['mach'][first_idx]:.3f}")
    print(f"Max |second diff h|      : {max_curvature:.6f} km/node^2")
    print(f"Max |delta gamma|        : {np.max(np.abs(gamma_step)) if len(gamma_step) else 0.0:.3f} deg/node")
    print(f"Max |delta alpha|        : {np.max(np.abs(alpha_step)) if len(alpha_step) else 0.0:.3f} deg/node")
    print(f"Alpha sign changes       : {alpha_sign_changes}")
    if midcourse_ground_touch:
        print("[Warning] Midcourse ground contact detected before terminal impact.")
    if suspicious_reclimb:
        print("[Warning] Trajectory appears to touch near-ground and climb again; treat as nonphysical.")
    if np.max(history["q"]) > 1.01 * params["max_q"]:
        print("[Warning] Dynamic pressure limit exceeded. Tighten q constraint or revise handoff guess.")
    if ramjet_never_reached:
        print("[Warning] Ramjet mode not reached. Do not interpret this as ramjet performance.")
    if max_curvature > 0.8:
        print("[Warning] Large altitude curvature detected; possible collocation wiggle.")
    print("=================================================\n")

    return history


def show_or_close():
    """
    GUI backend이면 표시하고, Agg/headless backend이면 파일 저장 후 닫는다.
    """
    import matplotlib.pyplot as plt

    if "agg" in plt.get_backend().lower():
        plt.close()
    else:
        plt.show()


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

    n_segments = 30
    poly_orders = [2] * n_segments

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
    x_data, u_data, t_data = sort_solution_by_time(x_data, u_data, t_data)
    if REPLAY_DYNAMICS_FOR_PLOTS:
        x_data, u_data, t_data = replay_solution_dynamics(x_data, u_data, t_data, params)

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

    history = print_solution_diagnostics(x_data, u_data, t_data, params)

    return params, solution, post, x_data, u_data, t_data, history


def plot_trajectory_results(x_data, u_data, t_data, params, history=None, save_path=None):
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
    if history is None:
        history = postprocess_propulsion_history(x_data, u_data, params)

    # Plot 1: 3D Trajectory (Range vs Altitude)
    plt.figure(figsize=(12, 5))
    plt.plot(R / 1000, h / 1000, "o-", linewidth=2, markersize=4)
    plt.xlabel("Downrange [km]", fontsize=11)
    plt.ylabel("Altitude [km]", fontsize=11)
    title_suffix = " (Dynamics Replay)" if REPLAY_DYNAMICS_FOR_PLOTS else ""
    plt.title(f"Missile Trajectory After Boost Handoff{title_suffix}", fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(f"{save_path}_01_trajectory.png", dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}_01_trajectory.png")
    show_or_close()

    # Plot 2: Velocity History
    plt.figure(figsize=(12, 5))
    plt.plot(t_data, V, "o-", linewidth=2, markersize=4, color='tab:orange')
    plt.xlabel("Time [s]", fontsize=11)
    plt.ylabel("Velocity [m/s]", fontsize=11)
    plt.title("Velocity History After Boost Handoff", fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(f"{save_path}_02_velocity.png", dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}_02_velocity.png")
    show_or_close()

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
    show_or_close()

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
    show_or_close()

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
    show_or_close()

    # Plot 6: Mach, dynamic pressure, and propulsion modes
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    axes[0].plot(t_data, history["mach"], "o-", linewidth=2, markersize=4, color='tab:purple')
    axes[0].axhline(RAMJET_MIN_MACH, color='k', linestyle='--', linewidth=1, alpha=0.6, label="Ramjet mode threshold")
    axes[0].set_ylabel("Mach", fontsize=11)
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t_data, history["q"] / 1000.0, "o-", linewidth=2, markersize=4, color='tab:brown')
    axes[1].axhline(params["max_q"] / 1000.0, color='k', linestyle='--', linewidth=1, alpha=0.6, label="q limit")
    axes[1].set_ylabel("q [kPa]", fontsize=11)
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t_data, history["rocket_on"], "o-", linewidth=2, markersize=4, label="Rocket mode")
    axes[2].plot(t_data, history["ramjet_on"], "s-", linewidth=2, markersize=4, label="Ramjet mode")
    axes[2].set_xlabel("Time [s]", fontsize=11)
    axes[2].set_ylabel("Mode gate", fontsize=11)
    axes[2].set_ylim(-0.05, 1.05)
    axes[2].legend(fontsize=9)
    axes[2].grid(True, alpha=0.3)
    fig.suptitle("Mach / Dynamic Pressure / Propulsion Mode", fontsize=12, fontweight='bold')
    fig.tight_layout()
    if save_path:
        plt.savefig(f"{save_path}_06_modes.png", dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}_06_modes.png")
    show_or_close()

    return None


# ============================================================
# 8. 실행
# ============================================================
if __name__ == "__main__":
    import datetime
    
    # 여러 연료 타입 비교가 필요하면 RUN_ALL_FUELS = True
    fuel_types = ["hydrogen", "methane", "ethylene", "kerosene"] if RUN_ALL_FUELS else [FUEL_TYPE]
    
    for model_name in MODEL_NAMES:
        for fuel in fuel_types:
            print(f"\n{'='*60}")
            print(f"Testing Model: {model_name} | Fuel: {fuel.upper()}")
            print(f"{'='*60}")

            params, solution, post, x_data, u_data, t_data, history = solve_one_model(
                model_name,
                GAS_RATIO,
                fuel,
                plot=PLOT_RESULT
            )

            # 커스텀 플롯 표시 및 저장 (PLOT_RESULT가 True일 때)
            if PLOT_RESULT:
                save_dir = f"{model_name}_Modechange_Plot"
                import os
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(save_dir, f"trajectory_{model_name}_{fuel}_{GAS_RATIO:.2f}_{timestamp}")

                plot_trajectory_results(x_data, u_data, t_data, params, history=history, save_path=save_path)
    
    show_or_close()
