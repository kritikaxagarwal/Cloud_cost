import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from environment import CloudCostEnv

load_dotenv()

# --- MANDATORY LOGGING FUNCTIONS (Don't Change) ---
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error=None) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = "You are a Cloud Infrastructure AI. Manage the cluster by choosing actions: 0(Stay), 1(Add Server), 2(Remove), 3(Toggle Spot). Reply with ONLY the integer."

# --- GET ACTION FROM LLM ---
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

# --- MAIN AGENT LOOP ---
async def main():
    api_base = os.getenv("API_BASE_URL")
    api_key = os.getenv("HF_TOKEN")
    model_name = os.getenv("MODEL_NAME")

    task_id = "daily_peaks"
    env = CloudCostEnv(task="medium")
    log_start(task=task_id, env="CloudEnv-v1", model=model_name)

    rewards = []
    state = await env.reset()

    try:
        for step in range(1, 21):
            action_int, action_text = await get_action_from_llama(state)
            state, reward, done = await env.step(action_int)
            log_step(step=step, action=str(action_int), reward=reward, done=done)
            rewards.append(reward)
            if done:
                break

        avg_score = sum(rewards) / len(rewards) if rewards else 0
        log_end(
            success=(avg_score >= 0.7),
            steps=len(rewards),
            score=avg_score,
            rewards=rewards
        )
    except Exception as e:
        log_step(step=0, action="error", reward=0.0, done=True, error=str(e))
    finally:
        await env.close()

if __name__ == "__main__":
    asyncio.run(main())
