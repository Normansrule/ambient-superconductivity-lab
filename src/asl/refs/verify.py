"""Verify every DOI in references.bib against the registry record.

For each entry with a DOI the verifier resolves metadata through DOI
content negotiation (https://doi.org, which covers Crossref and DataCite,
including arXiv DOIs) and falls back to the Crossref REST API. An entry is
``ok`` when all three agree with the local record:

* title similarity >= 0.85 (or one title contains the other);
* year within +/- 1 (online-first versus print dates differ);
* first author's family name matches (accent- and case-insensitive).

Results are cached in docs/references.verified.json keyed by bibkey, with a
fingerprint of (doi, title, year, first author) so that editing an entry
forces a re-check. The cache is committed, so Stage 0 can be re-proved
offline with ``ASL_OFFLINE=1`` from the last online verification.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

from asl import __version__
from asl.refs.bibparse import BibEntry, load_bib
from asl.refs.lint import status_of

DEFAULT_CACHE = "docs/references.verified.json"
TITLE_THRESHOLD = 0.85
Fetcher = Callable[[str], dict | None]


# ---------------------------------------------------------------- normalizing
def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


_LATEX_ACCENT = re.compile(r"\\[`'^\"~=.uvHtcdbk]\s*\{?([A-Za-z])\}?")


def normalize_text(s: str) -> str:
    s = _LATEX_ACCENT.sub(r"\1", s)
    s = re.sub(r"\\[A-Za-z]+", " ", s)  # drop other LaTeX commands
    s = s.replace("{", "").replace("}", "")  # BibTeX case-protection braces
    s = re.sub(r"<[^>]+>", " ", s)  # drop JATS/HTML tags in registry titles
    s = _strip_accents(s).replace("ß", "ss").lower()
    s = re.sub(r"^(retracted article|retracted|retraction note|retraction)\s*:\s*", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def first_author_family(author_field: str) -> str:
    first = re.split(r"\s+and\s+", author_field.strip(), maxsplit=1)[0].strip()
    first = first.strip("{}")
    if "," in first:
        family = first.split(",", 1)[0]
    else:
        family = first.split()[-1] if first.split() else first
    return normalize_text(family)


def titles_match(local: str, remote: str) -> tuple[bool, float]:
    a, b = normalize_text(local), normalize_text(remote)
    if not a or not b:
        return False, 0.0
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    return (ratio >= TITLE_THRESHOLD or a in b or b in a), round(ratio, 3)


def fingerprint(entry: BibEntry) -> str:
    raw = "|".join(
        [entry.get("doi").lower(), normalize_text(entry.get("title")), entry.get("year"),
         first_author_family(entry.get("author"))]
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------- fetching
def _user_agent() -> str:
    contact = os.environ.get("ASL_CONTACT_EMAIL", "")
    tail = f"; mailto:{contact}" if contact else ""
    return (f"ambient-superconductivity-lab/{__version__} "
            f"(https://github.com/Normansrule/ambient-superconductivity-lab{tail})")


def _get_json(url: str, accept: str, timeout: float = 20.0) -> dict | None:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": _user_agent()})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 406, 410):
                return None
            time.sleep(1.5 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            time.sleep(1.5 * (attempt + 1))
    return None


def fetch_record(doi: str) -> dict | None:
    """Return a CSL-JSON-like dict for ``doi`` or None if it cannot be resolved."""
    quoted = urllib.parse.quote(doi, safe="/()")
    rec = _get_json(f"https://doi.org/{quoted}", "application/vnd.citationstyles.csl+json")
    if rec:
        return rec
    msg = _get_json(f"https://api.crossref.org/works/{quoted}", "application/json")
    return msg.get("message") if msg else None


def summarize_record(rec: dict) -> dict:
    title = rec.get("title", "")
    if isinstance(title, list):
        title = title[0] if title else ""
    year = None
    for key in ("issued", "published-print", "published-online", "created"):
        parts = (rec.get(key) or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            year = int(parts[0][0])
            break
    authors = rec.get("author") or []
    family = ""
    if authors:
        a0 = authors[0]
        family = a0.get("family", "")
        if not family:
            literal = a0.get("literal", "").split()
            family = literal[-1] if literal else ""
    return {"title": " ".join(str(title).split()), "year": year, "first_author": family}


# ---------------------------------------------------------------- comparing
REPLACEMENT_CHAR = "�"


def family_matches_with_wildcards(local_family: str, raw_remote_family: str) -> bool:
    """Match a registry family name in which U+FFFD replaced a lost character.

    Each U+FFFD may stand for exactly one letter; the rest must match in full.
    Example: Crossref stores "M\\ufffdhlschlegel" for 10.1007/BF01332932.
    """
    parts = [normalize_text(p).replace(" ", "") for p in raw_remote_family.split(REPLACEMENT_CHAR)]
    pattern = "[a-z]".join(re.escape(p) for p in parts)
    return re.fullmatch(pattern, local_family.replace(" ", "")) is not None


def compare(entry: BibEntry, remote: dict) -> dict:
    ok_title, ratio = titles_match(entry.get("title"), remote["title"])
    local_year = int(entry.get("year") or 0)
    ok_year = remote["year"] is not None and abs(remote["year"] - local_year) <= 1
    local_family = first_author_family(entry.get("author"))
    remote_family = normalize_text(remote["first_author"])
    # Some registry records (e.g., retraction notices) list no authors; then the
    # author check is skipped and recorded, never silently passed as a match.
    notes = []
    if REPLACEMENT_CHAR in remote["first_author"]:
        # The registry's own record lost a character to an encoding error. Match it as a
        # one-letter wildcard (full match only, no containment) and record that we did.
        ok_author = family_matches_with_wildcards(local_family, remote["first_author"])
        notes.append(f"registry first author {remote['first_author']!r} contains U+FFFD; "
                     "matched with each U+FFFD as exactly one letter")
    else:
        ok_author = not remote_family or (
            local_family == remote_family or local_family in remote_family or remote_family in local_family
        )
    problems = []
    if not ok_title:
        problems.append(f"title similarity {ratio}")
    if not ok_year:
        problems.append(f"year {local_year} vs {remote['year']}")
    if not ok_author:
        problems.append(f"first author {local_family!r} vs {remote_family!r}")
    checks = {"title": ok_title, "year": ok_year,
              "author": "skipped (no registry authors)" if not remote_family else ok_author}
    result = {"status": "ok" if not problems else "mismatch", "title_similarity": ratio,
              "checks": checks, "problems": problems}
    if notes:
        result["notes"] = notes
    return result


def verify_entries(entries: list[BibEntry], cache: dict, *, offline: bool, refresh: bool,
                   fetcher: Fetcher = fetch_record, pause: float = 0.2) -> dict:
    today = _dt.date.today().isoformat()
    out: dict = {}
    for e in entries:
        if status_of(e) != "verified-doi":
            continue
        fp = fingerprint(e)
        prior = cache.get(e.key)
        if prior and prior.get("fingerprint") == fp and prior.get("status") == "ok" and not refresh:
            out[e.key] = prior
            continue
        if offline:
            out[e.key] = {"doi": e.get("doi"), "fingerprint": fp, "status": "unchecked",
                          "problems": ["offline: not yet verified online"]}
            continue
        rec = fetcher(e.get("doi"))
        if rec is None:
            out[e.key] = {"doi": e.get("doi"), "fingerprint": fp, "status": "unresolved",
                          "problems": ["DOI did not resolve"], "checked": today}
        else:
            remote = summarize_record(rec)
            result = compare(e, remote)
            out[e.key] = {"doi": e.get("doi"), "fingerprint": fp, "checked": today,
                          "remote": remote, **result}
        if pause:
            time.sleep(pause)
    return out


def load_cache(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8")).get("entries", {})


def save_cache(path: str | Path, results: dict) -> None:
    payload = {"generator": f"asl.refs.verify {__version__}",
               "rule": "title>=0.85 or containment; |year|<=1; first-author family match",
               "entries": dict(sorted(results.items()))}
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def verified_count(entries: list[BibEntry], cache: dict) -> int:
    """Entries whose DOI was verified online and whose record has not changed since."""
    n = 0
    for e in entries:
        rec = cache.get(e.key)
        if status_of(e) == "verified-doi" and rec and rec.get("status") == "ok" \
                and rec.get("fingerprint") == fingerprint(e):
            n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify bibliography DOIs against registry metadata.")
    ap.add_argument("bib", nargs="?", default="docs/references.bib")
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--offline", action="store_true", default=os.environ.get("ASL_OFFLINE") == "1",
                    help="use the committed cache only (also set by ASL_OFFLINE=1)")
    ap.add_argument("--refresh", action="store_true", help="re-check entries already marked ok")
    args = ap.parse_args(argv)

    entries = load_bib(args.bib)
    results = verify_entries(entries, load_cache(args.cache), offline=args.offline, refresh=args.refresh)
    if not args.offline:
        save_cache(args.cache, results)

    counts: dict[str, int] = {}
    for key, rec in sorted(results.items()):
        counts[rec["status"]] = counts.get(rec["status"], 0) + 1
        if rec["status"] != "ok":
            print(f"{rec['status'].upper():10} {key}: {'; '.join(rec.get('problems', []))}")
    print("verify: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    bad = counts.get("mismatch", 0) + counts.get("unresolved", 0)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
