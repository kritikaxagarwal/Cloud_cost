from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from environment import CloudCostEnv

app = FastAPI()
_env = CloudCostEnv()

class StepRequest(BaseModel):
    action: int

@app.post("/reset")
async def reset():
    state = await _env.reset()
    if hasattr(state, 'model_dump'):
        return state.model_dump()
    return state

@app.post("/step")
async def step(req: StepRequest):
    state, reward, done = await _env.step(req.action)
    if hasattr(state, 'model_dump'):
        state_data = state.model_dump()
    else:
        state_data = state
    return {"state": state_data, "reward": reward, "done": done}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/state")
async def get_state():
    state = await _env.state()
    if hasattr(state, 'model_dump'):
        return state.model_dump()
    return state

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
