# ☁️ Cloud-Cost Guardian AI

> **RL-Powered Autonomous Infrastructure — Live Intelligence Dashboard**

An autonomous cloud cost optimization system that uses a **custom RL environment** + **pluggable LLM agent** to analyze real-time infrastructure telemetry and make intelligent scaling decisions — balancing cost efficiency against demand without human intervention.

---

## 🎯 What It Does

Cloud-Cost Guardian AI simulates a live cloud infrastructure where an LLM agent autonomously decides every step — scale up, scale down, switch to spot instances, or hold. The environment rewards cost-efficient decisions while penalising latency breaches above the 100ms SLA threshold.

---

## ✨ Key Features

- **🧠 LLM-Powered Agent** — OpenAI-compatible client analyzes real-time state and picks optimal scaling actions
- **📊 Live Intelligence Dashboard** — incoming load, cost burn rate, server count, latency, agent score — all live
- **🎮 Interactive Scenarios** — Steady Load / Daily Peak Surges / Chaos Mode with adjustable sliders
- **💡 Explainable AI Decisions** — every action shows confidence %, reason, and full "Why did AI decide this?" breakdown
- **🔮 What-If Simulation** — predicts future cost and latency if current load continues
- **📉 Cost & Performance Waveforms** — visual cost burn vs budget + latency vs 99th pct SLA
- **📈 Cumulative RL Reward Chart** — agent performance vs static baseline over episodes
- **🆚 Before vs After** — side-by-side spend and downtime risk comparison
- **🐒 Chaos Monkey Mode** — random latency spikes and failure injection for stress testing
- **💰 Budget Constraint** — hard budget cap with real-time over-budget alerts
- **🎯 Radial Intelligence Gauges** — neon live gauges for load %, request burst, agent score

---

## 🎮 Action Space

| ID | Action | Description |
|---|---|---|
| `0` | Stay | Hold — system within normal thresholds |
| `1` | Provision Instance | Scale up — add a new server |
| `2` | Terminate Instance | Scale down — remove an idle server |
| `3` | Toggle Spot Instances | Switch to cheaper spot/preemptible compute |

---

## 📡 Observation Space

| Field | Description |
|---|---|
| `cpu_usage` | Average CPU utilization across all instances |
| `active_servers` | Current number of running instances |
| `hourly_burn_rate` | Current spend in $/hr |
| `response_latency` | Response latency in ms |
| `incoming_load` | Request throughput in req/s |

---

## 📈 Results

| Metric | Value |
|---|---|
| Agent Score Range | 0.0 – 1.0 (threshold-based grading) |
| Latency SLA | 100 ms (breaches penalised) |
| Budget SLA | $0.5/hr (overrun penalised) |
| Tasks | 3 (easy / medium / hard) |


---

## 🚀 Getting Started

### Run Locally

```bash
git clone https://github.com/kritikaxagarwal/Cloud_cost
cd Cloud_cost
pip install -r requirements.txt
python app.py
```

### Run via Docker

```bash
docker build -t cloud-cost-guardian .
docker run -p 7860:7860 cloud-cost-guardian
```

### Run Inference

```bash
export API_BASE_URL=<your LLM API base URL>
export MODEL_NAME=<model identifier>
export HF_TOKEN=<your Hugging Face token>
python inference.py
```

---

## 🗂️ Project Structure

```
Cloud_cost/
├── app.py              # Gradio dashboard + FastAPI (/reset /step /state /health)
├── environment.py      # CloudCostEnv — async reset, step, state, close
├── inference.py        # LLM agent — 3 tasks, [START][STEP][END] logs
├── models.py           # Pydantic State model
├── openenv.yaml        # OpenEnv spec — tasks, graders, endpoints
├── Dockerfile          # HF Spaces Docker config (port 7860)
├── requirements.txt    # Dependencies
└── server/             # Additional server utilities
```

---

## 🛠️ Tech Stack

- **Gradio** — Live dashboard UI
- **FastAPI + Uvicorn** — OpenEnv-compliant API server
- **OpenAI-compatible client** — Pluggable LLM agent
- **Matplotlib** — Neon dark theme charts
- **Pydantic** — Typed state schema
- **Docker** — Containerised deployment to Hugging Face Spaces

---

## 🌐 OpenEnv Compliance

This environment is fully compliant with the **OpenEnv spec**:

- `POST /reset` — resets environment, returns initial state
- `POST /step` — takes action, returns next state + reward + done
- `GET /state` — returns current state
- `GET /health` — returns `{"status": "ok"}`
- `openenv.yaml` — defines tasks, graders, endpoints, entry point
- Typed state schema via **Pydantic**
- Rewards strictly clamped **0.01 – 0.99**

---

## 🏆 Built For

**Meta × Hugging Face OpenEnv Hackathon** — autonomous AI agents for real-world infrastructure optimization.

---

## 👥 Contributors

- [@kritikaxagarwal](https://github.com/kritikaxagarwal)
- [@ankitxraj21](https://huggingface.co/ankitxraj21)
- [@arghadee-cyber](https://github.com/arghadee-cyber)
