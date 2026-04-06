from pydantic import BaseModel

# This model defines what the AI sees (The "State")
class State(BaseModel):
    cpu_usage: float           # 0.0 to 100.0
    active_servers: int        # Count of running VMs
    hourly_burn_rate: float    # Cost in USD
    response_latency: float    # In milliseconds (ms)
    incoming_load: int         # Number of requests/users

# This model defines what the AI can do (The "Action")
class Action(BaseModel):
    # 0: Stay (Do nothing)
    # 1: Provision (Add server)
    # 2: Terminate (Remove server)
    # 3: Switch to Spot (Toggle cheap mode)
    action_type: int