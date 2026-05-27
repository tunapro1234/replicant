import os
import time
import requests

URL = "https://openrouter.ai/api/v1/chat/completions"

total_cost = 0.0


def complete(messages: list[dict], model: str, api_key: str = None) -> str:
    global total_cost
    api_key = api_key or os.environ.get("OPEN_ROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("No API key. Set OPEN_ROUTER_API_KEY.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "messages": messages}

    for attempt in range(3):
        r = requests.post(URL, headers=headers, json=payload, timeout=600)
        if r.status_code == 429:
            time.sleep(3 * (attempt + 1))
            continue
        r.raise_for_status()
        data = r.json()
        usage = data.get("usage", {})
        total_cost += float(usage.get("total_cost", 0))
        return data["choices"][0]["message"].get("content", "") or ""

    return ""


def reset_cost():
    global total_cost
    total_cost = 0.0


def get_cost():
    return total_cost
