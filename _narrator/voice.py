"""
Stage 3 — voice: lecture scripts -> one mastered mp3 per post, with exact section
offsets and ID3 chapters.

    _audio/cache/<key>.flac + .json     one per section; key = AUDIO_VERSION | tts model |
                                        voice | instructions | script text. Lossless, so a
                                        page can be re-assembled without re-synthesis.
    _audio/<url path>.mp3               the page: sections joined with silence, loudness
                                        normalised (EBU R128, -16 LUFS), 128 kbps mono
    _audio/<url path>.json              manifest: sections with start/duration, chapters

Synthesis is per paragraph (the API takes 4096 chars; a paragraph is also the natural
unit of a pause). Paragraphs are joined with PARA_GAP of silence, sections with
SECTION_GAP; leading/trailing silence from the engine is trimmed first so the gaps are
ours and the offsets are exact. Durations come from sample counts, not from probing.
"""
from __future__ import annotations

import array
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from . import tts
from .script import post_dir, read_md
from .skeleton import Skeleton

AUDIO_VERSION = 1
DEFAULT_TTS_MODEL = "gpt-4o-mini-tts"
DEFAULT_VOICE = "cedar"
INSTRUCTIONS = (
    "You are a university lecturer delivering a formal mathematics lecture to an audience "
    "that cannot see the board. Tone: calm, precise, authoritative and warm. Pace: measured, "
    "a little slower than conversation, with clear pauses at commas and at the end of every "
    "sentence, and a slight pause before and after each mathematical expression. Read "
    "letters that name variables as letters. Never rush a formula."
)
PARA_GAP = 0.6         # seconds between paragraphs
SENTENCE_GAP = 0.3     # between chunks of one long paragraph
SECTION_GAP = 1.2      # between sections
MAX_CHARS = 3500
TRIM_THRESHOLD = 250   # |sample| below this is silence (of 32767)
TRIM_KEEP = 0.10       # seconds of engine silence kept at each end
LOUDNESS = "I=-16:TP=-1.5:LRA=11"

SR = tts.SAMPLE_RATE
BPS = tts.BYTES_PER_SAMPLE


class VoiceError(Exception):
    pass


# ----------------------------------------------------------------------------- text
def canonical(body: str) -> str:
    return "\n".join(line.rstrip() for line in body.strip().split("\n"))


def spoken_labels(text: str) -> str:
    """'Theorem 2.2.3' -> 'Theorem 2 point 2 point 3', so the engine never says 'two two three'."""
    def dots(match: "re.Match") -> str:
        return match.group(1) + " point ".join(match.group(2).split("."))
    return re.sub(r"\b([A-Z][a-z]+ )(\d+(?:\.\d+)+)\b", dots, text)


def chunks(body: str) -> list:
    """-> [(text, gap_before_seconds)]: paragraphs, long ones split at sentence ends."""
    out = []
    for para in re.split(r"\n\s*\n", canonical(body)):
        para = re.sub(r"\s+", " ", para).strip()
        if not para:
            continue
        gap = PARA_GAP
        if len(para) <= MAX_CHARS:
            out.append((para, gap))
            continue
        buf = ""
        for sentence in re.split(r"(?<=[.!?])\s+", para):
            if buf and len(buf) + 1 + len(sentence) > MAX_CHARS:
                out.append((buf, gap))
                gap = SENTENCE_GAP
                buf = sentence
            else:
                buf = (buf + " " + sentence).strip()
        if buf:
            out.append((buf, gap))
    if out:
        out[0] = (out[0][0], 0.0)
    return out


def section_key(body: str, voice: str, model: str, instructions: str = INSTRUCTIONS) -> str:
    material = "|".join([str(AUDIO_VERSION), model, voice, instructions, canonical(body)])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def page_key(section_keys: list) -> str:
    """Identity of an assembled page: the ordered section audio plus the mastering version."""
    material = "page|%d|" % AUDIO_VERSION + "\n".join(section_keys)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------- pcm
def silence(seconds: float) -> bytes:
    return b"\x00" * (int(round(seconds * SR)) * BPS)


def trim(pcm: bytes) -> bytes:
    samples = array.array("h")
    samples.frombytes(pcm)
    n = len(samples)
    start, end = 0, n
    while start < n and abs(samples[start]) < TRIM_THRESHOLD:
        start += 1
    while end > start and abs(samples[end - 1]) < TRIM_THRESHOLD:
        end -= 1
    keep = int(TRIM_KEEP * SR)
    start = max(0, start - keep)
    end = min(n, end + keep)
    return samples[start:end].tobytes()


def seconds(pcm: bytes) -> float:
    return len(pcm) / (SR * BPS)


# ----------------------------------------------------------------------------- ffmpeg
def ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise VoiceError("ffmpeg not found on PATH (brew install ffmpeg)")
    return path


def encode_flac(pcm: bytes, path: str) -> None:
    """Written to a temporary name and renamed, so a reader never sees a half-written file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".%d.tmp.flac" % os.getpid()
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                    "-i", "pipe:0", "-c:a", "flac", tmp], input=pcm, check=True)
    os.replace(tmp, path)


def decode_flac(path: str) -> bytes:
    result = subprocess.run([ffmpeg(), "-v", "error", "-i", path, "-f", "s16le", "-ar", str(SR),
                             "-ac", "1", "pipe:1"], capture_output=True, check=True)
    return result.stdout


def measure_loudness(pcm_path: str) -> dict:
    result = subprocess.run(
        [ffmpeg(), "-hide_banner", "-nostats", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", pcm_path,
         "-af", "loudnorm=%s:print_format=json" % LOUDNESS, "-f", "null", "-"],
        capture_output=True, text=True, check=True)
    match = re.search(r"\{.*\}", result.stderr, re.S)
    if not match:
        raise VoiceError("loudnorm measurement produced no JSON:\n" + result.stderr[-800:])
    return json.loads(match.group(0))


def encode_mp3(pcm_path: str, metadata_path: str, out_path: str, measured: dict) -> None:
    filt = "loudnorm=%s:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true" % (
        LOUDNESS, measured["input_i"], measured["input_tp"], measured["input_lra"],
        measured["input_thresh"], measured["target_offset"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    subprocess.run(
        [ffmpeg(), "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", pcm_path,
         "-i", metadata_path, "-map_metadata", "1", "-map_chapters", "1",
         "-af", filt, "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k",
         "-id3v2_version", "3", "-write_xing", "1", out_path],
        check=True)


def ffmetadata(title: str, artist: str, album: str, chapters: list) -> str:
    def esc(value: str) -> str:
        return re.sub(r"([=;#\\\n])", r"\\\1", value)
    lines = [";FFMETADATA1", "title=" + esc(title), "artist=" + esc(artist), "album=" + esc(album),
             "genre=Speech"]
    for chapter in chapters:
        lines += ["[CHAPTER]", "TIMEBASE=1/1000", "START=%d" % int(round(chapter["start"] * 1000)),
                  "END=%d" % int(round(chapter["end"] * 1000)), "title=" + esc(chapter["title"])]
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------- sections
def synth_section(body: str, voice: str, model: str, instructions: str = INSTRUCTIONS, log=print) -> tuple:
    """-> (pcm, parts) where parts = [{"chars", "start", "duration"}] within the section."""
    pieces = chunks(spoken_labels(body))
    pcm = b""
    parts = []
    for text, gap in pieces:
        audio = trim(tts.synth(text, voice=voice, model=model, instructions=instructions))
        if pcm:
            pcm += silence(gap)
        parts.append({"chars": len(text), "start": round(seconds(pcm), 3), "duration": round(seconds(audio), 3)})
        pcm += audio
    return pcm, parts


def cached_section(cache_dir: str, key: str) -> Optional[dict]:
    meta_path = os.path.join(cache_dir, key + ".json")
    flac_path = os.path.join(cache_dir, key + ".flac")
    if os.path.exists(meta_path) and os.path.exists(flac_path):
        with open(meta_path, encoding="utf-8") as handle:
            return json.load(handle)
    return None


_key_locks: dict = {}
_key_locks_guard = threading.Lock()


def _lock_for(key: str) -> threading.Lock:
    with _key_locks_guard:
        return _key_locks.setdefault(key, threading.Lock())


def ensure_section(cache_dir: str, section_id: str, body: str, voice: str, model: str, log=print) -> dict:
    key = section_key(body, voice, model)
    meta = cached_section(cache_dir, key)
    if meta:
        return meta
    with _lock_for(key):                      # posts are processed in parallel; pay for a key once
        meta = cached_section(cache_dir, key)
        if meta:
            return meta
        pcm, parts = synth_section(body, voice, model, log=log)
        encode_flac(pcm, os.path.join(cache_dir, key + ".flac"))
        meta = {"key": key, "section": section_id, "voice": voice, "model": model,
                "duration": round(seconds(pcm), 3), "chars": sum(p["chars"] for p in parts), "parts": parts}
        tmp = os.path.join(cache_dir, key + ".json.tmp")
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(meta, handle, indent=2)
        os.replace(tmp, os.path.join(cache_dir, key + ".json"))
    log("  synthesised %-40s %6.1fs  %d chars" % (section_id, meta["duration"], meta["chars"]))
    return meta


# ----------------------------------------------------------------------------- pages
def scripts_for(skel: Skeleton, narration_root: str) -> list:
    """[(section, body)] in reading order; refuses to build a page with holes."""
    directory = post_dir(narration_root, skel)
    out = []
    missing, stale = [], []
    for section in skel.sections:
        if section.skip or (section.words == 0 and section.math == 0):
            continue
        meta, body = read_md(os.path.join(directory, section.id + ".md"))
        if not body:
            missing.append(section.id)
        elif meta.get("source") != section.hash:
            stale.append(section.id)
        out.append((section, body))
    if missing:
        raise VoiceError("no script for: %s — run `script` first" % ", ".join(missing))
    if stale:
        raise VoiceError("scripts out of date with the page: %s — run `script` first" % ", ".join(stale))
    return out


def ensure_sections(scripts: list, cache_dir: str, voice: str, model: str, workers: int = 4,
                    fetch=None, log=print) -> list:
    """Make every section's audio exist in the local cache; returns the cache metas in order.

    `fetch(key) -> bool` may pull a section from a remote mirror before synthesis is paid for.
    """
    keys = [(section, body, section_key(body, voice, model)) for section, body in scripts]

    def work(item: tuple) -> dict:
        section, body, key = item
        if cached_section(cache_dir, key) is None and fetch is not None and fetch(key):
            log("  fetched     %-40s from the mirror" % section.id)
        return ensure_section(cache_dir, section.id, body, voice, model, log=log)

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        return list(pool.map(work, keys))


def assemble_page(skel: Skeleton, scripts: list, metas: list, cache_dir: str, out_mp3: str,
                  out_json: str, voice: str, model: str, artist: str = "", album: str = "",
                  log=print) -> dict:
    """Sections (from the cache) -> mastered mp3 + manifest. No network."""
    page = b""
    entries = []
    for (section, _body), meta in zip(scripts, metas):
        pcm = decode_flac(os.path.join(cache_dir, meta["key"] + ".flac"))
        if page:
            page += silence(SECTION_GAP)
        start = seconds(page)
        page += pcm
        entries.append({
            "id": section.id, "title": section.title, "kind": section.kind, "level": section.level,
            "start": round(start, 3), "duration": round(seconds(pcm), 3),
            "source": section.hash, "audio": meta["key"],
        })
    total = seconds(page)

    # Chapters: every section except transitional prose, which folds into the one before.
    chapters = []
    for entry in entries:
        if entry["kind"] == "prose" and chapters:
            continue
        chapters.append({"id": entry["id"], "title": entry["title"], "start": entry["start"]})
    for i, chapter in enumerate(chapters):
        chapter["end"] = chapters[i + 1]["start"] if i + 1 < len(chapters) else round(total, 3)

    with tempfile.TemporaryDirectory() as tmp:
        pcm_path = os.path.join(tmp, "page.pcm")
        with open(pcm_path, "wb") as handle:
            handle.write(page)
        meta_path = os.path.join(tmp, "chapters.ffmeta")
        with open(meta_path, "w", encoding="utf-8") as handle:
            handle.write(ffmetadata(skel.title, artist, album, chapters))
        log("mastering %.1f min: loudness pass 1" % (total / 60))
        measured = measure_loudness(pcm_path)
        log("  measured %s LUFS, true peak %s dBTP -> encoding mp3" % (measured["input_i"], measured["input_tp"]))
        encode_mp3(pcm_path, meta_path, out_mp3, measured)

    manifest = {
        "url": skel.url, "title": skel.title, "lang": skel.lang,
        "page_key": page_key([m["key"] for m in metas]),
        "audio": os.path.basename(out_mp3), "duration": round(total, 3), "bytes": os.path.getsize(out_mp3),
        "voice": voice, "model": model, "audio_version": AUDIO_VERSION,
        "skeleton_hash": skel.hash, "sections": entries, "chapters": chapters,
    }
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
    log("wrote %s (%.1f MB, %.1f min, %d chapters) and %s" % (
        out_mp3, manifest["bytes"] / 1e6, total / 60, len(chapters), out_json))
    return manifest


def page_paths(skel: Skeleton, audio_root: str) -> tuple:
    key = re.sub(r"\.html?$", "", skel.url.strip("/"))
    return os.path.join(audio_root, key + ".mp3"), os.path.join(audio_root, key + ".json")


def run(skel: Skeleton, narration_root: str = "_narration", audio_root: str = "_audio",
        voice: str = DEFAULT_VOICE, model: str = DEFAULT_TTS_MODEL, workers: int = 4,
        dry_run: bool = False, artist: str = "", album: str = "", log=print) -> dict:
    """Local-only: scripts -> cache -> mp3 under _audio/. The publish stage adds the mirror."""
    scripts = scripts_for(skel, narration_root)
    cache_dir = os.path.join(audio_root, "cache")
    todo = [(s, b) for s, b in scripts if not cached_section(cache_dir, section_key(b, voice, model))]
    chars = sum(len(b) for _, b in todo)
    log("%s: %d sections, %d to synthesise (%d chars ≈ %.0f min of speech) with %s/%s" % (
        skel.title, len(scripts), len(todo), chars, chars / 900.0, model, voice))
    if dry_run:
        return {}
    metas = ensure_sections(scripts, cache_dir, voice, model, workers=workers, log=log)
    out_mp3, out_json = page_paths(skel, audio_root)
    manifest = assemble_page(skel, scripts, metas, cache_dir, out_mp3, out_json, voice, model,
                             artist=artist, album=album, log=log)
    log("tts usage this run: %d calls, %d chars, %.1f min of audio" % (
        tts.USAGE["calls"], tts.USAGE["chars"], tts.USAGE["seconds"] / 60))
    return manifest


def samples(text: str, voices: list, model: str, out_dir: str, log=print) -> list:
    """One short mp3 per voice, for choosing by ear."""
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for voice in voices:
        pcm = b""
        for piece, gap in chunks(spoken_labels(text)):
            if pcm:
                pcm += silence(gap)
            pcm += trim(tts.synth(piece, voice=voice, model=model, instructions=INSTRUCTIONS))
        path = os.path.join(out_dir, "%s.mp3" % voice)
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                        "-i", "pipe:0", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "128k", path],
                       input=pcm, check=True)
        log("  %-8s %5.1fs  %s" % (voice, seconds(pcm), path))
        paths.append(path)
    return paths
