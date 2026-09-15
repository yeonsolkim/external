#!/bin/zsh
# Local narration for the "Git Stage" service: right after `jekyll build`, publish every post
# marked `publish: true`, stage the outputs (_narration/, audio/, podcast.xml) and notify —
# so the local site carries the audio before the push. Runs in the foreground; everything
# goes to the log.
#
#   /bin/zsh _narrator/bin/narrate-local.zsh [repo] [log]
set -uo pipefail

repo="${1:-$HOME/External}"
log="${2:-$HOME/Library/Logs/External-Jekyll/narration.log}"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"       # ffmpeg lives in Homebrew
pattern='synthesise|assemble|no scripts yet|scripts out of date'

notify() { /usr/bin/osascript -e "display notification \"$1\" with title \"Narration\"" >/dev/null 2>&1 || true; }

cd "$repo" || exit 1
mkdir -p "${log:h}"
{
  print -- "==== $(date '+%F %T') narration"
  if [[ ! -f .env ]]; then
    print -- "no .env in the repo — skipped"
    exit 0
  fi
  if [[ ! -d _site ]]; then
    print -- "no _site — build first"
    exit 1
  fi

  plan=$(python3 -m _narrator publish _site --dry-run 2>&1); rc=$?
  print -r -- "$plan"
  if (( rc != 0 )); then
    notify "Narration check failed — see narration.log"
    exit 1
  fi
  todo=$(print -r -- "$plan" | /usr/bin/grep -cE "$pattern" || true)
  if (( todo == 0 )); then
    print -- "up to date"
    exit 0
  fi

  notify "Narrating $todo post(s) — a new post takes a few minutes"
  python3 -m _narrator publish _site --max-new-minutes 60; rc=$?
  remaining=$(python3 -m _narrator publish _site --dry-run 2>&1 | /usr/bin/grep -E "$pattern" || true)
  git add _narration audio podcast.xml 2>/dev/null || true

  if (( rc != 0 )); then
    notify "Narration failed — see narration.log"
    exit 1
  fi
  if [[ -n "$remaining" ]]; then
    print -r -- "still pending:"
    print -r -- "$remaining"
    notify "Narration needs attention (edited script?) — see narration.log"
    exit 1
  fi
  notify "Audio published and staged"
  print -- "done"
} >>"$log" 2>&1
