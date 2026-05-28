import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from .client import OTreeClient, PageData, FormField
from ...providers import openrouter

MAX_RETRIES = 5


def play(participant_url: str, persona: str, model: str, api_key: str = None,
         temperature: float = 1.0, seed: int = None) -> dict:
    server_url = re.match(r'(https?://[^/]+)', participant_url).group(1)
    client = OTreeClient(server_url)
    log = []

    if not persona:
        from ...personas.baseline import build_prompt
        persona = build_prompt()

    system = persona + (
        "\n\nWhen asked to make a decision, respond with ONLY a valid JSON object. "
        "No explanation, no markdown, no text before or after."
    )
    messages = [{"role": "system", "content": system}]
    page = client.get_page(participant_url)

    while not page.is_finished:
        if page.is_wait_page:
            page = client.wait_for_page(page)
            continue

        if page.form_fields:
            prompt = _build_prompt(page)
            messages.append({"role": "user", "content": prompt})
            raw, answers = _get_valid_answers(messages, page.form_fields, model,
                                              api_key, temperature, seed)
            if answers:
                log.append({"page": _page_name(page), "prompt": prompt, "raw": raw, "answers": answers})
                messages.append({"role": "assistant", "content": json.dumps(answers)})
                page = client.submit(page, answers)
            else:
                log.append({"page": _page_name(page), "error": "no valid answers"})
                break
        else:
            if page.body_text.strip():
                messages.append({"role": "user", "content": page.body_text})
                messages.append({"role": "assistant", "content": "(noted)"})
            page = client.submit(page, {})

    return {"system_prompt": system, "log": log}


def run_batch(server_url: str, session_config: str, n: int,
              personas: list[str], model: str, api_key: str = None,
              rest_key: str = "test-rest-key",
              temperature: float = 1.0, seed: int = None) -> list[dict]:
    urls = OTreeClient.create_session(server_url, session_config, n, rest_key)

    results = [None] * n
    with ThreadPoolExecutor(max_workers=n) as pool:
        futures = {
            pool.submit(play, urls[i], personas[i], model, api_key,
                        temperature, seed): i
            for i in range(n)
        }
        for future in as_completed(futures):
            i = futures[future]
            try:
                results[i] = {"agent": f"bot_{i+1}", **future.result()}
            except Exception as e:
                results[i] = {"agent": f"bot_{i+1}", "error": str(e)}

    return results


def _build_prompt(page: PageData) -> str:
    parts = []
    if page.body_text:
        parts.append(page.body_text)
    for f in page.form_fields:
        label = f.label or f.name
        if f.choices:
            opts = ", ".join(f'"{d}"' for _, d in f.choices)
            parts.append(f'"{f.name}": {label} (choose one: {opts})')
        elif f.input_type == "number":
            bounds = f" ({f.min_value} to {f.max_value})" if f.min_value is not None and f.max_value is not None else ""
            parts.append(f'"{f.name}": {label}{bounds}')
        else:
            parts.append(f'"{f.name}": {label}')
    example = ", ".join(f'"{f.name}": ...' for f in page.form_fields)
    parts.append(f"Respond: {{{example}}}")
    return "\n".join(parts)


def _get_valid_answers(messages, fields, model, api_key, temperature=1.0, seed=None):
    for _ in range(MAX_RETRIES):
        text = openrouter.complete(messages, model, api_key, temperature, seed)
        cleaned, errors = _validate(_parse_json(text), fields)
        if not errors:
            return text, cleaned
        messages.append({"role": "assistant", "content": text})
        messages.append({"role": "user", "content": f"Errors: {errors}. JSON only."})
    return "", {}


def _parse_json(text: str) -> dict:
    if not text:
        return {}
    text = re.sub(r'```json?\s*', '', text)
    text = re.sub(r'```\s*', '', text).strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    start, end = text.find("{"), text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except (json.JSONDecodeError, TypeError):
            pass
    return {}


def _validate(answers: dict, fields: list[FormField]) -> tuple[dict, list[str]]:
    cleaned, errors = {}, []
    for f in fields:
        val = answers.get(f.name)
        if val is None:
            errors.append(f"missing: {f.name}")
        elif f.choices:
            valid = {v: v for v, _ in f.choices}
            display = {d.lower(): v for v, d in f.choices}
            s = str(val)
            if s in valid:
                cleaned[f.name] = s
            elif s.lower() in display:
                cleaned[f.name] = display[s.lower()]
            else:
                errors.append(f"{f.name}: invalid choice '{val}'")
        elif f.input_type == "number":
            try:
                num = float(val)
                cleaned[f.name] = int(num) if num == int(num) else num
            except (ValueError, TypeError):
                errors.append(f"{f.name}: not a number")
        else:
            cleaned[f.name] = str(val)
    return cleaned, errors


def _page_name(page: PageData) -> str:
    for p in reversed(page.url.rstrip("/").split("/")):
        if p and not p.isdigit():
            return p
    return page.url
