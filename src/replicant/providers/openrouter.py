import os
import time
import requests

URL = "https://openrouter.ai/api/v1/chat/completions"


def complete(messages: list[dict], model: str, api_key: str = None) -> str:
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
        return r.json()["choices"][0]["message"].get("content", "") or ""

    return ""
