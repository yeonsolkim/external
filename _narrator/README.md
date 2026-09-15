# `_narrator` — narration for this site

Build-time pipeline: built post HTML → **skeleton** → script → audio → manifest + podcast
feed. Each stage's output is content-addressed by the previous stage's hash, so an edit
regenerates only what it touched. Stdlib Python only; run from the repository root.
The directory starts with `_` so Jekyll never publishes it.

| stage | status | input → output |
|---|---|---|
| 1 skeleton | **done** | `_site/**/*.html` → sectioned prose+math stream, hashed per section |
| 2 script | **done** | skeleton section + document glossary → lecture script (LLM), editable in `_narration/` |
| 3 voice | **done** | script → TTS → mastered mp3 with exact section offsets + ID3 chapters |
| 4 publish | **done** | mp3 → R2 (+ section-cache mirror), `_site/audio/<url>.json` per page, `podcast.xml`, in-page player |

## Stage 1 — skeleton

```bash
python3 -m _narrator skeleton _site/2026/07/31/2.-Compact-Sets.html     # readable stream
python3 -m _narrator skeleton https://yeonsolkim.com/2026/07/30/2.-Compact-Sets.html --json out.json
python3 -m _narrator skeleton _site                                      # one line per post
python3 -m unittest _narrator.tests.test_skeleton                        # 16 checks incl. a golden hash
```

**Input is the built HTML, not the Markdown** — what is narrated is exactly what is
published (Liquid resolved, plugin markup present). Local builds and the Actions build
produce byte-identical post bodies (verified), so hashes agree across machines.

**Stream format** (per section; the old extension's `extract.js` format, so the existing
spoken-math prompt applies unchanged):

```
Theorem 2.2.3. Let [MATH 1; TeX] M [/MATH] be a metric space and let [MATH 2; TeX] A\subseteq N\subseteq M [/MATH]. …

[MATH 17; TeX display] A\subseteq \bigcup_{k=1}^{n}V_{i_k}\tag{$\ast$} [/MATH]

Proof. … Therefore [MATH 43; TeX] A [/MATH] is compact in [MATH 44; TeX] M [/MATH]. [END PROOF]
```

- Math is numbered **per section**, so inserting an equation renumbers — and re-hashes —
  only that section.
- Trailing sentence punctuation inside inline math moves out: `\(A\subseteq M.\)` →
  `[MATH] A\subseteq M [/MATH].` The site's `math-inline-punctuated` spans (`\(A\).`,
  `\(k\)-cell`) keep their punctuation in the prose.
- QED becomes a cue: `<span data-environment-end="proof">` → `[END PROOF]`; a
  `\tag*{\(\square\)}` on a display equation is stripped and the cue follows the block;
  `\blacksquare` → `[END SUBPROOF]`. Real labels like `\tag{$\ast$}` survive.
- Lists render one item per line: `(1) …` (ordered, honours `start`) or `- …`.
- Figures → `[FIGURE: caption|alt]`, TikZ → `[DIAGRAM: title]`, tables → `[TABLE omitted]`,
  code ≥ 4 lines → `[CODE omitted]`, footnotes and citation markup dropped. Each is also a
  document-level warning so the summary shows which pages lose content.
- Normalisation happens in exactly one function (`normalize`): NFC, every whitespace run
  (including NBSP) → one space. It is part of the cache key; treat it as frozen.

**Sectioning rule.** A section opens at every heading (`h2`–`h6`) and at every numbered
environment paragraph (`<strong>Theorem 2.2.16.</strong> …`, kinds in `ENV_KINDS`;
unnumbered `<strong>Remark.</strong>` also counts, numbered by occurrence). The statement,
its proof, display equations and lists belong to it. The author's transitional prose
between two results is its own `prose` section: after a proof, every paragraph past the
QED; without a proof, the first paragraph that starts a new sentence in a new block (a
paragraph that finishes a display equation, or begins lowercase, still belongs to the
statement). Prose before the first section is `introduction`. A heading named
References/Bibliography is kept but `skip`ped. The name in parentheses after the label is
captured: `Theorem 2.2.20 (Heine–Borel theorem)`. A `prose` section is a cache unit; the
feed and player may fold it into the previous chapter for display.

Section ids: heading `id` as-is; environments `theorem-2-2-16`. Environments have **no
anchor in the HTML yet** (`anchor: null`) — the player and podcast chapters will need one,
which is a one-line change in the site's plugin when we get there.

**JSON** (`--json`): document `url`, `title`, `lang`, `scope`, `published`, `modified`,
`hash`, `math`, `words`, `warnings`, and `sections[]` with `id`, `title`, `kind`, `level`,
`label`, `name`, `anchor`, `skip`, `text`, `hash`, `math`, `words`, `has_proof`.

**Frozen by a test.** `tests/test_skeleton.py` pins the live *2.2. Compact Sets* page
(fixture fetched 2026-09-15): 33 sections / 32 narrated (11 of them `prose`) / 351
equations / 3 726 words / document hash `94b54ab2…`. If a change to this module moves that hash, every recording
would regenerate — bump `SKELETON_VERSION` and update the golden on purpose only.

## Stage 2 — script

```bash
python3 -m _narrator script  <post.html|URL> --dry-run          # the plan, spends nothing
python3 -m _narrator script  <post.html|URL>                    # writes _narration/<url>/*.md
python3 -m _narrator script  <post.html|URL> --only theorem-2-2-3 --force
python3 -m _narrator lecture <post.html|URL> --out-file lecture.md   # everything in reading order
python3 -m unittest _narrator.tests.test_script                 # bookkeeping, no network
```

`OPENAI_API_KEY` from the environment or `.env` at the repository root (gitignored).
Default model `gpt-5.5`; the lecture pass runs at `reasoning_effort: medium` (`--reasoning`),
the glossary at `low`. One post ≈ 75k input tokens, well under a dollar.

**What it writes** — one directory per post, keyed by the canonical URL path:

```
_narration/2026/07/30/2.-Compact-Sets/
  glossary.md            notation readings fixed for the whole document
  theorem-2-2-3.md       one lecture script per narrated section (front matter + text)
  prose-after-theorem-2-2-3.md
  index.json             reading order, provenance, current/edited flags (derived)
```

**The scripts are the source of truth for the voice stage, and you may edit them.** Each
file's front matter records `source` (the section's skeleton hash), `prompt`
(`PROMPT_VERSION`), `model`, and `body` (hash of the text as generated). On the next run:

| the section's text on the page | the file | result |
|---|---|---|
| unchanged | untouched | left alone |
| unchanged | edited by you | left alone — even after a prompt bump |
| changed | untouched | regenerated |
| changed | edited by you | **kept**, marked `stale: true`; fresh draft written to `<id>.new.md` |
| any | `--force` | regenerated, edited files still kept |

Editing is detected from the body hash, so there is no flag to remember. When the page
changes under a script you edited, resolve it one of three ways: keep yours —
`python3 -m _narrator script <post> --accept <id>` stamps it current (no LLM); take the
draft — move `<id>.new.md` over `<id>.md`; or merge into the draft and move it. Until then
the post is not re-published and the site keeps the previous audio. The glossary is
keyed by the document's set of distinct equations (prose edits never touch it), and a
glossary change does **not** cascade into existing scripts: a reviewed section does not
get worse because an equation was added elsewhere. `--force` re-reads with the new glossary.

**The prompt** (`prompts.py`, `lecture-v2`) writes a formal lecture: first person plural,
present tense, the author's order and wording, every equation in words, and nothing added
except what a lecturer needs to speak structure — "Theorem 2.2.20, the Heine–Borel
theorem.", "Proof.", "This completes the proof." for `[END PROOF]`, a lead-in for a display
equation, "We refer to this inclusion as star." after a labelled equation (named after the
sentence that contains it), list items by number. The notation glossary is passed to every
section so readings stay consistent; each entry is `symbol — spoken name (note)` — the
name is what is said, the note says when a role word ("the cover U") is needed, and
styled letters are named by role, never "bold x". Bump `PROMPT_VERSION` when a change
should regenerate the unedited scripts; leave it for changes that only matter going forward.

## Stage 3 — voice

```bash
python3 -m _narrator sample <post.html|URL> --section theorem-2-2-3 --voices cedar,marin,onyx,ash
python3 -m _narrator voice  <post.html|URL> --dry-run            # what would be synthesised
python3 -m _narrator voice  <post.html|URL> --voice cedar --artist "Yeonsol Kim" --album External
python3 -m unittest _narrator.tests.test_voice                   # no network, no ffmpeg
```

Needs `ffmpeg` on PATH (`brew install ffmpeg`) and the OpenAI key. Engine `gpt-4o-mini-tts`
(`--model`), default voice `cedar` (`--voice`); the engine gets `INSTRUCTIONS` — a formal
lecturer, measured pace — which is part of the cache key. Cost ≈ $0.015 per minute of audio;
*Compact Sets* is 21 min.

**What it writes:**

```
_audio/cache/<key>.flac + .json      one per section, lossless; key = AUDIO_VERSION | model |
                                     voice | instructions | script text
_audio/2026/07/30/2.-Compact-Sets.mp3    the page, 128 kbps mono 44.1 kHz, ID3 title/artist/
                                          album + CHAP chapters (ffmpeg writes them; verified)
_audio/2026/07/30/2.-Compact-Sets.json   manifest: every section with start/duration, and the
                                          chapter list
```

`_audio/` is gitignored — the cache is what makes re-assembly free; stage 4 will mirror it
to R2 so a lost disk does not mean paying for synthesis again.

**How the audio is made.** The script of a section is synthesised one paragraph at a time
(the API takes 4096 chars; a paragraph is also the natural unit of a pause), as raw PCM
(24 kHz, 16-bit, mono). Each piece has the engine's own leading/trailing silence trimmed
to 0.1 s, then pieces are joined with 0.6 s of silence between paragraphs (0.3 s inside a
split paragraph) and 1.2 s between sections. Offsets therefore come from sample counts and
are exact. The page is loudness-normalised in two passes (`loudnorm`, −16 LUFS, −1.5 dBTP,
linear gain so timing is untouched) and encoded once. Result labels are spelled out for
the engine before synthesis — "Theorem 2.2.3" → "Theorem 2 point 2 point 3" — so it can
never say "two two three".

**Chapters** are every section except transitional `prose`, which folds into the chapter
before it (the manifest still lists prose sections with their own offsets). The voice
stage refuses to build a page whose scripts are missing or out of date with the skeleton —
run `script` first.

## Stage 4 — publish

```bash
python3 -m _narrator publish _site --dry-run                  # state of every post, spends nothing
python3 -m _narrator publish _site/2026/07/30/2.-Compact-Sets.html
python3 -m _narrator publish _site --max-new-minutes 60       # everything (generates missing scripts)
python3 -m unittest discover -s _narrator/tests -t .          # 42 checks, no network
```

Runs **after** `jekyll build`, needs the bucket credentials and (for new posts) the OpenAI
key — environment or `.env`; `AUDIO_BASE_URL` or `narration.audio_url` in `_config.yml` is
the public base of the bucket. The store is any S3-compatible bucket (`store.py`, SigV4
pinned to AWS's vector; R2 verified). `--no-store` writes only the site files.

**Bucket layout** (under `S3_PREFIX` if set):

```
o/<page key>.mp3, o/<page key>.json      immutable, content-addressed — the web player
<url path>.mp3 / .json / .chapters.json  stable aliases — the podcast enclosure (guid never moves)
cache/<section key>.flac + .json         mirror of the section cache
```

Posts are processed **two at a time** (`--posts N`) with four sections in flight per post
(`--workers`), so one post's upload overlaps another's synthesis; the section cache is
written atomically and a key is synthesised at most once even when two posts race for it.
Output lines carry the post's slug when more than one post is being handled.

A post's `page_key` is its ordered section keys + `AUDIO_VERSION`. `publish` costs nothing
when `o/<page key>.json` already exists (one HEAD, then the site files are written); with
a local `_audio/` page it uploads; otherwise it pulls sections from the mirror, synthesises
only the missing ones (`--max-new-minutes` guards a post), assembles, uploads, mirrors, and
re-points the aliases with a server-side copy. A fresh checkout (CI, another machine) never
pays for audio it already has. Posts with no scripts get them generated (`--no-scripts`
forbids the LLM); posts under 40 words are skipped.

**Into the site, twice:** `audio/<url path>.json` (absolute audio URLs, sections, chapters)
and, when enabled, `podcast.xml` — written into the built `_site/` for the current deploy
AND into the source tree, which Jekyll copies on every build and which is committed. So a
local `jekyll serve` rebuild never loses them, and Pages serves them even when the
narration step does not run. `--no-source` skips the source-tree copy. (RSS + iTunes + Podcasting 2.0 chapters; episode = page,
guid = page URL, enclosure = stable alias, newest first).

**Which posts get audio.** Only posts whose front matter says `publish: true` (a checkbox in
Obsidian's properties panel; `templates/Jekyll-Post.md` seeds `publish: false`). The layout
turns it into `<meta name="narrate" content="true">`, the skeleton reads it, and `publish`
skips everything else — unchecking a post later removes its manifest and feed entry on the
next publish (nothing in the bucket is deleted). Unrelated to the flag, posts under 40 words
are skipped too.

**Site integration** (committed alongside): there is no player. `_includes/narration.html`
in `_layouts/post.html` leaves a hidden element carrying the manifest URL;
`assets/js/narration-player.js` fetches it and, only when it exists, makes the page itself
the control surface (`assets/css/narration.css`):

- **click or tap a statement's label** ("Theorem 3.1.1.") → that statement (and its proof)
  is read, then playback stops by itself;
- **click the post title** → the whole post from the start;
- **while playing, one click or tap anywhere** stops (Esc too). Drags and text selections
  are not clicks.

While playing, everything except the section being read fades to grey (labels, links and
equations included — post.css colours those explicitly), the page follows the reading unless
you scrolled in the last 8 s, a 2 px hairline along the top shows progress, and the lock
screen gets play/pause/seek. Labels are found through the ids `main.js` already gives
every labelled statement (`cursor: pointer` + dotted underline on hover mark them), and the
block map is rebuilt when `main.js` wraps statements into `<section>`s. A dropped stream is
reloaded at the same spot, three times, then playback stops cleanly. `_config.yml` gained
`timezone: UTC` (so local builds produce the same URLs as Pages) and a `narration:` block
(author, audio_url, voice, `podcast: true|false` — false drops `podcast.xml` and the head
link).

**CI** (`.github/workflows/pages.yml`): after the Jekyll build — tests, ffmpeg, `publish
_site --max-new-minutes 60`, then generated scripts are committed back to `_narration/`
(`[skip ci]`), together with `audio/**.json` and `podcast.xml`; needs `contents: write`. The steps are skipped until the `S3_BUCKET` secret
exists, so the site deploys as before in the meantime.

**Local run from the "Git Stage" service.** `~/Library/Services/Git Stage.workflow` now runs,
in this order: front-matter sync → stop the old `jekyll serve` → `jekyll build` →
`_narrator/bin/narrate-local.zsh` in the foreground (dry run; nothing to do → silent;
otherwise a notification, `publish _site --max-new-minutes 60`, a re-check, and a
notification with the outcome) → `git add .` → start `jekyll serve`. So when the service
finishes, the local site at :4000 already plays the new audio and everything, scripts and
manifests included, is staged for the push. A narration failure is reported and does not
stop the rest. Log: `~/Library/Logs/External-Jekyll/narration.log`. Automator's shell has a
bare PATH, so the script prepends `/opt/homebrew/bin` for ffmpeg and uses the system
Python 3.9. Unchanged site: the whole service takes ~6 s.

### Setting it up (once)

1. **Bucket.** Cloudflare R2 → create a bucket (e.g. `external-audio`) → Settings → Public
   access → connect the custom domain `audio.yeonsolkim.com` (the zone must be on Cloudflare;
   the `r2.dev` URL is fine for testing only) → an API token with Object Read & Write on it.
2. **Local `.env`** (gitignored): `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY_ID`,
   `S3_SECRET_ACCESS_KEY`, `OPENAI_API_KEY`. Set `narration.audio_url` in `_config.yml`.
3. **GitHub → Settings → Secrets**: the same five names.
4. **Per post**: tick `publish` in the front matter when the text is final, then
   `python3 -m _narrator publish _site --dry-run` and, without `--dry-run`, the real thing
   (≈ $0.30 of speech per 20-minute post; scripts are pennies). Review `_narration/**` as
   it lands — edits are honoured forever.
5. **Listen**: Apple Podcasts → File → Follow a Show by URL → `https://yeonsolkim.com/podcast.xml`
   (Overcast: + → Add URL). The in-page player appears on every published post.
6. A running `jekyll serve` must be restarted after the `_config.yml` change.

### Known limits (stages 1–4)

- Diagrams carry only their title (`Commutative diagram`); the TikZ source is not in the
  HTML. If diagrams should be described, the renderer plugin can stamp the source into a
  `data-` attribute and the skeleton will pick it up.
- Custom MathJax macros (`\lowparen`) are not expanded; the script stage will pass the
  macro list from `assets/js/mathjax-config.js` to the model.
- Table-only posts (Greek Alphabet, Timeline, Tenses) and empty stubs come out at 0 words;
  the publish stage should skip anything under a word threshold rather than narrate a cue.
- The mp3 encoder's ~25 ms priming delay is declared in the LAME header (`-write_xing 1`), so
  gapless-aware players land chapters exactly; others are a frame late, which is inaudible.
- Podcast apps that index the directory want square artwork (1400–3000 px); set
  `narration.cover` to add `<itunes:image>`. Not needed for following by URL.
- The stable alias carries `Cache-Control: max-age=300`; a re-narrated page reaches podcast
  apps on their next refresh, the web player immediately (it uses the immutable URL).
