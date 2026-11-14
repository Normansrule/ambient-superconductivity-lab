"""Minimal, dependency-free BibTeX parser.

Handles ``@type{key, field = {value}, field = "value", field = 1990}``
with nested braces. ``@comment``, ``@preamble``, and ``@string`` blocks
are skipped. Field names are lower-cased; values keep their braces
stripped at the outer level only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

SKIPPED_TYPES = {"comment", "preamble", "string"}


@dataclass
class BibEntry:
    entry_type: str
    key: str
    fields: dict[str, str] = field(default_factory=dict)
    line: int = 0

    def get(self, name: str, default: str = "") -> str:
        return self.fields.get(name.lower(), default)


class BibParseError(ValueError):
    pass


def _read_braced(text: str, i: int) -> tuple[str, int]:
    """Read from text[i] == '{' to its matching '}'. Return (inner, next index)."""
    depth = 0
    start = i
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
        i += 1
    raise BibParseError(f"unbalanced braces starting at offset {start}")


def _read_quoted(text: str, i: int) -> tuple[str, int]:
    depth = 0
    j = i + 1
    while j < len(text):
        ch = text[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif ch == '"' and depth == 0:
            return text[i + 1 : j], j + 1
        j += 1
    raise BibParseError(f"unterminated quoted value at offset {i}")


def _skip_ws(text: str, i: int) -> int:
    while i < len(text) and text[i].isspace():
        i += 1
    return i


def _parse_fields(body: str) -> tuple[str, dict[str, str]]:
    key, _, rest = body.partition(",")
    key = key.strip()
    fields: dict[str, str] = {}
    i = 0
    while True:
        i = _skip_ws(rest, i)
        if i >= len(rest):
            break
        eq = rest.find("=", i)
        if eq == -1:
            if rest[i:].strip(" ,\n\t"):
                raise BibParseError(f"dangling text in entry {key!r}: {rest[i:].strip()[:40]!r}")
            break
        name = rest[i:eq].strip().strip(",").strip().lower()
        j = _skip_ws(rest, eq + 1)
        if j >= len(rest):
            raise BibParseError(f"missing value for field {name!r} in {key!r}")
        if rest[j] == "{":
            value, j = _read_braced(rest, j)
        elif rest[j] == '"':
            value, j = _read_quoted(rest, j)
        else:
            end = rest.find(",", j)
            end = len(rest) if end == -1 else end
            value, j = rest[j:end].strip(), end
        if name in fields:
            raise BibParseError(f"duplicate field {name!r} in entry {key!r}")
        fields[name] = " ".join(value.split())
        j = _skip_ws(rest, j)
        if j < len(rest) and rest[j] == ",":
            j += 1
        i = j
    return key, fields


def parse_bibtex(text: str) -> list[BibEntry]:
    entries: list[BibEntry] = []
    i = 0
    while True:
        at = text.find("@", i)
        if at == -1:
            break
        brace = text.find("{", at)
        if brace == -1:
            break
        entry_type = text[at + 1 : brace].strip().lower()
        body, i = _read_braced(text, brace)
        if entry_type in SKIPPED_TYPES:
            continue
        key, fields = _parse_fields(body)
        line = text.count("\n", 0, at) + 1
        entries.append(BibEntry(entry_type, key, fields, line))
    return entries


def load_bib(path: str | Path) -> list[BibEntry]:
    return parse_bibtex(Path(path).read_text(encoding="utf-8"))
