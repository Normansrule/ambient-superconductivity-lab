"""Stage 0 proof: the foundation exists and the bibliography is verified.

Run with ``make prove-0`` (verifies DOIs online first) or, offline from the
committed verification cache, ``ASL_OFFLINE=1 make prove-0``.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from asl.refs.bibparse import load_bib
from asl.refs.lint import lint_entries, status_of
from asl.refs.verify import DEFAULT_CACHE, fingerprint, load_cache, verified_count

REQUIRED_FILES = [
    "README.md",
    "Makefile",
    "CONTRIBUTING.md",
    "CITATION.cff",
    "ROADMAP.md",
    "LICENSE",
    "LICENSE-docs",
    "environment.yml",
    "pyproject.toml",
    "docs/references.bib",
    ".github/workflows/ci.yml",
    ".github/workflows/pages.yml",
    "site/package.json",
    "data/PROVENANCE_TEMPLATE.md",
]

REQUIRED_DIRS = [
    "docs/theory", "docs/landscape", "docs/screening", "docs/measurement", "docs/claims",
    "docs/experiments", "docs/papers", "docs/session_logs",
    "src/asl/theory", "src/asl/data", "src/asl/screening", "src/asl/claims", "src/asl/measurement",
    "data", "notebooks", "animations/manim", "site", "proofs", "tests",
]


def citation_cff_problems(path: Path) -> list[str]:
    try:
        cff = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"unreadable: {exc}"]
    problems = [f"missing {k}" for k in ("cff-version", "message", "title", "authors", "license",
                                         "repository-code") if not cff.get(k)]
    for a in cff.get("authors") or []:
        if not a.get("family-names"):
            problems.append("author without family-names")
    if cff.get("license") and cff["license"] != "MIT":
        problems.append("code license must be MIT")
    return problems


def measure(root: Path) -> dict:
    entries = load_bib(root / "docs" / "references.bib")
    issues = lint_entries(entries)
    cache = load_cache(root / DEFAULT_CACHE)

    doi_entries = [e for e in entries if status_of(e) == "verified-doi"]
    not_ok = [e.key for e in doi_entries
              if not (cache.get(e.key, {}).get("status") == "ok"
                      and cache[e.key].get("fingerprint") == fingerprint(e))]

    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    markers = min(readme.count("<!-- STATUS:START -->"), readme.count("<!-- STATUS:END -->"))
    registry = yaml.safe_load((root / "proofs" / "registry.yaml").read_text(encoding="utf-8"))

    missing_files = [f for f in REQUIRED_FILES if not (root / f).is_file()]
    missing_dirs = [d for d in REQUIRED_DIRS if not (root / d).is_dir()]
    cff = citation_cff_problems(root / "CITATION.cff")

    def note(items: list[str], limit: int = 4) -> str:
        return ", ".join(items[:limit]) + (" …" if len(items) > limit else "")

    return {
        "required_files_missing": {"value": len(missing_files), "note": note(missing_files)},
        "tree_dirs_missing": {"value": len(missing_dirs), "note": note(missing_dirs)},
        "bib_entries_total": len(entries),
        "bib_lint_errors": sum(1 for i in issues if i.level == "error"),
        "bib_doi_verified": verified_count(entries, cache),
        "bib_doi_not_ok": {"value": len(not_ok),
                           "note": ("run `make verify-refs` online: " + note(not_ok)) if not_ok else ""},
        "citation_cff_errors": {"value": len(cff), "note": note(cff)},
        "readme_status_markers": markers,
        "registry_stages": len(registry.get("stages", [])),
    }
