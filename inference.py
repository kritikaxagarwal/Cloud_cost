import os
import json
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from environment import CloudCostEnv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)
env = None
event_loop = None

# --- MANDATORY LOGGING FUNCTIONS (Don't Change) ---
def log_start(task: str, env_name: str, model: str) -> None:
    print(f"[START] task={task} env={env_name} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error=None) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = "You are a Cloud Infrastructure AI. Manage the cluster by choosing actions: 0(Stay), 1(Add Server), 2(Remove), 3(Toggle Spot). Reply with ONLY the integer."

# --- GET EVENT LOOP (fixes asyncio + Flask conflict) ---
def get_loop():
    global event_loop
    try:
        if event_loop is None or event_loop.is_closed():
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
        return event_loop
    except Exception:
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        return event_loop

# --- LLM ACTION ---
async def get_action_from_llama(state):
    api_base = os.getenv("API_BASE_URL")
    api_key = os.getenv("HF_TOKEN")
    model_name = os.getenv("MODEL_NAME")
    client = OpenAI(base_url=api_base, api_key=api_key)
    state_data = state.model_dump_json() if hasattr(state, 'model_dump_json') else str(state)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Current State: {state_data}"}
            ],
            max_tokens=10
        )
        action_text = response.choices[0].message.content.strip()
        action_int = int(''.join(filter(str.isdigit, action_text))[0])
        return action_int, action_text
    except Exception as e:
        return 0, f"Error: {str(e)}"

# --- ROUTES ---

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/reset', methods=['POST'])
def reset():
    global env
    try:
        loop = get_loop()
        env = CloudCostEnv(task="medium")
        state = loop.run_until_complete(env.reset())
        log_start(
            task="daily_peaks",
            env_name="CloudEnv-v1",
            model=os.getenv("MODEL_NAME", "unknown")
        )
        if hasattr(state, 'model_dump'):
            state_data = state.model_dump()
        elif hasattr(state, 'model_dump_json'):
            state_data = json.loads(state.model_dump_json())
        else:
            state_data = str(state)
        return jsonify({"status": "ok", "state": state_data}), 200
    except Exception as e:
        print(f"[ERROR] reset failed: {str(e)}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/step', methods=['POST'])
def step():
    global env
    try:
        if env is None:
            return jsonify({"status": "error", "message": "Call /reset first"}), 400
        data = request.get_json()
        action = int(data.get("action", 0))
        loop = get_loop()
        state, reward, done = loop.run_until_complete(env.step(action))
        log_step(step=1, action=str(action), reward=reward, done=done)
        if hasattr(state, 'model_dump'):
            state_data = state.model_dump()
        elif hasattr(state, 'model_dump_json'):
            state_data = json.loads(state.model_dump_json())
        else:
            state_data = str(state)
        return jsonify({
            "state": state_data,
            "reward": reward,
            "done": done
        }), 200
    except Exception as e:
        print(f"[ERROR] step failed: {str(e)}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500

# --- TERMINAL TESTING (unchanged) ---
async def main():
    model_name = os.getenv("MODEL_NAME")
    task_id = "daily_peaks"
    env_local = CloudCostEnv(task="medium")
    log_start(task=task_id, env_name="CloudEnv-v1", model=model_name)
    rewards = []
    state = await env_local.reset()
    try:
        for step_num in range(1, 21):
            action_int, action_text = await get_action_from_llama(state)
            state, reward, done = await env_local.step(action_int)
            log_step(step=step_num, action=str(action_int), reward=reward, done=done)
            rewards.append(reward)
            if done:
                break
        avg_score = sum(rewards) / len(rewards) if rewards else 0
        log_end(success=(avg_score >= 0.7), steps=len(rewards),
                score=avg_score, rewards=rewards)
    except Exception as e:
        log_step(step=0, action="error", reward=0.0, done=True, error=str(e))
    finally:
        await env_local.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
