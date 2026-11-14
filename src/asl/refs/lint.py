"""Bibliography linter for docs/references.bib.

Rules (errors fail ``make lint-bib`` and Stage 0):

* keys are unique and match ``authorYYYY[a-z]`` (lower case, hyphens allowed);
* entry types and their required fields are present;
* ``year`` is four digits and plausible;
* DOIs are bare (``10.xxxx/...``), never ``https://doi.org/...`` URLs;
* ISBNs pass their checksum;
* every entry has a locator (``doi``, ``isbn``, ``url``, or ``eprint``), or
  declares ``asl_status = {manual}`` with an ``asl_check`` explaining how a
  human verified it, or is flagged ``asl_status = {todo-verify}`` (warning);
* ``asl_status = {todo-verify}`` entries must say "TODO: verify" in ``note``;
* ``asl_record = {retracted}`` entries must name ``asl_retraction_doi``;
* the string "TODO" appears only in ``note``.

The ``asl_*`` fields are project-specific; BibTeX and biber ignore them.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from dataclasses import dataclass

from asl.refs.bibparse import BibEntry, BibParseError, load_bib

KEY_RE = re.compile(r"^[a-z][a-z0-9-]*\d{4}[a-z]?$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
YEAR_RE = re.compile(r"^\d{4}$")

REQUIRED = {
    "article": ("author", "title", "journal", "year"),
    "book": ("author", "title", "publisher", "year"),
    "incollection": ("author", "title", "booktitle", "year"),
    "inproceedings": ("author", "title", "booktitle", "year"),
    "misc": ("author", "title", "year"),
    "techreport": ("author", "title", "institution", "year"),
}
STATUSES = {"verified-doi", "manual", "todo-verify"}
RECORDS = {"published", "preprint", "retracted", "retraction-notice", "news", "software", "book"}


@dataclass(frozen=True)
class LintIssue:
    key: str
    line: int
    level: str  # "error" or "warning"
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():7} L{self.line:<4} {self.key}: {self.message}"


def isbn_ok(raw: str) -> bool:
    digits = re.sub(r"[^0-9Xx]", "", raw)
    if len(digits) == 10:
        total = 0
        for i, ch in enumerate(digits):
            val = 10 if ch in "Xx" else int(ch)
            if ch in "Xx" and i != 9:
                return False
            total += (10 - i) * val
        return total % 11 == 0
    if len(digits) == 13 and digits.isdigit():
        total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
        return total % 10 == 0
    return False


def status_of(entry: BibEntry) -> str:
    """Effective verification status: explicit asl_status, else verified-doi if a DOI exists."""
    explicit = entry.get("asl_status").lower()
    if explicit:
        return explicit
    return "verified-doi" if entry.get("doi") else ""


def lint_entries(entries: list[BibEntry]) -> list[LintIssue]:
    issues: list[LintIssue] = []
    seen: dict[str, int] = {}
    this_year = _dt.date.today().year

    def err(e: BibEntry, msg: str) -> None:
        issues.append(LintIssue(e.key, e.line, "error", msg))

    def warn(e: BibEntry, msg: str) -> None:
        issues.append(LintIssue(e.key, e.line, "warning", msg))

    for e in entries:
        if e.key in seen:
            err(e, f"duplicate key (first defined on line {seen[e.key]})")
        else:
            seen[e.key] = e.line
        if not KEY_RE.match(e.key):
            err(e, "key must look like authorYYYY or authorYYYYa (lower case)")

        required = REQUIRED.get(e.entry_type)
        if required is None:
            err(e, f"unsupported entry type @{e.entry_type}")
            required = ()
        for name in required:
            if not e.get(name):
                err(e, f"missing required field '{name}'")

        year = e.get("year")
        if year and (not YEAR_RE.match(year) or not 1800 <= int(year) <= this_year + 1):
            err(e, f"implausible year {year!r}")

        doi = e.get("doi")
        if doi and not DOI_RE.match(doi):
            err(e, f"DOI must be bare like 10.1103/PhysRev.108.1175, got {doi!r}")

        isbn = e.get("isbn")
        if isbn and not isbn_ok(isbn):
            err(e, f"ISBN fails checksum: {isbn!r}")

        status = status_of(e)
        if status not in STATUSES:
            err(e, f"asl_status must be one of {sorted(STATUSES)} (or omitted when a DOI is present)")
        if status == "verified-doi" and not doi:
            err(e, "asl_status verified-doi requires a doi")
        if status == "manual" and not e.get("asl_check"):
            err(e, "asl_status manual requires asl_check describing how it was verified")
        if status == "todo-verify" and "TODO: verify" not in e.get("note"):
            err(e, "asl_status todo-verify requires 'TODO: verify' in note")
        has_locator = any(e.get(f) for f in ("doi", "isbn", "url", "eprint"))
        if not has_locator and status not in ("manual", "todo-verify"):
            err(e, "no locator (doi, isbn, url, or eprint); use asl_status = {manual} with asl_check")
        if not has_locator and status == "todo-verify":
            warn(e, "no locator yet; does not count as verified")

        record = e.get("asl_record").lower()
        if record and record not in RECORDS:
            err(e, f"asl_record must be one of {sorted(RECORDS)}")
        if record == "retracted" and not e.get("asl_retraction_doi"):
            err(e, "retracted entries must cite asl_retraction_doi")
        if e.get("asl_retraction_doi") and not DOI_RE.match(e.get("asl_retraction_doi")):
            err(e, "asl_retraction_doi must be a bare DOI")

        for name, value in e.fields.items():
            if name != "note" and "TODO" in value:
                err(e, f"'TODO' found in field '{name}'; put it in note")

        if e.entry_type == "article" and not doi and status == "manual":
            warn(e, "article without DOI (acceptable for pre-DOI journals)")

    return issues


def lint_file(path) -> list[LintIssue]:
    try:
        entries = load_bib(path)
    except BibParseError as exc:
        return [LintIssue("<file>", 0, "error", f"parse error: {exc}")]
    return lint_entries(entries)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint a BibTeX file against project rules.")
    parser.add_argument("bib", nargs="?", default="docs/references.bib")
    args = parser.parse_args(argv)
    issues = lint_file(args.bib)
    for issue in issues:
        print(issue)
    errors = sum(1 for i in issues if i.level == "error")
    try:
        n = len(load_bib(args.bib))
    except (BibParseError, OSError):
        n = 0
    print(f"bib lint: {n} entries, {errors} errors, {len(issues) - errors} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
