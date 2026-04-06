
# Cloud-Cost Guardian AI

This is an RL environment for optimizing cloud infrastructure costs.

## Action Space
- 0: Stay
- 1: Provision Instance
- 2: Terminate Instance
- 3: Toggle Spot Instances

## Observation Space
- CPU Usage, Active Servers, Burn Rate, Latency, Incoming Load.

## Setup
Built for the OpenEnv Hackathon. Deployable to Hugging Face Spaces via Docker.

