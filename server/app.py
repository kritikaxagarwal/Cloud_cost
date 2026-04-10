from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from environment import CloudCostEnv

app = FastAPI()
env = CloudCostEnv()

class StepRequest(BaseModel):
    action: int

@app.post("/reset")
async def reset():
    return await env.reset()

@app.post("/step")
async def step(req: StepRequest):
    state, reward, done = await env.step(req.action)
    return {"state": state, "reward": reward, "done": done}

@app.get("/state")
async def get_state():
    return await env.state()
