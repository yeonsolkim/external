#!/usr/bin/env python3
"""
Teach the macOS spelling dictionary the words in scripts/spelling_words.txt: Learn Spelling
for the whole list at once.

    python3 scripts/learn_spelling.py            learn the listed words the dictionary lacks
    python3 scripts/learn_spelling.py --dry-run  only list them
    python3 scripts/learn_spelling.py --forget   unlearn every listed word

The words go into the macOS user dictionary, as Learn Spelling in any app does, and count
wherever the macOS spell checker does: in other apps, and in scripts/check_spelling.py.
Run it again after adding words to the list; what the dictionary already knows is left alone.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import unicodedata

from check_spelling import system_misspelled


WORDS_FILE = Path(__file__).with_name("spelling_words.txt")

# "learn" teaches every word; "forget" unlearns those that were learned. Prints the words it changed.
DICTIONARY_JS = r"""
ObjC.import('AppKit');
function run(argv) {
  const checker = $.NSSpellChecker.sharedSpellChecker;
  const [action, ...words] = argv;
  return words.filter(word => {
    if (action === 'learn') {
      checker.learnWord($(word));
      return true;
    }
    if (!checker.hasLearnedWord($(word))) return false;
    checker.unlearnWord($(word));
    return true;
  }).join('\n');
}
"""


def listed_words(path: Path = WORDS_FILE) -> list[str]:
    words = (line.split("#", 1)[0].strip() for line in path.read_text(encoding="utf-8").splitlines())
    return list(dict.fromkeys(unicodedata.normalize("NFC", word) for word in words if word))


def change_dictionary(action: str, words: list[str]) -> list[str]:
    if not words:
        return []

    result = subprocess.run(
        ["/usr/bin/osascript", "-l", "JavaScript", "-", action, *words],
        input=DICTIONARY_JS,
        capture_output=True,
        encoding="utf-8",
        timeout=60,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser(description="Teach the macOS spelling dictionary the listed words.")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--dry-run", action="store_true", help="only list the words it would learn")
    action.add_argument("--forget", action="store_true", help="unlearn every listed word")
    args = parser.parse_args()

    words = listed_words()
    try:
        if args.forget:
            print(f"Unlearned {len(change_dictionary('forget', words))} word(s).")
            return 0

        missing = list(system_misspelled(words))
        if args.dry_run:
            print("\n".join(missing + [f"{len(missing)} of {len(words)} listed word(s) to learn."]))
            return 0

        change_dictionary("learn", missing)
        still_missing = list(system_misspelled(missing))
    except subprocess.CalledProcessError as error:
        print(f"spelling dictionary unavailable: {error.stderr.strip()}", file=sys.stderr)
        return 1
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"spelling dictionary unavailable: {error}", file=sys.stderr)
        return 1

    print(f"Learned {len(missing) - len(still_missing)} word(s); the dictionary knew the other {len(words) - len(missing)}.")
    if still_missing:
        print(f"Still unknown: {', '.join(still_missing)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
