import gradio as gr
import plotly.graph_objects as go
import asyncio
import pandas as pd
import os
from environment import CloudCostEnv
from inference import get_action_from_llama

# Initialize environment
env = CloudCostEnv()

async def run_comparison_sim(steps, scenario):
    # 1. RUN STATIC BASELINE (Before AI)
    state_static = await env.reset()
    env.task = scenario.lower().split()[0]
    static_costs = []
    for _ in range(steps):
        next_s, _, _ = await env.step(0) # Action 0 = Stay
        static_costs.append(next_s.hourly_burn_rate)
    
    # 2. RUN AI AGENT (After AI)
    state_ai = await env.reset()
    ai_results = []
    logs = []
    for i in range(1, steps + 1):
        action_int, action_name = await get_action_from_llama(state_ai)
        next_state, reward, done = await env.step(action_int)
        
        ai_results.append({
            "Step": i,
            "Load": next_state.incoming_load,
            "Servers": next_state.active_servers * 50,
            "Cost": next_state.hourly_burn_rate,
            "Reward": reward
        })
        logs.append(f"[Step {i}] Action: {action_name} | Reward: {reward:.2f}")
        state_ai = next_state
        if done: break
        
    return pd.DataFrame(ai_results), static_costs, "\n".join(logs)

def update_dashboard(scenario):
    df_ai, static_costs, log_text = asyncio.run(run_comparison_sim(20, scenario))
    
    # Chart 1: Traffic & Scaling (The original green/blue look)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_ai["Step"], y=df_ai["Load"], name="Incoming Load", line=dict(color="#00ffcc", width=3)))
    fig1.add_trace(go.Scatter(x=df_ai["Step"], y=df_ai["Servers"], name="Active Servers", line=dict(color="#3399ff", dash='dot')))
    fig1.update_layout(template="plotly_dark", title="Traffic & Scaling", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # Chart 2: Optimization Impact (Before vs After)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(y=static_costs, name="Before (Static)", line=dict(color="#ff4d4d", dash='dash')))
    fig2.add_trace(go.Scatter(y=df_ai["Cost"], name="After (AI)", fill='tozeroy', line=dict(color="#00f2ff")))
    fig2.update_layout(template="plotly_dark", title="Cost Optimization Impact", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    avg_reward = df_ai["Reward"].mean()
    score_text = f"{avg_reward:.2f} / 1.0"
    
    return fig1, fig2, log_text, score_text

# Custom CSS for that exact dark feel
custom_css = """
.gradio-container { background-color: #0b0f19 !important; }
#title-text { text-align: center; color: #00f2ff; font-family: 'Arial'; }
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="cyan"), css=custom_css) as demo:
    gr.Markdown("# 🛡️ Cloud-Cost Guardian AI Dashboard", elem_id="title-text")
    
    with gr.Row():
        traffic_plot = gr.Plot()
        impact_plot = gr.Plot()
        
    with gr.Row():
        with gr.Column(scale=1):
            scenario_opt = gr.Dropdown(["Daily Peaks", "Steady Load", "Chaos Monkey"], label="Scenario", value="Daily Peaks")
            run_btn = gr.Button("🚀 Run AI Optimization", variant="primary")
            score_display = gr.Label(label="Final Agent Score")
            
        with gr.Column(scale=2):
            log_box = gr.Textbox(label="Agent Action Log (Interpretable)", lines=8)

    run_btn.click(update_dashboard, inputs=[scenario_opt], outputs=[traffic_plot, impact_plot, log_box, score_display])

if __name__ == "__main__":
    demo.launch(share=True)