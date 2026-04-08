import gradio as gr
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════
#  COLOR SYSTEM
# ═══════════════════════════════════════════════════════════════════
C = {
    "bg":      "#06091a",
    "panel":   "#0b1120",
    "panel2":  "#0f172a",
    "border":  "#1e3a5f",
    "cyan":    "#00e5ff",
    "green":   "#00ff9d",
    "amber":   "#ffb300",
    "red":     "#ff3d5a",
    "purple":  "#c084fc",
    "blue":    "#60a5fa",
    "muted":   "#334d6e",
    "text":    "#e2eeff",
    "dim":     "#5a7a9a",
}

# ═══════════════════════════════════════════════════════════════════
#  CHART HELPERS
# ═══════════════════════════════════════════════════════════════════
def style_ax(ax, fig, title=""):
    fig.patch.set_facecolor(C["panel"])
    ax.set_facecolor(C["panel"])
    ax.tick_params(colors=C["dim"], labelsize=9)
    ax.xaxis.label.set_color(C["dim"])
    ax.yaxis.label.set_color(C["dim"])
    for sp in ax.spines.values():
        sp.set_edgecolor(C["border"])
    ax.grid(True, color=C["border"], lw=0.5, linestyle="--", alpha=0.5)
    if title:
        ax.set_title(title, color=C["text"], fontsize=11, fontweight="bold", pad=10)

def _leg(ax):
    ax.legend(fontsize=8, facecolor=C["panel2"], labelcolor=C["text"],
              edgecolor=C["border"], loc="upper right", framealpha=0.9)

# ═══════════════════════════════════════════════════════════════════
#  CHARTS
# ═══════════════════════════════════════════════════════════════════
def make_gauge_chart(value, label, color, seed):
    fig, ax = plt.subplots(figsize=(3.8, 3.8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(C["panel"])
    ax.set_facecolor(C["panel"])
    pct   = max(0, min(value, 100)) / 100
    theta = np.linspace(np.pi * 1.25, np.pi * 1.25 - 2.5 * np.pi * pct, 300)
    r_in, r_out = 0.60, 0.90
    t_bg = np.linspace(np.pi * 1.25, np.pi * 1.25 - 2.5 * np.pi, 300)
    ax.fill_between(t_bg, r_in, r_out, color=C["muted"], alpha=0.25, zorder=1)
    ax.fill_between(theta, r_in, r_out, color=color, alpha=0.92, zorder=2)
    if len(theta) > 0:
        ax.scatter([theta[-1]], [(r_in + r_out) / 2], s=80, color="white", zorder=5, alpha=0.9)
    np.random.seed(seed % 40)
    for t in t_bg[::30]:
        ax.plot([t, t], [r_out + 0.02, r_out + 0.07], color=C["dim"], lw=1.0, alpha=0.6)
    ax.text(0, 0, f"{int(value)}%", ha="center", va="center",
            fontsize=22, fontweight="bold", color=color, transform=ax.transData)
    ax.text(0, -0.28, label, ha="center", va="center",
            fontsize=10, color=C["dim"], transform=ax.transData)
    ax.set_ylim(0, 1)
    ax.axis("off")
    plt.tight_layout(pad=0.3)
    return fig

def make_radial_burst(value, label, color, seed):
    np.random.seed(seed % 40 + 5)
    n   = 180
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r   = 0.3 + 0.6 * np.abs(np.random.normal(0, max(value, 1) / 120, n))
    r   = np.clip(r, 0, 1)
    fig, ax = plt.subplots(figsize=(3.8, 3.8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(C["panel"])
    ax.set_facecolor(C["panel"])
    for i in range(n):
        ax.plot([ang[i], ang[i]], [0, r[i]], color=color, lw=1.0, alpha=0.3 + 0.7 * r[i])
    ax.scatter(ang, r, s=4, color=color, alpha=0.7, zorder=3)
    theta_fill = np.linspace(0, 2 * np.pi, 300)
    ax.fill(theta_fill, [0.28] * 300, color=C["panel2"], zorder=2)
    ax.fill(theta_fill, [0.27] * 300, color=color, alpha=0.15, zorder=2)
    ax.text(0, 0, str(value), ha="center", va="center",
            fontsize=18, fontweight="bold", color=color, transform=ax.transData)
    ax.text(0, -0.5, label, ha="center", va="center",
            fontsize=9, color=C["dim"], transform=ax.transData)
    ax.set_ylim(0, 1.1)
    ax.axis("off")
    plt.tight_layout(pad=0.3)
    return fig

def make_area_chart(user_load, seed):
    np.random.seed(seed % 60)
    t    = np.arange(80)
    base = user_load * 8
    y    = base + 160 * np.sin(t / 10) + np.random.normal(0, 25, 80)
    y    = np.clip(y, 0, 1000)
    spk  = np.where(y > np.percentile(y, 88))[0]
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    style_ax(ax, fig, "Traffic Load — Area View")
    ax.fill_between(t, y, alpha=0.35, color=C["cyan"])
    ax.plot(t, y, color=C["cyan"], lw=1.8)
    ax.scatter(spk, y[spk], color=C["red"], s=28, zorder=5, label="Load spike")
    ax.set_xlabel("Time steps", fontsize=9)
    ax.set_ylabel("req/s", fontsize=9)
    _leg(ax)
    plt.tight_layout(pad=1.0)
    return fig

def make_neon_bar(auto_scaling, seed):
    np.random.seed(seed % 60 + 1)
    cats = ["t0","t1","t2","t3","t4","t5","t6","t7","t8","t9","t10","t11"]
    vals = np.random.uniform(30, 100, 12)
    if auto_scaling:
        colors = [C["green"] if v > 70 else C["amber"] if v > 45 else C["red"] for v in vals]
    else:
        colors = [C["red"] if v > 60 else C["muted"] for v in vals]
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    style_ax(ax, fig, "Server Utilisation — Neon Bars")
    bars = ax.bar(cats, vals, color=colors, width=0.65, edgecolor=C["bg"], linewidth=0.4)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, v + 1.5, f"{int(v)}",
                ha="center", color=C["dim"], fontsize=7)
    ax.set_ylabel("Utilisation %", fontsize=9)
    ax.set_ylim(0, 115)
    p1 = mpatches.Patch(color=C["green"], label="Optimal")
    p2 = mpatches.Patch(color=C["amber"], label="Warning")
    p3 = mpatches.Patch(color=C["red"],   label="Critical")
    ax.legend(handles=[p1,p2,p3], fontsize=8, facecolor=C["panel2"],
              labelcolor=C["text"], edgecolor=C["border"])
    plt.tight_layout(pad=1.0)
    return fig

def make_waveform_cost(budget_on, spot_avail, seed):
    np.random.seed(seed % 60 + 2)
    t    = np.arange(120)
    burn = 0.80 * np.exp(-t/40) + 0.08
    burn += 0.04 * np.sin(t/6) + np.random.normal(0, 0.015, 120)
    if budget_on:
        burn = np.clip(burn, None, 0.55)
    if spot_avail > 50:
        burn *= 0.72
    cap = 0.50
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    style_ax(ax, fig, "Cost Burn — Waveform")
    ax.plot(t, burn, color=C["purple"], lw=1.8)
    ax.fill_between(t, burn, alpha=0.20, color=C["purple"])
    ax.axhline(cap, color=C["amber"], lw=1.2, ls="--", label=f"Budget ${cap}/hr")
    ax.fill_between(t, burn, cap, where=(burn > cap), color=C["red"], alpha=0.22, label="Over budget")
    ax.set_xlabel("Time steps", fontsize=9)
    ax.set_ylabel("$/hr", fontsize=9)
    _leg(ax)
    plt.tight_layout(pad=1.0)
    return fig

def make_latency_wave(chaos_monkey, seed):
    np.random.seed(seed % 60 + 3)
    t   = np.arange(120)
    lat = 35 + 20*np.sin(t/12) + np.random.normal(0, 5, 120)
    spk = []
    if chaos_monkey:
        spk = np.random.choice(120, size=8, replace=False)
        lat[spk] += np.random.uniform(80, 170, 8)
    lat = np.clip(lat, 0, 240)
    sla = 100
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    style_ax(ax, fig, "Latency Waveform (99th pct SLA)")
    ax.plot(t, lat, color=C["blue"], lw=1.8)
    ax.fill_between(t, lat, alpha=0.18, color=C["blue"])
    ax.axhline(sla, color=C["red"], lw=1.0, ls=":", label=f"SLA {sla} ms")
    ax.fill_between(t, lat, sla, where=(lat > sla), color=C["red"], alpha=0.22, label="SLA breach")
    if len(spk):
        ax.scatter(spk, lat[spk], color=C["red"], s=35, marker="x", lw=2, zorder=5, label="Chaos spike")
    ax.set_xlabel("Time steps", fontsize=9)
    ax.set_ylabel("Latency (ms)", fontsize=9)
    _leg(ax)
    plt.tight_layout(pad=1.0)
    return fig

def make_reward_curve(auto_scaling, seed):
    np.random.seed(seed % 60 + 4)
    eps = np.arange(1, 201)
    if auto_scaling:
        r = 950*(1 - np.exp(-eps/55)) + np.random.normal(0, 18, 200)
    else:
        r = 380*(1 - np.exp(-eps/90)) + np.random.normal(0, 12, 200)
    rc  = np.cumsum(np.clip(r/180, 0, None))
    col = C["green"] if auto_scaling else C["muted"]
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    style_ax(ax, fig, "Cumulative RL Reward")
    ax.plot(eps, rc, color=col, lw=2.0)
    ax.fill_between(eps, rc, alpha=0.15, color=col)
    lbl = "RL Agent (ON)" if auto_scaling else "Static (no RL)"
    ax.legend([lbl], fontsize=8, facecolor=C["panel2"], labelcolor=C["text"], edgecolor=C["border"])
    ax.set_xlabel("Episodes", fontsize=9)
    ax.set_ylabel("Cumulative reward", fontsize=9)
    plt.tight_layout(pad=1.0)
    return fig

def make_before_after(auto_scaling):
    cats   = ["Static\n(Before RL)", "RL Agent\n(After)"]
    spend  = [1250, 680 if auto_scaling else 1050]
    dtime  = [35,   8   if auto_scaling else 22]
    colors = [C["muted"], C["green"] if auto_scaling else C["amber"]]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.8, 3.0))
    for ax in (ax1, ax2):
        style_ax(ax, fig)
    b1 = ax1.bar(cats, spend, color=colors, width=0.5, edgecolor=C["bg"], linewidth=0.5)
    ax1.set_title("Total Spend ($)", color=C["text"], fontsize=10, fontweight="bold")
    ax1.set_ylabel("USD", fontsize=9)
    for bar, v in zip(b1, spend):
        ax1.text(bar.get_x()+bar.get_width()/2, v+18, f"${v}",
                 ha="center", color=C["text"], fontsize=9, fontweight="bold")
    b2 = ax2.bar(cats, dtime, color=colors, width=0.5, edgecolor=C["bg"], linewidth=0.5)
    ax2.set_title("Downtime Risk (%)", color=C["text"], fontsize=10, fontweight="bold")
    ax2.set_ylabel("Risk %", fontsize=9)
    for bar, v in zip(b2, dtime):
        ax2.text(bar.get_x()+bar.get_width()/2, v+0.4, f"{v}%",
                 ha="center", color=C["text"], fontsize=9, fontweight="bold")
    saved = round((1 - spend[1]/1250)*100)
    fig.suptitle(f"RL saved {saved}% cost  |  Risk reduced by {dtime[0]-dtime[1]}%",
                 color=C["green"] if auto_scaling else C["amber"], fontsize=10, y=1.04)
    plt.tight_layout(pad=1.0)
    return fig

def make_whatif(user_load, spot_avail):
    loads     = np.arange(10, 101, 10)
    cost_od   = 0.085 * loads / 10
    cost_spot = cost_od * (1 - spot_avail/220)
    lat_base  = 18 + loads * 1.15
    lat_rl    = lat_base * 0.82
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.8, 3.0))
    for ax in (ax1, ax2):
        style_ax(ax, fig)
    ax1.plot(loads, cost_od,   color=C["red"],   lw=2.0, label="On-demand")
    ax1.plot(loads, cost_spot, color=C["green"], lw=2.0, ls="--", label="With spot")
    ax1.axvline(user_load, color=C["amber"], lw=1.2, ls=":", label=f"Now {int(user_load)}%")
    ax1.set_title("Predicted Cost", color=C["text"], fontsize=10, fontweight="bold")
    ax1.set_xlabel("Load (%)", fontsize=9)
    ax1.set_ylabel("$/hr", fontsize=9)
    _leg(ax1)
    ax2.plot(loads, lat_base, color=C["amber"], lw=2.0, label="No RL")
    ax2.plot(loads, lat_rl,   color=C["cyan"],  lw=2.0, ls="--", label="With RL")
    ax2.axhline(100, color=C["red"], lw=1.0, ls=":", label="SLA 100ms")
    ax2.axvline(user_load, color=C["amber"], lw=1.2, ls=":")
    ax2.set_title("Predicted Latency", color=C["text"], fontsize=10, fontweight="bold")
    ax2.set_xlabel("Load (%)", fontsize=9)
    ax2.set_ylabel("ms", fontsize=9)
    _leg(ax2)
    plt.tight_layout(pad=1.0)
    return fig

# ═══════════════════════════════════════════════════════════════════
#  AI DECISION ENGINE
# ═══════════════════════════════════════════════════════════════════
DECISIONS = {
    "scale_up":    ("Scale Up  +2 servers",    "High latency spike detected",    C["red"]),
    "scale_down":  ("Scale Down  -1 server",   "Load dropping — saving cost",    C["green"]),
    "spot_switch": ("Switch to Spot Instances","Budget threshold approaching",   C["amber"]),
    "hold":        ("Hold — no change needed", "System within normal thresholds",C["cyan"]),
    "chaos_resp":  ("Emergency Scale Up  +4",  "Chaos event detected!",          C["red"]),
}
XAI = {
    "scale_up":    ["Latency > 80 ms threshold", "Load trend +12% rising",      "Budget still safe"],
    "scale_down":  ["Load < 35%",                "Servers under-utilised",       "Cost optimisation trigger"],
    "spot_switch": ["Burn rate > $0.45/hr",       "Spot availability > 60%",     "Budget constraint active"],
    "hold":        ["All metrics nominal",         "No threshold breached",       "Agent confidence stable"],
    "chaos_resp":  ["Multiple server failures",    "Latency > 150 ms",            "Load spike > 200%"],
}

def get_decision(user_load, spot_avail, chaos_monkey, budget_on, latency):
    if chaos_monkey and latency > 120:   key = "chaos_resp"
    elif user_load > 80 and latency > 80: key = "scale_up"
    elif user_load < 35:                  key = "scale_down"
    elif budget_on and spot_avail > 50:   key = "spot_switch"
    else:                                 key = "hold"
    action, reason, color = DECISIONS[key]
    conf = random.randint(85, 99) if key != "hold" else random.randint(70, 88)
    return key, action, reason, conf, XAI[key]

def health_badge(latency, load, drisk):
    if latency > 120 or load > 850 or drisk == "High":
        return "🔴  CRITICAL — System Under Stress", "red"
    elif latency > 70 or load > 600 or drisk == "Medium":
        return "🟡  WARNING — Elevated Load", "amber"
    return "🟢  HEALTHY — All Systems Nominal", "green"

# ═══════════════════════════════════════════════════════════════════
#  MAIN SIMULATION  —  returns exactly 23 values, matching outputs
# ═══════════════════════════════════════════════════════════════════
_tick = 0

def run_simulation(scenario, user_load, spot_avail,
                   chaos_monkey, budget_on, auto_scaling):
    global _tick
    _tick += 1
    seed = _tick

    t       = datetime.now().strftime("%H:%M:%S")
    load    = int(user_load * 9.5)
    servers = random.randint(8, 20)
    burn    = round(random.uniform(0.18, 0.44 if budget_on else 0.82), 2)
    latency = random.randint(22, 70 if not chaos_monkey else 165)
    score   = round(random.uniform(0.83, 1.0) if auto_scaling
                    else random.uniform(0.50, 0.77), 2)
    spend_str = "$680" if auto_scaling else "$1,250"
    savings   = f"{round((1-680/1250)*100)}%" if auto_scaling else "0%"
    drisk     = ("Low"    if latency < 60 and load < 600
                 else "Medium" if latency < 110
                 else "High")

    key, action, reason, conf, xai = get_decision(
        user_load, spot_avail, chaos_monkey, budget_on, latency)
    health_txt, _ = health_badge(latency, load, drisk)

    decision_md = f"""### 🧠 AI Decision
**→ {action}**

| | |
|---|---|
| Confidence | `{conf}%` |
| Reason | {reason} |
| Scenario | {scenario.split(':')[0]} |
| Time | `{t}` |
"""
    xai_md     = "### 💡 Why did AI decide this?\n" + "".join(f"- ✔ {r}\n" for r in xai)
    health_md  = f"""### {health_txt}

| Metric | Value |
|---|---|
| Latency | `{latency} ms` |
| Load | `{load} req/s` |
| Downtime risk | `{drisk}` |
| Agent score | `{score} / 1.0` |
"""
    pred_cost  = round(burn * (user_load / 48), 2)
    pred_lat   = round(latency * (user_load / 58), 1)
    risk_lbl   = ("🔴 HIGH"   if pred_lat > 100 or pred_cost > 0.65
                  else "🟡 MEDIUM" if pred_lat > 60
                  else "🟢 LOW")
    whatif_md  = f"""### 🔮 What-If Simulation
*If Load = {int(user_load)}% continues...*

| Prediction | Value |
|---|---|
| Predicted cost | `${pred_cost}/hr` |
| Predicted latency | `{pred_lat} ms` |
| Risk level | {risk_lbl} |
| Estimated savings | `{savings}` |
"""
    log  = f"[{t}]  {scenario}\n"
    log += f"[{t}]  Load: {load} req/s  |  Servers: {servers}  |  Burn: ${burn}/hr\n"
    log += f"[{t}]  Latency: {latency} ms  |  Risk: {drisk}\n"
    log += f"[{t}]  DECISION: {action}  (conf {conf}%)\n"
    log += f"[{t}]  Score: {score} / 1.0  |  Savings: {savings}"

    # ── charts ──
    gauge_fig  = make_gauge_chart(int(user_load), "User Load",  C["cyan"],   seed)
    burst_fig  = make_radial_burst(load,           "req/s",      C["purple"], seed)
    burst2_fig = make_radial_burst(int(score*100), "Score×100",  C["green"],  seed+1)
    area_fig   = make_area_chart(user_load, seed)
    bar_fig    = make_neon_bar(auto_scaling, seed)
    wave_fig   = make_waveform_cost(budget_on, spot_avail, seed)
    lat_fig    = make_latency_wave(chaos_monkey, seed)
    reward_fig = make_reward_curve(auto_scaling, seed)
    before_fig = make_before_after(auto_scaling)
    whatif_fig = make_whatif(int(user_load), int(spot_avail))

    # ── 23 return values — perfectly matches outputs list below ──
    return (
        f"🚀  {load}  req/s",           # load_out
        f"🖥️  {servers}  instances",    # server_out
        f"💸  ${burn}/hr",              # burn_out
        f"⚡  {latency} ms",            # latency_out
        f"💰  {savings}  saved",        # savings_out
        f"🏆  {score} / 1.0",           # score_out
        decision_md,                    # decision_out
        xai_md,                         # xai_out
        health_md,                      # health_out
        whatif_md,                      # whatif_out
        log,                            # log_out
        spend_str,                      # spend_out2
        drisk,                          # risk_out
        score,                          # score_num  ← raw float, fixes the Error bug
        gauge_fig,                      # gauge_plot
        burst_fig,                      # burst_plot
        burst2_fig,                     # burst2_plot
        area_fig,                       # area_plot
        bar_fig,                        # bar_plot
        wave_fig,                       # wave_plot
        lat_fig,                        # lat_plot
        reward_fig,                     # reward_plot
        before_fig,                     # before_plot
        whatif_fig,                     # whatif_plot  ← 24 total
    )

# ═══════════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════════
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Mono&family=Inter:wght@400;600;700;800&display=swap');

body, .gradio-container {
    background: #06091a !important;
    color: #e2eeff !important;
    font-family: 'Inter', sans-serif !important;
}
.gr-panel, .gr-box, .gr-form, .gr-block {
    background: rgba(11,17,32,0.85) !important;
    border: 0.5px solid #1e3a5f !important;
    border-radius: 14px !important;
    backdrop-filter: blur(12px) !important;
}
.hero-metric textarea, .hero-metric input {
    font-size: 22px !important; font-weight: 800 !important;
    color: #00e5ff !important; text-align: center !important;
    background: rgba(0,229,255,0.06) !important;
    border: 1px solid rgba(0,229,255,0.25) !important;
    border-radius: 12px !important; padding: 18px 10px !important;
}
.sec-metric textarea, .sec-metric input {
    font-size: 17px !important; font-weight: 700 !important;
    color: #a78bfa !important; text-align: center !important;
    background: rgba(167,139,250,0.06) !important;
    border: 0.5px solid rgba(167,139,250,0.22) !important;
    border-radius: 10px !important; padding: 12px 8px !important;
}
.card-decision { background: rgba(255,61,90,0.07) !important; border: 1px solid rgba(255,61,90,0.35) !important; border-radius: 14px !important; padding: 6px 10px !important; }
.card-decision h3 { color: #ff3d5a !important; }
.card-xai { background: rgba(0,229,255,0.05) !important; border: 1px solid rgba(0,229,255,0.25) !important; border-radius: 14px !important; padding: 6px 10px !important; }
.card-xai h3 { color: #00e5ff !important; }
.card-health { background: rgba(0,255,157,0.06) !important; border: 1px solid rgba(0,255,157,0.28) !important; border-radius: 14px !important; padding: 6px 10px !important; }
.card-health h3 { color: #00ff9d !important; }
.card-whatif { background: rgba(192,132,252,0.06) !important; border: 1px solid rgba(192,132,252,0.28) !important; border-radius: 14px !important; padding: 6px 10px !important; }
.card-whatif h3 { color: #c084fc !important; }
.gr-button-primary {
    background: linear-gradient(135deg, rgba(0,229,255,0.15), rgba(0,255,157,0.10)) !important;
    border: 1.5px solid #00e5ff !important; color: #00e5ff !important;
    font-size: 15px !important; font-weight: 700 !important;
    letter-spacing: 2px !important; border-radius: 12px !important;
    padding: 14px 0 !important; text-transform: uppercase !important;
}
.gr-button-primary:hover { background: rgba(0,229,255,0.22) !important; border-color: #00ff9d !important; color: #00ff9d !important; }
label, .gr-input-label { color: #4a6080 !important; font-size: 11px !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; }
input, select, textarea { background: #0a1020 !important; color: #e2eeff !important; border: 0.5px solid #1e3a5f !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important; }
.log-panel textarea { font-family: 'Space Mono', monospace !important; font-size: 11.5px !important; color: #7ab0d0 !important; background: #050810 !important; border: 0.5px solid #1e3a5f !important; border-radius: 10px !important; line-height: 1.9 !important; }
.score-box input { font-size: 30px !important; font-weight: 900 !important; color: #00ff9d !important; text-align: center !important; background: rgba(0,255,157,0.07) !important; border: 1px solid rgba(0,255,157,0.30) !important; border-radius: 12px !important; }
.gr-plot { background: rgba(11,17,32,0.90) !important; border: 0.5px solid #1e3a5f !important; border-radius: 12px !important; padding: 6px !important; }
.gr-markdown table { font-size: 13px !important; width: 100% !important; }
.gr-markdown td, .gr-markdown th { padding: 5px 8px !important; border-color: #1e3a5f !important; }
.gr-markdown h3 { font-size: 14px !important; margin-bottom: 8px !important; }
.gr-markdown code { background: rgba(0,229,255,0.10) !important; color: #00e5ff !important; border-radius: 4px !important; padding: 1px 6px !important; font-family: 'Space Mono', monospace !important; font-size: 12px !important; }
hr { border-color: #1e3a5f !important; margin: 14px 0 !important; }
.gr-markdown h2 { color: #00e5ff !important; letter-spacing: 1px !important; border-bottom: 1px solid #1e3a5f !important; padding-bottom: 6px !important; }
"""

# ═══════════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════════
with gr.Blocks(css=CSS, title="☁️ Cloud-Cost Guardian AI") as demo:

    gr.Markdown("# ☁️  Cloud-Cost Guardian AI\n#### RL-Powered Autonomous Infrastructure — Live Intelligence Dashboard\n---")

    gr.Markdown("## 📊 Live System Metrics")
    with gr.Row(equal_height=True):
        load_out    = gr.Textbox(label="🚀 Incoming Load",  interactive=False, elem_classes="hero-metric")
        savings_out = gr.Textbox(label="💰 Cost Saved",     interactive=False, elem_classes="hero-metric")
        score_out   = gr.Textbox(label="🏆 Agent Score",    interactive=False, elem_classes="hero-metric")

    with gr.Row(equal_height=True):
        server_out  = gr.Textbox(label="🖥️ Servers",   interactive=False, elem_classes="sec-metric")
        burn_out    = gr.Textbox(label="💸 Burn Rate",  interactive=False, elem_classes="sec-metric")
        latency_out = gr.Textbox(label="⚡ Latency",    interactive=False, elem_classes="sec-metric")

    gr.Markdown("---")

    with gr.Row():
        with gr.Column(scale=1, min_width=260):
            gr.Markdown("## 🎮 Controls")
            scenario     = gr.Dropdown(
                choices=["Scenario 1: Steady Load (Easy)",
                         "Scenario 2: Daily Peak Surges (Medium)",
                         "Scenario 3: Chaos Mode (Hard)"],
                value="Scenario 2: Daily Peak Surges (Medium)", label="Scenario")
            user_load    = gr.Slider(0, 100, value=75, step=1, label="User Load Scale (%)")
            spot_avail   = gr.Slider(0, 100, value=40, step=1, label="Spot Availability (%)")
            chaos_monkey = gr.Checkbox(value=False, label="🐒 Chaos Monkey — Hard Mode")
            budget_constr= gr.Checkbox(value=True,  label="💰 Budget Constraint Active")
            auto_scaling = gr.Checkbox(value=True,  label="🤖 RL Auto-Scaling Agent ON")
            run_btn      = gr.Button("🚀  RUN SIMULATION", variant="primary", size="lg")

        with gr.Column(scale=1, min_width=260):
            decision_out = gr.Markdown("### 🧠 AI Decision\n*Click Run to start...*", elem_classes="card-decision")
            xai_out      = gr.Markdown("### 💡 Explainable AI\n*Waiting...*",          elem_classes="card-xai")

        with gr.Column(scale=1, min_width=260):
            health_out   = gr.Markdown("### 🟢 Health Status\n*Click Run...*",         elem_classes="card-health")
            whatif_out   = gr.Markdown("### 🔮 What-If Simulation\n*Adjust sliders...*",elem_classes="card-whatif")

    gr.Markdown("---")

    with gr.Row():
        with gr.Column(scale=3):
            log_out    = gr.Textbox(lines=5, label="📋 Agent Action Log", interactive=False, elem_classes="log-panel")
        with gr.Column(scale=1):
            spend_out2 = gr.Textbox(label="Total Spend",       interactive=False)
            risk_out   = gr.Textbox(label="Downtime Risk",      interactive=False)
            score_num  = gr.Number( label="Agent Score / 1.0",  interactive=False, elem_classes="score-box")

    gr.Markdown("---")
    gr.Markdown("## 🎯 Radial Intelligence — Live Gauges")
    with gr.Row():
        gauge_plot  = gr.Plot(label="Load Gauge")
        burst_plot  = gr.Plot(label="Request Burst")
        burst2_plot = gr.Plot(label="Score Burst")

    gr.Markdown("---")
    gr.Markdown("## 📈 Traffic & Utilisation")
    with gr.Row():
        area_plot = gr.Plot(label="Traffic Load — Area")
        bar_plot  = gr.Plot(label="Server Utilisation — Neon Bars")

    gr.Markdown("---")
    gr.Markdown("## 💡 Cost & Performance Waveforms")
    with gr.Row():
        wave_plot = gr.Plot(label="Cost Burn Waveform")
        lat_plot  = gr.Plot(label="Latency Waveform + SLA")

    gr.Markdown("---")
    gr.Markdown("## 🧠 RL Intelligence & Impact")
    with gr.Row():
        reward_plot = gr.Plot(label="Cumulative RL Reward")
        before_plot = gr.Plot(label="Before vs After RL")
        whatif_plot = gr.Plot(label="What-If: Cost & Latency")

    gr.Markdown("> 💡 **Pro tip:** Turn on **Chaos Monkey** + set Load to **90%** for maximum drama!")

    # ── wire — outputs count must equal return tuple length (24) ──
    run_btn.click(
        fn=run_simulation,
        inputs=[scenario, user_load, spot_avail, chaos_monkey, budget_constr, auto_scaling],
        outputs=[
            load_out, server_out, burn_out, latency_out, savings_out, score_out,
            decision_out, xai_out, health_out, whatif_out,
            log_out, spend_out2, risk_out,
            score_num,          # gr.Number ← now receives raw float from return tuple
            gauge_plot, burst_plot, burst2_plot,
            area_plot, bar_plot,
            wave_plot, lat_plot,
            reward_plot, before_plot, whatif_plot,
        ]
    )

if __name__ == "__main__":
    demo.launch(share=True)
