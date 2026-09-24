"""
    python3 -m _narrator skeleton <post.html | URL>  [--json out.json] [--text out.txt]
    python3 -m _narrator skeleton _site               [--json out-dir]
    python3 -m _narrator script   <post.html | URL>  [--dry-run] [--force] [--only id,id] [--model M]
    python3 -m _narrator lecture  <post.html | URL>  [--out file]     # assembled script, for review
    python3 -m _narrator voice    <post.html | URL>  [--voice V] [--dry-run]   # scripts -> _audio/<url>.mp3 + .json
    python3 -m _narrator sample   <post.html | URL>  --section theorem-2-2-3 [--voices a,b,c]
    python3 -m _narrator publish  <post.html | URL | _site> [--site _site] [--dry-run] [--max-new-minutes 30]

A single post prints the readable skeleton (the stream the script stage will see);
a directory prints one summary line per post. `script` writes editable per-section
scripts under _narration/. Run from the repository root; OPENAI_API_KEY from the
environment or .env.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from .env import load_dotenv
from .skeleton import SkeletonError, build, render_text


def read_source(path: str) -> str:
    if path.startswith(("http://", "https://")):
        with urllib.request.urlopen(path, timeout=30) as response:
            return response.read().decode("utf-8")
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def find_posts(directory: str) -> list:
    posts = []
    for dirpath, _dirnames, filenames in os.walk(directory):
        for name in filenames:
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8", errors="replace") as handle:
                head = handle.read(200_000)
            if '<article class="post"' in head:
                posts.append(path)
    return sorted(posts)


def cmd_skeleton(args: argparse.Namespace) -> int:
    if os.path.isdir(args.source):
        return summarize(args)
    skel = build(read_source(args.source), args.source)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(skel.to_dict(), handle, ensure_ascii=False, indent=2)
    text = render_text(skel)
    if args.text:
        with open(args.text, "w", encoding="utf-8") as handle:
            handle.write(text)
    if not args.text or args.verbose:
        sys.stdout.write(text)
    return 0


def summarize(args: argparse.Namespace) -> int:
    posts = find_posts(args.source)
    if args.json:
        os.makedirs(args.json, exist_ok=True)
    print("%-52s %5s %5s %6s  %s" % ("url", "sect", "math", "words", "warnings"))
    total_words = 0
    for path in posts:
        try:
            skel = build(read_source(path), path)
        except SkeletonError as error:
            print("%-52s  !! %s" % (path, error))
            continue
        total_words += skel.words
        print("%-52s %5d %5d %6d  %s" % (
            skel.url[:52], sum(1 for s in skel.sections if not s.skip), skel.math, skel.words,
            "; ".join(skel.warnings)))
        if args.json:
            name = skel.url.strip("/").replace("/", "__").replace(".html", "") or "index"
            with open(os.path.join(args.json, name + ".json"), "w", encoding="utf-8") as handle:
                json.dump(skel.to_dict(), handle, ensure_ascii=False, indent=2)
    print("%d posts, %d words (~%d min at 150 wpm, before math)" % (len(posts), total_words, total_words // 150))
    return 0


def cmd_script(args: argparse.Namespace) -> int:
    from . import script as stage2
    load_dotenv()
    skel = build(read_source(args.source), args.source)
    out_dir = stage2.post_dir(args.out, skel)
    if args.accept:
        stage2.accept(skel, out_dir, set(x.strip() for x in args.accept.split(",")))
        return 0
    only = set(x.strip() for x in args.only.split(",")) if args.only else None
    stage2.run(skel, out_dir, model=args.model, force=args.force, only=only,
               dry_run=args.dry_run, workers=args.workers, reasoning=args.reasoning)
    return 0


def cmd_lecture(args: argparse.Namespace) -> int:
    from . import script as stage2
    skel = build(read_source(args.source), args.source)
    text = "# %s\n\n" % skel.title + stage2.assemble(skel, stage2.post_dir(args.out, skel))
    if args.out_file:
        with open(args.out_file, "w", encoding="utf-8") as handle:
            handle.write(text)
        print("wrote %s" % args.out_file)
    else:
        sys.stdout.write(text)
    return 0


def cmd_voice(args: argparse.Namespace) -> int:
    from . import voice as stage3
    load_dotenv()
    skel = build(read_source(args.source), args.source)
    try:
        stage3.run(skel, narration_root=args.narration, audio_root=args.audio, voice=args.voice,
                   model=args.model, workers=args.workers, dry_run=args.dry_run,
                   artist=args.artist, album=args.album)
    except stage3.VoiceError as error:
        print("error: %s" % error, file=sys.stderr)
        return 1
    return 0


def cmd_sample(args: argparse.Namespace) -> int:
    from . import script as stage2, voice as stage3
    load_dotenv()
    skel = build(read_source(args.source), args.source)
    _meta, body = stage2.read_md(os.path.join(stage2.post_dir(args.narration, skel), args.section + ".md"))
    if not body:
        print("error: no script for section %s" % args.section, file=sys.stderr)
        return 1
    text = body.strip()[:args.chars]
    text = text[:text.rfind(".") + 1] or text
    print("sampling %d chars of %s with %s:" % (len(text), args.section, args.model))
    stage3.samples(text, [v.strip() for v in args.voices.split(",")], args.model,
                   os.path.join(args.audio, "samples"))
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    from . import publish as stage4, script as stage2, siteconfig
    from .store import Store, StoreError
    load_dotenv()
    cfg = siteconfig.load()
    if not cfg["site_url"]:
        print("error: _config.yml has no `url`", file=sys.stderr)
        return 1
    base_url = cfg["audio_url"]
    if not base_url:
        print("error: set AUDIO_BASE_URL (or narration.audio_url in _config.yml) — the public base of the bucket",
              file=sys.stderr)
        return 1
    store = None if args.no_store else Store.from_env()
    voice = args.voice or cfg["voice"] or "cedar"
    pub = stage4.Publisher(store, base_url, args.site, cfg, narration_root=args.narration,
                           audio_root=args.audio, voice=voice, model=args.model, workers=args.workers,
                           source_dir=None if args.no_source else ".")
    sources = find_posts(args.source) if os.path.isdir(args.source) else [args.source]
    print_lock = threading.Lock()

    def say(prefix: str, message: str) -> None:
        with print_lock:
            print((prefix + message) if message.startswith("  ") or not prefix else prefix + message)

    def one(source: str) -> bool:
        """Publish one post; returns False on a failure worth reporting."""
        try:
            skel = build(read_source(source), source)
        except SkeletonError as error:
            say("", "  !! %s" % error)
            return True
        tag = "[%s] " % os.path.basename(skel.url).replace(".html", "")[:28] if len(sources) > 1 else ""
        log = lambda m: say(tag, m)
        state = pub.plan(skel)["state"]
        if state == "scripts" and not args.no_scripts and not args.dry_run and skel.words >= stage4.MIN_WORDS:
            log("%-50s generating scripts" % skel.url)
            stage2.run(skel, stage2.post_dir(args.narration, skel), model=args.text_model, workers=args.workers,
                       log=lambda m: log("  " + m))
        try:
            pub.publish_post(skel, max_new_minutes=args.max_new_minutes, dry_run=args.dry_run, log=log)
        except (stage4.PublishError, StoreError) as error:
            say(tag, "  !! %s" % error)
            return False
        return True

    # Posts run a few at a time: one post's upload overlaps another's synthesis, and the
    # section cache makes it safe (atomic writes, one synthesis per key).
    posts_at_once = max(1, min(args.posts, len(sources)))
    if posts_at_once == 1 or args.dry_run:
        results = [one(source) for source in sources]
    else:
        with ThreadPoolExecutor(max_workers=posts_at_once) as pool:
            results = list(pool.map(one, sources))
    failures = results.count(False)
    if os.path.isdir(args.source):
        pub.prune_orphans(dry_run=args.dry_run)   # only a whole-site run knows which pages still exist
    if not args.dry_run:
        pub.write_feed()
    return 1 if failures else 0


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m _narrator", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("skeleton", help="built HTML -> sectioned prose+math stream")
    p.add_argument("source", help="a built post (.html), a URL, or the _site directory")
    p.add_argument("--json", help="write the skeleton as JSON (a directory when source is a directory)")
    p.add_argument("--text", help="write the readable rendering to this file instead of stdout")
    p.add_argument("-v", "--verbose", action="store_true", help="print even when --text is given")
    p.set_defaults(func=cmd_skeleton)

    p = sub.add_parser("script", help="skeleton -> lecture scripts under _narration/ (calls the LLM)")
    p.add_argument("source", help="a built post (.html) or a URL")
    p.add_argument("--out", default="_narration", help="root of the script tree (default _narration)")
    p.add_argument("--model", default=None, help="chat model (default: %s)" % "gpt-5.5")
    p.add_argument("--reasoning", default="medium", help="reasoning_effort for the lecture pass (default medium)")
    p.add_argument("--force", action="store_true", help="regenerate even when current (edited files still kept)")
    p.add_argument("--only", help="comma-separated section ids to (re)generate")
    p.add_argument("--accept", help="comma-separated section ids whose hand-edited script is now current (no LLM)")
    p.add_argument("--dry-run", action="store_true", help="print the plan, spend nothing")
    p.add_argument("--workers", type=int, default=4, help="parallel sections (default 4)")
    p.set_defaults(func=cmd_script)

    p = sub.add_parser("lecture", help="assemble the existing scripts of a post in reading order")
    p.add_argument("source", help="a built post (.html) or a URL")
    p.add_argument("--out", default="_narration", help="root of the script tree (default _narration)")
    p.add_argument("--out-file", dest="out_file", help="write here instead of stdout")
    p.set_defaults(func=cmd_lecture)

    p = sub.add_parser("voice", help="lecture scripts -> mastered mp3 + manifest (calls the TTS API)")
    p.add_argument("source", help="a built post (.html) or a URL")
    p.add_argument("--narration", default="_narration", help="root of the script tree")
    p.add_argument("--audio", default="_audio", help="root of the audio tree (default _audio)")
    p.add_argument("--voice", default="cedar", help="TTS voice (default cedar)")
    p.add_argument("--model", default="gpt-4o-mini-tts", help="TTS model (default gpt-4o-mini-tts)")
    p.add_argument("--workers", type=int, default=4, help="parallel sections (default 4)")
    p.add_argument("--artist", default="", help="ID3 artist")
    p.add_argument("--album", default="", help="ID3 album")
    p.add_argument("--dry-run", action="store_true", help="say what would be synthesised, spend nothing")
    p.set_defaults(func=cmd_voice)

    p = sub.add_parser("sample", help="render one section's opening in several voices, to choose by ear")
    p.add_argument("source", help="a built post (.html) or a URL")
    p.add_argument("--section", required=True, help="section id whose script to sample")
    p.add_argument("--voices", default="cedar,marin,onyx,ash", help="comma-separated voices")
    p.add_argument("--chars", type=int, default=700, help="how much of the script to read (default 700)")
    p.add_argument("--model", default="gpt-4o-mini-tts")
    p.add_argument("--narration", default="_narration")
    p.add_argument("--audio", default="_audio")
    p.set_defaults(func=cmd_sample)

    p = sub.add_parser("publish", help="audio -> bucket, manifests -> _site, podcast.xml")
    p.add_argument("source", help="a built post (.html), a URL, or the _site directory (every post)")
    p.add_argument("--site", default="_site", help="built site to write manifests + podcast.xml into")
    p.add_argument("--narration", default="_narration")
    p.add_argument("--audio", default="_audio")
    p.add_argument("--voice", default=None, help="TTS voice (default: narration.voice in _config.yml, else cedar)")
    p.add_argument("--model", default="gpt-4o-mini-tts", help="TTS model")
    p.add_argument("--text-model", dest="text_model", default="gpt-5.5", help="chat model for missing scripts")
    p.add_argument("--workers", type=int, default=4, help="parallel sections within a post (default 4)")
    p.add_argument("--posts", type=int, default=2, help="posts processed at the same time (default 2)")
    p.add_argument("--max-new-minutes", dest="max_new_minutes", type=float, default=30.0,
                   help="refuse to synthesise more than this much new speech for one post (default 30)")
    p.add_argument("--no-scripts", dest="no_scripts", action="store_true", help="never call the LLM; skip posts without scripts")
    p.add_argument("--no-store", dest="no_store", action="store_true", help="no bucket: only write site files")
    p.add_argument("--no-source", dest="no_source", action="store_true",
                   help="do not also write audio/*.json and podcast.xml into the source tree")
    p.add_argument("--dry-run", dest="dry_run", action="store_true", help="report the state of every post, spend nothing")
    p.set_defaults(func=cmd_publish)

    args = parser.parse_args(argv)
    if getattr(args, "model", None) is None and args.command == "script":
        from .script import DEFAULT_MODEL
        args.model = DEFAULT_MODEL
    try:
        return args.func(args)
    except SkeletonError as error:
        print("error: %s" % error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
