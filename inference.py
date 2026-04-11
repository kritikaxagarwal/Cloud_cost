import os
import json
import asyncio
import traceback
from dotenv import load_dotenv
from openai import OpenAI
from environment import CloudCostEnv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)
env = None

def log_start(task, env_name, model):
    print(f"[START] task={task} env={env_name} model={model}", flush=True)

def log_step(step, action, reward, done, error=None):
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

SYSTEM_PROMPT = "You are a Cloud Infrastructure AI. Manage the cluster by choosing actions: 0(Stay), 1(Add Server), 2(Remove), 3(Toggle Spot). Reply with ONLY the integer."

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
        return loop.run_until_complete(coro)
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/reset', methods=['POST'])
def reset():
    global env
    print("[DEBUG] /reset called", flush=True)
    try:
        env = CloudCostEnv(task="medium")
        state = run_async(env.reset())
        log_start(
            task="daily_peaks",
            env_name="CloudEnv-v1",
            model=os.getenv("MODEL_NAME", "unknown")
        )
        if hasattr(state, 'model_dump'):
            state_data = state.model_dump()
        elif hasattr(state, 'model_dump_json'):
            state_data = json.loads(state.model_dump_json())
        elif hasattr(state, '__dict__'):
            state_data = state.__dict__
        else:
            state_data = str(state)

        print("[DEBUG] /reset success", flush=True)
        return jsonify({"status": "ok", "state": state_data}), 200

    except Exception as e:
        full_error = traceback.format_exc()
        print(f"[ERROR] /reset crashed:\n{full_error}", flush=True)
        return jsonify({
            "status": "error",
            "message": str(e),
            "trace": full_error
        }), 500

@app.route('/step', methods=['POST'])
def step():
    global env
    try:
        if env is None:
            return jsonify({"status": "error", "message": "Call /reset first"}), 400

        data = request.get_json()
        action = int(data.get("action", 0))
        state, reward, done = run_async(env.step(action))
        log_step(step=1, action=str(action), reward=reward, done=done)

        if hasattr(state, 'model_dump'):
            state_data = state.model_dump()
        elif hasattr(state, 'model_dump_json'):
            state_data = json.loads(state.model_dump_json())
        elif hasattr(state, '__dict__'):
            state_data = state.__dict__
        else:
            state_data = str(state)

        return jsonify({
            "state": state_data,
            "reward": reward,
            "done": done
        }), 200

    except Exception as e:
        full_error = traceback.format_exc()
        print(f"[ERROR] /step crashed:\n{full_error}", flush=True)
        return jsonify({
            "status": "error",
            "message": str(e),
            "trace": full_error
        }), 500

if __name__ == "__main__":
    print("[BOOT] Flask starting on port 8080", flush=True)
    app.run(host="0.0.0.0", port=8080, debug=False)
