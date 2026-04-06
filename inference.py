import os
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Actions ko readable aur interpretable banayein
ACTION_NAMES = {
    0: "Stay (Efficiency Optimized)",
    1: "Scale Up (Capacity +1)",
    2: "Scale Down (Cost -1)",
    3: "Switch to Spot (Save 60%)"
}

async def get_action_from_llama(state):
    api_base = os.getenv("API_BASE_URL")
    api_key = os.getenv("HF_TOKEN")
    model_name = os.getenv("MODEL_NAME")

    client = OpenAI(base_url=api_base, api_key=api_key)
    state_data = state.model_dump_json() if hasattr(state, 'model_dump_json') else str(state)
    
    try:
        # API Call with Timeout
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Choose action 0-3. Reply ONLY with the integer."},
                {"role": "user", "content": f"State: {state_data}"}
            ],
            max_tokens=5,
            timeout=8
        )
        action_text = response.choices[0].message.content.strip()
        action_int = int(''.join(filter(str.isdigit, action_text))[0])
        return action_int, f"{ACTION_NAMES.get(action_int, 'Stay')}"
    
    except Exception as e:
        # 🔥 SMART FALLBACK: API fail hone par demo rukega nahi
        load = state.incoming_load
        fallback_action = 1 if load > 450 else 0
        return fallback_action, f"{ACTION_NAMES[fallback_action]} (AI Fallback Active)"