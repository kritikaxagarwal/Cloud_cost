import asyncio
import math
from models import State

class CloudCostEnv:
    def __init__(self, task="medium"):
        self.task = task
        self.reset_vars()

    def reset_vars(self):
        self.steps = 0
        self.servers = 5
        self.is_spot = False

    async def reset(self):          # ← added async HERE
        self.reset_vars()
        return self.get_current_state()

    def get_current_state(self):
        if self.task == "easy":
            load = 450
        else:
            load = int(500 + 350 * math.sin(self.steps / 5))

        capacity = self.servers * 100
        latency = max(20, (load / (capacity + 1)) * 150)
        base_rate = 0.60
        current_rate = base_rate * 0.25 if self.is_spot else base_rate
        cost = self.servers * current_rate

        return State(
            cpu_usage=min(100.0, (load / (capacity + 1)) * 100),
            active_servers=self.servers,
            hourly_burn_rate=round(cost, 2),
            response_latency=round(latency, 2),
            incoming_load=load
        )

    async def step(self, action_int):
        if action_int == 1:
            self.servers += 1
        elif action_int == 2:
            self.servers = max(1, self.servers - 1)
        elif action_int == 3:
            self.is_spot = not self.is_spot

        self.steps += 1
        state = self.get_current_state()

        reward = 1.0
        if state.response_latency > 150:
            reward -= 0.7
        if state.hourly_burn_rate > 5.0:
            reward -= 0.5

        done = self.steps >= 20
        return state, reward, done

    async def state(self):
        return self.get_current_state()

    async def close(self):
        pass
