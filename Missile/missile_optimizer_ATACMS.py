import os
from pathlib import Path
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
MODEL_NAME = "ATACMS"
GAS_RATIO  = 0.30
FUEL_TYPE  = "gas_generator"  # "gas_generator" / "hydrogen" / "methane" / "ethylene" / "kerosene"
OBJECTIVE  = "range"          # "range" / "range_terminal_velocity"
RUN_GAS_RATIO_SWEEP = True
OUTPUT_DIR = "Final_Plot"

# ============================================================
# 1. 상수
# ============================================================
G0 = 9.80665
R_EARTH = 6371000.0
R_AIR = 287.05
GAMMA_AIR = 1.4

W_MACH = 0.20
W_MASS = 5.0
W_GEN  = 1e-3

# ============================================================
# 2. 미사일 DB (공개 제원 + 연구용 가정)
#    교수님 피드백 반영:
#    * ramjet_ref_thrust / 상수 isp_ramjet surrogate 제거.
#    * 램제트 추력은 흡입 공기유량 rho*V*A_inlet 기반으로 계산.
#    * A_inlet은 frontal area의 약 25%를 기본값으로 둔다.
# ============================================================
MISSILE_DB = {
    "ATACMS": {
        "name": "ATACMS-class SRBM (ramjet-sustained concept)",
        "length": 3.98,
        "diameter": 0.61,
        "launch_mass": 1673.0,
        "public_range": 300e3,
        "dry_fraction": 0.40,
        "isp_solid": 245.0,
        "solid_burn_time": 28.0,
        "launch_angle_deg": 70.0,
        "handoff_gamma_deg": 25.0,
        "max_altitude": 30000.0,
        "max_velocity": 1800.0,
        "max_q": 300000.0,
        "tf_min": 30.0,
        "tf_max": 220.0,
    },
    "LORA": {
        "name": "LORA-class SRBM (ramjet-sustained concept)",
        "length": 5.20,
        "diameter": 0.624,
        "launch_mass": 1600.0,
        "public_range": 280e3,
        "dry_fraction": 0.40,
        "isp_solid": 245.0,
        "solid_burn_time": 32.0,
        "launch_angle_deg": 70.0,
        "handoff_gamma_deg": 25.0,
        "max_altitude": 30000.0,
        "max_velocity": 1800.0,
        "max_q": 300000.0,
        "tf_min": 30.0,
        "tf_max": 220.0,
    },
    "HYUNMOO_2B": {
        "name": "Hyunmoo-2B-class SRBM (ramjet-sustained concept)",
        "length": 12.0,
        "diameter": 0.90,
        "launch_mass": 5400.0,
        "public_range": 500e3,
        "dry_fraction": 0.42,
        "isp_solid": 250.0,
        "solid_burn_time": 45.0,
        "launch_angle_deg": 70.0,
        "handoff_gamma_deg": 25.0,
        "max_altitude": 40000.0,
        "max_velocity": 2200.0,
        "max_q": 300000.0,
        "tf_min": 60.0,
        "tf_max": 320.0,
    },
    "TOCHKA": {
        "name": "OTR-21 Tochka-class SRBM (ramjet-sustained concept)",
        "length": 6.40,
        "diameter": 0.655,
        "launch_mass": 2000.0,
        "public_range": 120e3,
        "dry_fraction": 0.42,
        "isp_solid": 235.0,
        "solid_burn_time": 25.0,
        "launch_angle_deg": 70.0,
        "handoff_gamma_deg": 25.0,
        "max_altitude": 25000.0,
        "max_velocity": 1700.0,
        "max_q": 240000.0,
        "tf_min": 30.0,
        "tf_max": 180.0,
    },
}

# 이상 램제트 연료 모델 입력값
# LHV [J/kg], f=fuel/air 질량비, cp [J/kg/K], gam=연소가스 비열비,
# Mmix [g/mol], eta=연소효율
FUELS = {
    "hydrogen":      {"LHV": 120e6, "f": 0.0292, "cp": 1400.0, "gam": 1.25, "Mmix": 28.0, "eta": 0.92},
    "methane":       {"LHV": 50e6,  "f": 0.058,  "cp": 1450.0, "gam": 1.24, "Mmix": 29.0, "eta": 0.90},
    "ethylene":     {"LHV": 47e6,  "f": 0.064,  "cp": 1450.0, "gam": 1.24, "Mmix": 29.0, "eta": 0.90},
    "kerosene":     {"LHV": 43e6,  "f": 0.068,  "cp": 1450.0, "gam": 1.24, "Mmix": 29.0, "eta": 0.90},
    "gas_generator": {"LHV": 30e6,  "f": 0.10,   "cp": 1500.0, "gam": 1.22, "Mmix": 29.0, "eta": 0.85},
}

RAMJET_MACH_MIN = 1.6
RAMJET_MACH_MAX = 5.0
RAMJET_T3_CAP = 2500.0
INLET_PR_RECOVERY = 0.85
INLET_AREA_FRACTION = 0.25
Q_CONSTRAINT_MARGIN = 0.65  # replay/interpolation margin for dynamic pressure

# ============================================================
# 3. 매끄러운 유틸 (CasADi / NumPy)
# ============================================================
def s_step(z, w): return 0.5 * (1.0 + ca.tanh(z / w))
def s_pos(z, w): return 0.5 * (z + ca.sqrt(z ** 2 + w ** 2))
def s_min(v, hi, w): return hi - s_pos(hi - v, w)
def s_max(v, lo, w): return lo + s_pos(v - lo, w)

def n_step(z, w): return 0.5 * (1.0 + np.tanh(np.asarray(z) / w))

# ============================================================
# 4. 대기 모델 (ISA)
# ============================================================
def atm_ca(h):
    h = s_max(h, 0.0, 1.0)
    T_tropo = 288.15 - 0.0065 * h
    P_tropo = 101325.0 * (T_tropo / 288.15) ** 5.2559
    T_strat = 216.65
    P_strat = 22632.0 * ca.exp(-(h - 11000.0) / 6341.6)
    T = ca.if_else(h < 11000.0, T_tropo, T_strat)
    P = ca.if_else(h < 11000.0, P_tropo, P_strat)
    rho = P / (R_AIR * T)
    a = ca.sqrt(GAMMA_AIR * R_AIR * T)
    return rho, a, T, P

def atm_np(h):
    h = max(float(h), 0.0)
    if h < 11000.0:
        T = 288.15 - 0.0065 * h
        P = 101325.0 * (T / 288.15) ** 5.2559
    else:
        T = 216.65
        P = 22632.0 * np.exp(-(h - 11000.0) / 6341.6)
    rho = P / (R_AIR * T)
    a = np.sqrt(GAMMA_AIR * R_AIR * T)
    return rho, a, T, P

def gravity(h):
    return G0 * (R_EARTH / (R_EARTH + s_max(h, 0.0, 1.0))) ** 2

# ============================================================
# 5. 항력계수 Cd(M)
# ============================================================
def cd_of_mach_ca(mach):
    cd_sup = s_max(0.31 - 0.033 * mach, 0.18, 1e-3)
    cd_tr = 0.30 * ca.exp(-((mach - 1.05) / 0.25) ** 2)
    return cd_sup + cd_tr

def cd_of_mach_np(mach):
    cd_sup = np.maximum(0.31 - 0.033 * mach, 0.18)
    cd_tr = 0.30 * np.exp(-((mach - 1.05) / 0.25) ** 2)
    return cd_sup + cd_tr

# ============================================================
# 6. 이상 램제트 성능
#    T = rho * V * A_inlet * sp_thrust
# ============================================================
def ramjet_perf_ca(mach, h, fuel):
    _, a, T1, P1 = atm_ca(h)
    V = mach * a
    T2 = T1 * (1.0 + 0.2 * mach ** 2)
    P2 = P1 * (T2 / T1) ** 3.5 * INLET_PR_RECOVERY
    f, LHV, cp = fuel["f"], fuel["LHV"], fuel["cp"]
    gam, Mmix, eta = fuel["gam"], fuel["Mmix"], fuel["eta"]
    T3 = T2 + eta * f * LHV / ((1.0 + f) * cp)
    T3 = s_min(T3, RAMJET_T3_CAP, 10.0)
    Rg = 8314.0 / Mmix
    pr = P1 / P2
    arg = 1.0 - pr ** ((gam - 1.0) / gam)
    Ve = ca.sqrt(2.0 * gam / (gam - 1.0) * Rg * T3 * s_max(arg, 1e-4, 1e-4))
    sp_thrust = s_pos((1.0 + f) * Ve - V, 1.0)
    Isp = sp_thrust / (f * G0)
    return sp_thrust, Isp, V

def ramjet_perf_np(mach, h, fuel):
    _, a, T1, P1 = atm_np(h)
    V = mach * a
    T2 = T1 * (1.0 + 0.2 * mach ** 2)
    P2 = P1 * (T2 / T1) ** 3.5 * INLET_PR_RECOVERY
    f, LHV, cp = fuel["f"], fuel["LHV"], fuel["cp"]
    gam, Mmix, eta = fuel["gam"], fuel["Mmix"], fuel["eta"]
    T3 = min(T2 + eta * f * LHV / ((1.0 + f) * cp), RAMJET_T3_CAP)
    Rg = 8314.0 / Mmix
    pr = P1 / P2
    arg = max(1.0 - pr ** ((gam - 1.0) / gam), 1e-4)
    Ve = np.sqrt(2.0 * gam / (gam - 1.0) * Rg * T3 * arg)
    sp_thrust = max((1.0 + f) * Ve - V, 0.0)
    Isp = sp_thrust / (f * G0) if sp_thrust > 0 else 0.0
    return sp_thrust, Isp, V

# ============================================================
# 7. 파라미터 구성
# ============================================================
def build_params(model_name, gas_ratio, fuel_type):
    base = MISSILE_DB[model_name].copy()
    if fuel_type not in FUELS:
        raise ValueError(f"unknown fuel: {fuel_type}")
    fuel = FUELS[fuel_type]

    m0 = base["launch_mass"]
    dry = m0 * base["dry_fraction"]
    prop = m0 - dry
    gas_ratio = float(np.clip(gas_ratio, 0.0, 0.8))
    solid_prop = prop * (1.0 - gas_ratio)
    gas_prop = prop * gas_ratio

    area = np.pi * (base["diameter"] / 2.0) ** 2
    inlet_area = base.get("inlet_area", INLET_AREA_FRACTION * area)

    # boost_thrust_ref는 gas_ratio=0일 때의 고체모터 평균추력을 기준으로 고정한다.
    # 따라서 gas_ratio가 커질수록 고체 추진제량과 부스트 연소시간이 함께 줄어든다.
    boost_thrust_ref = prop * G0 * base["isp_solid"] / base["solid_burn_time"]
    solid_thrust = boost_thrust_ref if solid_prop > 1.0 else 0.0

    base.update({
        "model_name": model_name, "fuel_type": fuel_type, "fuel": fuel,
        "m0": m0, "dry_mass": dry, "prop_mass": prop,
        "solid_prop": solid_prop, "gas_prop": gas_prop,
        "gas_ratio": gas_ratio, "solid_ratio": 1.0 - gas_ratio,
        "area": area, "inlet_area": inlet_area,
        "boost_thrust_ref": boost_thrust_ref, "solid_thrust": solid_thrust,
    })
    return base

# ============================================================
# 8. 부스트 -> handoff 상태 (prescribed gamma(t), 점질량 병진 적분)
# ============================================================
def compute_boost_handoff(params):
    m0 = params["m0"]
    m_burnout = params["dry_mass"] + params["gas_prop"]
    solid_prop = params["solid_prop"]
    isp = params["isp_solid"]

    if solid_prop < 1.0:
        _, a, _, _ = atm_np(500.0)
        return np.array([0.0, 500.0, 1.6 * a, m0])

    F = params["boost_thrust_ref"]
    tb = solid_prop * G0 * isp / F
    mdot = solid_prop / tb
    g_launch = np.radians(params["launch_angle_deg"])
    g_hand = np.radians(params["handoff_gamma_deg"])

    x = np.array([0.0, 5.0, 30.0, g_launch, m0])
    dt, t = 0.01, 0.0
    while t < tb:
        R, h, v, _, m = x
        gam = g_launch + (g_hand - g_launch) * (t / tb)
        rho, a, _, _ = atm_np(h)
        mach = v / a
        q = 0.5 * rho * v ** 2
        D = q * params["area"] * cd_of_mach_np(mach)
        g = G0 * (R_EARTH / (R_EARTH + max(h, 0.0))) ** 2
        dv = (F - D) / m - g * np.sin(gam)
        x = x + dt * np.array([v * np.cos(gam), v * np.sin(gam), dv, 0.0, -mdot])
        x[3] = gam
        t += dt

    h_out = min(max(x[1], 300.0), 0.6 * params["max_altitude"])
    rho_out, _, _, _ = atm_np(h_out)
    v_q_limit = np.sqrt(2.0 * Q_CONSTRAINT_MARGIN * params["max_q"] / max(rho_out, 1e-6))
    v_out = min(max(x[2], 50.0), 0.97 * params["max_velocity"], v_q_limit)
    return np.array([0.0, h_out, v_out, m_burnout])

# ============================================================
# 9. 추진/동역학 (CasADi)
# ============================================================
def ramjet_thrust_ca(x, throttle, params):
    h, v, m = x[1], x[2], x[3]
    rho, a, _, _ = atm_ca(h)
    mach = v / a
    sp, Isp, _ = ramjet_perf_ca(mach, h, params["fuel"])
    gate_lo = s_step(mach - RAMJET_MACH_MIN, W_MACH)
    gate_hi = s_step(RAMJET_MACH_MAX - mach, W_MACH)
    gate_fuel = s_step(m - params["dry_mass"], W_MASS)
    gate_alt = s_step(h - 300.0, 200.0)
    gate = gate_lo * gate_hi * gate_fuel * gate_alt
    T = gate * throttle * rho * v * params["inlet_area"] * sp
    mdot = T / (G0 * s_max(Isp, 50.0, 10.0))
    return T, mdot, mach

def dynamics_ca(x, u, params):
    R, h, v, m = x[0], x[1], x[2], x[3]
    gam, throttle = u[0], u[1]
    rho, a, _, _ = atm_ca(h)
    g = gravity(h)
    q = 0.5 * rho * v ** 2
    mach = v / a
    D = q * params["area"] * cd_of_mach_ca(mach)
    T, mdot, _ = ramjet_thrust_ca(x, throttle, params)
    return [
        v * ca.cos(gam),
        v * ca.sin(gam),
        (T - D) / m - g * ca.sin(gam),
        -mdot,
    ]

# ============================================================
# 10. 추진/동역학 (NumPy replay)
# ============================================================
def thrust_np(h, v, m, throttle, params):
    rho, a, _, _ = atm_np(h)
    mach = v / a
    sp, Isp, _ = ramjet_perf_np(mach, h, params["fuel"])
    gate = (n_step(mach - RAMJET_MACH_MIN, W_MACH) * n_step(RAMJET_MACH_MAX - mach, W_MACH)
            * n_step(m - params["dry_mass"], W_MASS) * n_step(h - 300.0, 200.0))
    T = float(gate) * throttle * rho * v * params["inlet_area"] * sp
    mdot = T / (G0 * max(Isp, 50.0))
    return T, mdot, mach

def dynamics_np(x, u, params):
    R, h, v, m = x
    v = max(v, 1.0)
    m = max(m, params["dry_mass"])
    gam, throttle = float(u[0]), float(np.clip(u[1], 0.0, 1.0))
    rho, a, _, _ = atm_np(h)
    g = G0 * (R_EARTH / (R_EARTH + max(h, 0.0))) ** 2
    q = 0.5 * rho * v ** 2
    mach = v / a
    D = q * params["area"] * cd_of_mach_np(mach)
    T, mdot, _ = thrust_np(h, v, m, throttle, params)
    return np.array([v * np.cos(gam), v * np.sin(gam), (T - D) / m - g * np.sin(gam), -mdot])

# ============================================================
# 11. OCP 구성 (단일 phase, 순수 램제트 sustain)
# ============================================================
def create_ocp(params, x0):
    ocp = mp.OCP(n_states=4, n_controls=2, n_phases=1)  # x=[R,h,v,m], u=[gamma,throttle]

    def term_cost(xf, tf, x00, t0):
        base = -xf[0] / 1000.0 + 2e-3 * tf
        if OBJECTIVE == "range_terminal_velocity":
            base += -0.05 * xf[2]
        return base

    def run_cost(x, u, t):
        return 1e-3 * u[1] ** 2 + 5e-4 * u[0] ** 2

    ocp.terminal_costs[0] = term_cost
    ocp.running_costs[0] = run_cost
    ocp.dynamics[0] = lambda x, u, t: dynamics_ca(x, u, params)
    ocp.terminal_constraints[0] = lambda xf, tf, x00, t0: [xf[1]]
    q_design_limit = Q_CONSTRAINT_MARGIN * params["max_q"]
    ocp.path_constraints[0] = lambda x, u, t: [0.5 * atm_ca(x[1])[0] * x[2] ** 2 - q_design_limit]

    ocp.x00[0] = list(map(float, x0))
    ocp.u00[0] = [np.radians(15.0), 0.7]
    ocp.xf0[0] = [0.5 * params["public_range"], 0.0, 0.6 * x0[2], params["dry_mass"]]

    ocp.lbx[0] = [0.0, 0.0, 50.0, params["dry_mass"]]
    ocp.ubx[0] = [3.0 * params["public_range"], params["max_altitude"], params["max_velocity"], params["m0"]]
    ocp.lbu[0] = [np.radians(-80.0), 0.0]
    ocp.ubu[0] = [np.radians(70.0), 1.0]
    ocp.lbtf[0] = params["tf_min"]
    ocp.ubtf[0] = params["tf_max"]
    return ocp

# ============================================================
# 12. replay (numpy RK4)
# ============================================================
def replay(x_data, u_data, t_data, params, dt=0.2):
    t_src = np.asarray(t_data).reshape(-1)
    u_src = np.asarray(u_data)
    x = np.asarray(x_data[0], float).copy()
    x[1] = max(x[1], 1.0)
    t_lim = min(max(float(t_src[-1]), params["tf_min"]), params["tf_max"])

    def interp(t):
        return np.array([np.interp(t, t_src, u_src[:, 0]), np.interp(t, t_src, u_src[:, 1])])

    ts, xs, us = [0.0], [x.copy()], [interp(0.0)]
    t = 0.0
    while t < t_lim and x[1] > 0.0:
        step = min(dt, t_lim - t)
        xp, hp = x.copy(), x[1]
        k1 = dynamics_np(x, interp(t), params)
        k2 = dynamics_np(x + 0.5 * step * k1, interp(t + 0.5 * step), params)
        k3 = dynamics_np(x + 0.5 * step * k2, interp(t + 0.5 * step), params)
        k4 = dynamics_np(x + step * k3, interp(t + step), params)
        x = x + step / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        x[3] = max(x[3], params["dry_mass"])
        t += step
        if hp > 0 and x[1] <= 0:
            fr = hp / (hp - x[1] + 1e-12)
            x = xp + fr * (x - xp)
            x[1] = 0.0
            t = (t - step) + fr * step
        ts.append(t)
        xs.append(x.copy())
        us.append(interp(t))
    return np.asarray(xs), np.asarray(us), np.asarray(ts)

# ============================================================
# 13. solve
# ============================================================
def solve_model(model_name, gas_ratio, fuel_type, n_segments=18):
    params = build_params(model_name, gas_ratio, fuel_type)
    x0 = compute_boost_handoff(params)
    _, a0, _, _ = atm_np(x0[1])
    print(f"\n[{model_name}|{fuel_type}|gas_ratio={gas_ratio}]")
    print(f"  solid_prop={params['solid_prop']:.0f} kg  gas_prop={params['gas_prop']:.0f} kg  "
          f"boost_thrust_ref={params['boost_thrust_ref']/1e3:.1f} kN  inlet_area={params['inlet_area']:.3f} m^2")
    print(f"  boost handoff: h={x0[1]/1000:.2f} km  v={x0[2]:.0f} m/s (M{x0[2]/a0:.2f})  "
          f"m={x0[3]:.0f} kg  (gamma is a control)")

    ocp = create_ocp(params, x0)
    mpo = mp.mpopt(ocp, n_segments=n_segments, poly_orders=[3] * n_segments, scheme="LGR")
    sol = mpo.solve(ipopt_options={"tol": 1e-6, "max_iter": 2000, "acceptable_tol": 1e-5, "print_level": 0})
    post = mpo.process_results(sol, plot=False)
    xd, ud, td, _ = post.get_data()
    order = np.argsort(np.asarray(td).reshape(-1), kind="mergesort")
    xd, ud, td = xd[order], ud[order], np.asarray(td).reshape(-1)[order]
    xd, ud, td = replay(xd, ud, td, params)

    fuel_used = x0[3] - xd[-1, 3]
    mach = np.array([xd[i, 2] / atm_np(xd[i, 1])[1] for i in range(len(xd))])
    q_replay = np.array([0.5 * atm_np(xd[i, 1])[0] * xd[i, 2] ** 2 for i in range(len(xd))])
    print(f"  RESULT: range={xd[-1,0]/1000:.2f} km  max_alt={xd[:,1].max()/1000:.2f} km  "
          f"Vmax={xd[:,2].max():.0f}  Vterm={xd[-1,2]:.0f}  Mmax={mach.max():.2f}  "
          f"qmax={q_replay.max()/1000:.1f}/{params['max_q']/1000:.0f} kPa  "
          f"tf={td[-1]:.1f} s  gas_used={fuel_used:.1f}/{params['gas_prop']:.0f} kg")
    return params, xd, ud, td, mach

# ============================================================
# 14. plot save
# ============================================================
def save_plots(params, x, u, t, mach, output_dir=OUTPUT_DIR):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir = Path(__file__).resolve().parent / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    model = params["model_name"]
    prefix = output_dir / f"{model}_{params['fuel_type']}_{params['gas_ratio']:.2f}"
    q = np.array([0.5 * atm_np(x[i, 1])[0] * x[i, 2] ** 2 / 1000.0 for i in range(len(x))])
    thrust = np.array([thrust_np(x[i, 1], x[i, 2], x[i, 3], u[i, 1], params)[0] / 1000.0 for i in range(len(x))])

    plots = []
    plt.figure(figsize=(7, 4.5))
    plt.plot(x[:, 0] / 1000.0, x[:, 1] / 1000.0, linewidth=2)
    plt.xlabel("Downrange [km]")
    plt.ylabel("Altitude [km]")
    plt.title(f"{model} Trajectory")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = f"{prefix}_01_trajectory.png"
    plt.savefig(path, dpi=150)
    plt.close()
    plots.append(path)

    plt.figure(figsize=(7, 4.5))
    plt.plot(t, x[:, 2], linewidth=2)
    plt.xlabel("Time [s]")
    plt.ylabel("Velocity [m/s]")
    plt.title(f"{model} Velocity")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = f"{prefix}_02_velocity.png"
    plt.savefig(path, dpi=150)
    plt.close()
    plots.append(path)

    plt.figure(figsize=(7, 4.5))
    plt.plot(t, x[:, 3], linewidth=2)
    plt.xlabel("Time [s]")
    plt.ylabel("Mass [kg]")
    plt.title(f"{model} Mass")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = f"{prefix}_03_mass.png"
    plt.savefig(path, dpi=150)
    plt.close()
    plots.append(path)

    plt.figure(figsize=(7, 4.5))
    plt.plot(t, np.degrees(u[:, 0]), linewidth=2, label="gamma [deg]")
    plt.plot(t, u[:, 1], linewidth=2, label="throttle [-]")
    plt.xlabel("Time [s]")
    plt.title(f"{model} Controls")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = f"{prefix}_04_controls.png"
    plt.savefig(path, dpi=150)
    plt.close()
    plots.append(path)

    plt.figure(figsize=(7, 4.5))
    plt.plot(t, mach, linewidth=2, label="Mach")
    plt.plot(t, q, linewidth=2, label="q [kPa]")
    plt.plot(t, thrust, linewidth=2, label="ramjet thrust [kN]")
    plt.axhline(params["max_q"] / 1000.0, color="k", linestyle="--", linewidth=1, label="q limit")
    plt.xlabel("Time [s]")
    plt.title(f"{model} Mach / q / Thrust")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = f"{prefix}_05_mach_q_thrust.png"
    plt.savefig(path, dpi=150)
    plt.close()
    plots.append(path)

    print(f"  Saved plots: {output_dir}")
    return plots

# ============================================================
# 15. main
# ============================================================
if __name__ == "__main__":
    params, xd, ud, td, mach = solve_model(MODEL_NAME, GAS_RATIO, FUEL_TYPE)
    save_plots(params, xd, ud, td, mach)

    if RUN_GAS_RATIO_SWEEP:
        print("\n==== gas_ratio sweep (%s, %s) ====" % (MODEL_NAME, FUEL_TYPE))
        for gr in [0.0, 0.1, 0.2, 0.3, 0.4]:
            try:
                solve_model(MODEL_NAME, gr, FUEL_TYPE)
            except Exception as e:
                print(f"  gas_ratio={gr}: solve failed ({e})")
