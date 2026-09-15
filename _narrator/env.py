"""Configuration from the environment, with an optional `.env` at the repository root.

dotenv semantics that bit us before: `KEY=value   # comment` strips the comment, quotes
win, and a `#` with no whitespace before it is kept (passwords contain them).
"""
from __future__ import annotations

import os
import re

_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")


def load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            match = _LINE.match(line)
            if not match or line.lstrip().startswith("#"):
                continue
            key, value = match.group(1), match.group(2)
            if value[:1] in ("'", '"') and value[-1:] == value[:1] and len(value) >= 2:
                value = value[1:-1]
            else:
                value = re.sub(r"\s+#.*$", "", value)
            os.environ.setdefault(key, value)


def require(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise SystemExit("%s is not set (export it, or put it in .env at the repository root)" % name)
    return value
