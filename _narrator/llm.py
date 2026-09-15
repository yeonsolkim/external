"""OpenAI Chat Completions over urllib — one function, retries, usage accounting."""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request

from .env import require

ENDPOINT = "https://api.openai.com/v1/chat/completions"
_usage_lock = threading.Lock()
USAGE = {"prompt": 0, "completion": 0, "calls": 0}


class LLMError(Exception):
    pass


def _reasoning_model(model: str) -> bool:
    return model.startswith(("gpt-5", "o1", "o3", "o4"))


def chat(system: str, user: str, model: str, max_tokens: int = 8000,
         reasoning: str = "", temperature: float = 0.2, timeout: int = 300) -> str:
    body: dict = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    if _reasoning_model(model):
        # Reasoning tokens count against the completion budget; leave room for them.
        body["max_completion_tokens"] = max_tokens * 4
        body["reasoning_effort"] = reasoning or "low"
    else:
        body["max_tokens"] = max_tokens
        body["temperature"] = temperature

    key = require("OPENAI_API_KEY")
    delay = 2.0
    for attempt in range(6):
        request = urllib.request.Request(
            ENDPOINT, data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"content-type": "application/json", "authorization": "Bearer " + key},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            text = error.read().decode("utf-8", "replace")
            if error.code == 400 and "reasoning_effort" in text and "reasoning_effort" in body:
                body.pop("reasoning_effort")
                continue
            if error.code in (429, 500, 502, 503, 504) and attempt < 5:
                time.sleep(delay)
                delay *= 2
                continue
            raise LLMError("%s %s: %s" % (model, error.code, text[:500]))
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt < 5:
                time.sleep(delay)
                delay *= 2
                continue
            raise LLMError("%s: %s" % (model, error))
        usage = data.get("usage") or {}
        with _usage_lock:
            USAGE["prompt"] += usage.get("prompt_tokens", 0)
            USAGE["completion"] += usage.get("completion_tokens", 0)
            USAGE["calls"] += 1
        choice = data["choices"][0]
        if choice.get("finish_reason") == "length":
            raise LLMError("%s: output cut off at max_tokens" % model)
        return (choice["message"]["content"] or "").strip()
    raise LLMError("%s: gave up after retries" % model)
