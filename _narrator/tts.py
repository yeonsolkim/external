"""OpenAI text-to-speech over urllib. Returns raw PCM: 24 kHz, 16-bit signed LE, mono."""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request

from .env import require

ENDPOINT = "https://api.openai.com/v1/audio/speech"
SAMPLE_RATE = 24000
BYTES_PER_SAMPLE = 2
MAX_INPUT_CHARS = 4096
_lock = threading.Lock()
USAGE = {"chars": 0, "calls": 0, "seconds": 0.0}


class TTSError(Exception):
    pass


def synth(text: str, voice: str, model: str, instructions: str = "", timeout: int = 180) -> bytes:
    if len(text) > MAX_INPUT_CHARS:
        raise TTSError("input of %d chars exceeds the %d limit" % (len(text), MAX_INPUT_CHARS))
    body = {"model": model, "input": text, "voice": voice, "response_format": "pcm"}
    if instructions and model.startswith("gpt-4o-mini-tts"):
        body["instructions"] = instructions
    key = require("OPENAI_API_KEY")
    delay = 2.0
    for attempt in range(6):
        request = urllib.request.Request(
            ENDPOINT, data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"content-type": "application/json", "authorization": "Bearer " + key},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                pcm = response.read()
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")
            if error.code in (429, 500, 502, 503, 504) and attempt < 5:
                time.sleep(delay)
                delay *= 2
                continue
            raise TTSError("%s %s: %s" % (model, error.code, detail[:400]))
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt < 5:
                time.sleep(delay)
                delay *= 2
                continue
            raise TTSError("%s: %s" % (model, error))
        if len(pcm) % BYTES_PER_SAMPLE:
            pcm = pcm[:-1]
        with _lock:
            USAGE["chars"] += len(text)
            USAGE["calls"] += 1
            USAGE["seconds"] += len(pcm) / (SAMPLE_RATE * BYTES_PER_SAMPLE)
        return pcm
    raise TTSError("%s: gave up after retries" % model)
