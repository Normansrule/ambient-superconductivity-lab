"""Checks on the real repository content (no network)."""

import re
from pathlib import Path

from asl.proofs.targets import load_targets
from asl.refs.bibparse import load_bib
from asl.refs.lint import lint_entries, status_of

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = load_bib(ROOT / "docs" / "references.bib")
KEYS = {e.key for e in ENTRIES}


def test_bibliography_lints_clean():
    errors = [i for i in lint_entries(ENTRIES) if i.level == "error"]
    assert errors == [], "\n".join(map(str, errors))


def test_at_least_40_doi_candidates():
    assert sum(status_of(e) == "verified-doi" for e in ENTRIES) >= 40


def test_retractions_point_at_notices_in_the_bib():
    dois = {e.get("doi"): e for e in ENTRIES}
    for e in ENTRIES:
        if e.get("asl_record") == "retracted":
            notice = dois.get(e.get("asl_retraction_doi"))
            if notice is not None:
                assert notice.get("asl_record") == "retraction-notice", e.key


def test_stage0_targets_load():
    spec = load_targets(ROOT / "proofs" / "stage0" / "targets.yaml")
    assert spec.stage == 0 and len(spec.targets) >= 5


def test_roadmap_bibkeys_exist():
    text = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    cited = {k.strip() for group in re.findall(r"\[([a-z][a-z0-9;\s-]*\d{4}[a-z]?)\]", text)
             for k in group.split(";")}
    assert cited, "ROADMAP should cite references"
    assert cited <= KEYS, f"unknown bibkeys: {cited - KEYS}"


def test_site_citations_exist():
    cited = set()
    for path in (ROOT / "site" / "src").rglob("*.tsx"):
        for group in re.findall(r"keys=\{\[([^\]]*)\]\}|cite=\{\[([^\]]*)\]\}", path.read_text(encoding="utf-8")):
            for chunk in group:
                cited |= set(re.findall(r'"([a-z][a-z0-9-]*\d{4}[a-z]?)"', chunk))
    assert cited, "site should cite references"
    assert cited <= KEYS, f"unknown bibkeys in site: {cited - KEYS}"
