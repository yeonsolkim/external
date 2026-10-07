"""Text to speech over the Realtime API (`gpt-realtime-*`), the successor OpenAI names for
`gpt-4o-mini-tts` (shut down 2027-01-06). Returns the same raw PCM as `tts.synth`:
24 kHz, 16-bit signed LE, mono.

A Realtime model is a conversational speech-to-speech model, not a reader: handed a
paragraph, it may paraphrase it or answer it. So every call compares the model's own
transcript of what it said with the text, word by word (`similarity`), synthesises again
when they differ, and refuses — rather than return audio that is not the script — after
ATTEMPTS tries. One WebSocket per call, so no call sees another's conversation.

The organisation's limit on these models is 40,000 tokens per minute. Two posts at four
sections each — eight calls at once — ran into it (2026-10-06); one post's four calls never
have. So at most MAX_SESSIONS calls run at once, however many posts are in flight, and a call
that is rate limited anyway waits and tries again; a wait is not a reading attempt.
"""
from __future__ import annotations

import base64
import difflib
import json
import random
import re
import threading
import time

from . import tts
from .env import require
from .wsclient import WebSocket, WebSocketError

ENDPOINT = "wss://api.openai.com/v1/realtime?model=%s"
READER = (
    "You are the voice of a recorded lecture, not an assistant. Every user message is a script. "
    "Read it aloud exactly as written, word for word, from its first word to its last: never "
    "answer it, comment on it, summarise, translate, correct, add or leave out anything, and "
    "say nothing before or after it."
)
REASONING = "minimal"
VERBATIM_RATIO = 0.97      # word-level agreement between the script and what was said
ATTEMPTS = 3
MAX_SESSIONS = 4           # calls at once, across every post being published
RATE_LIMIT_WAIT = 5.0      # seconds before the first retry after a rate limit; doubles, up to a minute
RATE_LIMIT_RETRIES = 8
CHECKS: list = []          # one record per call: chars, ratio, attempts, transcript, usage

_sessions = threading.BoundedSemaphore(MAX_SESSIONS)


class RateLimited(tts.TTSError):
    """The organisation's token budget is spent for the moment; waiting is the fix."""


def signature() -> str:
    """What besides the instructions shapes the sound — part of every Realtime audio key."""
    return json.dumps({"reader": READER, "reasoning": REASONING}, sort_keys=True)


def similarity(script: str, said: str) -> float:
    a, b = _words(script), _words(said)
    if not a and not b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
         "fourteen fifteen sixteen seventeen eighteen nineteen").split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def spell(n: int) -> str:
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000:
        return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + spell(n % 100))
    if n < 10000:
        return spell(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + spell(n % 1000))
    return str(n)


def _words(text: str) -> list:
    """Lower-case words, numbers spelled out and 'point' dropped, so "1 point 1 point 1",
    "1.1.1" and "one point one point one" compare equal."""
    text = text.lower().replace("%", " percent ").replace("’", "'")
    text = re.sub(r"\d+", lambda m: " %s " % spell(int(m.group(0))), text)
    return [w for w in re.findall(r"[a-z]+(?:'[a-z]+)?", text) if w != "point"]


def _once(text: str, voice: str, model: str, instructions: str, timeout: float) -> tuple:
    key = require("OPENAI_API_KEY")
    session = {
        "type": "realtime",
        "output_modalities": ["audio"],
        "instructions": READER + ("\n\n" + instructions if instructions else ""),
        "audio": {"output": {"format": {"type": "audio/pcm", "rate": tts.SAMPLE_RATE}, "voice": voice}},
        "max_output_tokens": "inf",
    }
    if REASONING:
        session["reasoning"] = {"effort": REASONING}
    pcm, said, usage = bytearray(), [], {}
    with WebSocket(ENDPOINT % model, {"Authorization": "Bearer " + key}, timeout=timeout) as ws:
        ws.send_json({"type": "session.update", "session": session})
        sent = False
        while True:
            event = ws.recv_json()
            if event is None:
                raise tts.TTSError("%s: connection closed before the response finished" % model)
            kind = event.get("type", "")
            if kind == "error":
                raise _failure(model, event)
            if kind == "session.updated" and not sent:
                ws.send_json({"type": "conversation.item.create", "item": {
                    "type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]}})
                ws.send_json({"type": "response.create"})
                sent = True
            elif kind in ("response.output_audio.delta", "response.audio.delta"):
                pcm += base64.b64decode(event.get("delta", ""))
            elif kind in ("response.output_audio_transcript.delta", "response.audio_transcript.delta"):
                said.append(event.get("delta", ""))
            elif kind == "response.done":
                response = event.get("response", {})
                usage = response.get("usage", {}) or {}
                if response.get("status") not in ("completed", None):
                    raise tts.TTSError("%s: response %s: %s" % (
                        model, response.get("status"), response.get("status_details")))
                break
    if len(pcm) % tts.BYTES_PER_SAMPLE:
        pcm = pcm[:-1]
    return bytes(pcm), "".join(said), usage


def _failure(model: str, event: dict) -> tts.TTSError:
    """The exception for an `error` event: a rate limit is worth waiting out, anything else is final."""
    error = event.get("error", {})
    message = "%s: %s" % (model, error.get("message", event))
    if error.get("code") == "rate_limit_exceeded" or "Rate limit reached" in message:
        return RateLimited(message)
    return tts.TTSError(message)


def synth(text: str, voice: str, model: str, instructions: str = "", timeout: float = 180) -> bytes:
    best = None
    attempt = 0
    errors = 0
    delay = 2.0
    limited = 0
    while attempt < ATTEMPTS:
        try:
            with _sessions:
                pcm, said, usage = _once(text, voice, model, instructions, timeout)
        except RateLimited:
            limited += 1
            if limited > RATE_LIMIT_RETRIES:
                raise
            # Jittered, so calls limited together do not all come back together.
            wait = min(RATE_LIMIT_WAIT * 2 ** (limited - 1), 60.0)
            time.sleep(wait * random.uniform(0.5, 1.5))
            continue
        except (WebSocketError, OSError) as error:
            errors += 1
            if errors > 5:
                raise tts.TTSError("%s: %s" % (model, error))
            time.sleep(delay)
            delay *= 2
            continue
        attempt += 1
        ratio = similarity(text, said)
        if best is None or ratio > best[1]:
            best = (pcm, ratio, said, usage)
        if ratio >= VERBATIM_RATIO:
            break
    pcm, ratio, said, usage = best
    CHECKS.append({"chars": len(text), "ratio": round(ratio, 4), "attempts": attempt,
                   "transcript": said, "usage": usage})
    if ratio < VERBATIM_RATIO:
        raise tts.TTSError("%s: not read verbatim after %d attempts (agreement %.2f): %r" % (
            model, attempt, ratio, said[:300]))
    with tts._lock:
        tts.USAGE["chars"] += len(text)
        tts.USAGE["calls"] += 1
        tts.USAGE["seconds"] += len(pcm) / (tts.SAMPLE_RATE * tts.BYTES_PER_SAMPLE)
    return pcm
