import gradio as gr
import random
import time
from datetime import datetime

# ─────────────────────────────────────────
#  Import your friend's code here (Step 3)
#  from cloud_guardian import run_agent
# ─────────────────────────────────────────

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def run_simulation(scenario, user_load, spot_avail, chaos_monkey, budget_on, auto_scaling):
    """
    RIGHT NOW: uses fake random data so you can see the UI work.
    LATER: replace the inside with your friend's real function.
    """
    t = get_timestamp()

    # Fake metrics — replace with real ones later
    load       = int(user_load * 10)
    servers    = random.randint(8, 20)
    burn_rate  = round(random.uniform(0.2, 0.6), 2)
    latency    = random.randint(30, 120)
    score      = round(random.uniform(0.75, 1.0), 2)

    spend      = "$680"  if auto_scaling else "$1,250"
    downtime   = "🟢 Low" if auto_scaling else "🟡 Medium"

    log  = f"[{t}] Load: {load} → ACTION: Add Instance (t3.medium)\n"
    log += f"[{t}] Latency improved to {latency}ms. Budget Remaining: $12\n"
    log += f"[{t}] Cost > Threshold → ACTION: Switch to Spot Instance\n"
    log += f"[{t}] Final Score: {score} / 1.0"

    return (
        f"🔥 {load} req/sec",
        f"🖥️ {servers} instances",
        f"💸 ${burn_rate}/hr",
        log,
        spend,
        downtime,
        score
    )

# ──────────────────────────────────────────────
#  BUILD THE UI
# ──────────────────────────────────────────────
with gr.Blocks(
    title="☁️ Cloud-Cost Guardian AI",
    theme=gr.themes.Base(
        primary_hue="cyan",
        neutral_hue="slate",
    ),
    css="""
    .gradio-container { max-width: 1100px !important; }
    .metric-box { text-align: center; font-size: 1.4em; font-weight: bold; }
    """
) as demo:

    # ── Header ──
    gr.Markdown("""
    # ☁️ Cloud-Cost Guardian AI
    ### Live Simulation Dashboard
    ---
    """)

    # ── Metric cards row ──
    with gr.Row():
        load_out    = gr.Textbox(label="📈 Incoming Load",    elem_classes="metric-box", interactive=False)
        server_out  = gr.Textbox(label="🖥️ Active Servers",  elem_classes="metric-box", interactive=False)
        burn_out    = gr.Textbox(label="💸 Hourly Burn Rate", elem_classes="metric-box", interactive=False)

    gr.Markdown("---")

    # ── Controls + Log side by side ──
    with gr.Row():

        # Left column — controls
        with gr.Column(scale=1):
            gr.Markdown("### 🎮 Simulation Controls")

            scenario = gr.Dropdown(
                choices=[
                    "Scenario 1: Steady Load (Easy)",
                    "Scenario 2: Daily Peak Surges (Medium)",
                    "Scenario 3: Chaos Mode (Hard)"
                ],
                value="Scenario 2: Daily Peak Surges (Medium)",
                label="Select Scenario"
            )
            user_load    = gr.Slider(0, 100, value=75, step=1,  label="User Load Scale (%)")
            spot_avail   = gr.Slider(0, 100, value=40, step=1,  label="Spot Instance Availability (%)")
            chaos_monkey = gr.Checkbox(value=False, label="🐒 Chaos Monkey (Hard Tasks)")
            budget_constr= gr.Checkbox(value=True,  label="💰 Budget Constraint")
            auto_scaling = gr.Checkbox(value=True,  label="🤖 Auto-Scaling Agent")

            run_btn = gr.Button("🚀 Reset Environment & Restart Agent", variant="primary", size="lg")

        # Right column — outputs
        with gr.Column(scale=2):
            gr.Markdown("### 📋 Agent Action Log")
            log_out      = gr.Textbox(lines=6,  label="Live Log",       interactive=False)

            with gr.Row():
                spend_out   = gr.Textbox(label="Total Spend",    interactive=False)
                risk_out    = gr.Textbox(label="Downtime Risk",  interactive=False)

            score_out = gr.Number(label="🏆 Final Agent Score (out of 1.0)", interactive=False)

    # ── Wire button to function ──
    run_btn.click(
        fn=run_simulation,
        inputs=[scenario, user_load, spot_avail, chaos_monkey, budget_constr, auto_scaling],
        outputs=[load_out, server_out, burn_out, log_out, spend_out, risk_out, score_out]
    )

    gr.Markdown("""
    ---
    > 💡 Tip: Click **Reset Environment** after changing any setting to see updated results.
    """)

# ── Launch ──
if __name__ == "__main__":
    demo.launch(share=True)   # share=True gives you a public link