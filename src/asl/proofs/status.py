"""Turn proof results into status badges and the README status table.

``python -m asl.proofs.status badges OUT_DIR``
    Writes Shields.io endpoint JSON (one file per stage) plus status.json for
    the site. CI runs this after ``make prove-all`` and publishes the files on
    GitHub Pages, so every README badge reflects the latest CI run.

``python -m asl.proofs.status readme``
    Rewrites the table between the STATUS markers in README.md from
    proofs/registry.yaml. Rows are static; the badges inside them are live.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from asl.proofs.runner import find_root, load_registry

PAGES = "https://normansrule.github.io/ambient-superconductivity-lab"
START, END = "<!-- STATUS:START -->", "<!-- STATUS:END -->"
STATE_LABEL = {
    "planned": "planned",
    "in-progress": "in progress",
    "proved": "proved, awaiting approval",
    "done": "done (proved and approved)",
}


def stage_badge(stage: dict, result: dict | None) -> dict:
    label = f"S{stage['id']} proof"
    if not stage.get("ci"):
        return {"schemaVersion": 1, "label": label, "message": "not started", "color": "lightgrey"}
    if result is None:
        return {"schemaVersion": 1, "label": label, "message": "no result", "color": "yellow"}
    ok = bool(result.get("passed"))
    n_pass = sum(1 for r in result.get("results", []) if r.get("passed"))
    n_all = len(result.get("results", []))
    return {"schemaVersion": 1, "label": label,
            "message": f"{'passing' if ok else 'failing'} {n_pass}/{n_all}",
            "color": "brightgreen" if ok else "red"}


def write_badges(root: Path, out_dir: Path) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for s in load_registry(root):
        rpath = root / "proofs" / f"stage{s['id']}" / "result.json"
        result = json.loads(rpath.read_text()) if rpath.exists() else None
        badge = stage_badge(s, result)
        (out_dir / f"stage{s['id']}.json").write_text(json.dumps(badge) + "\n")
        summary.append({"id": s["id"], "name": s["name"], "state": s["state"], "badge": badge,
                        "commit": (result or {}).get("commit"), "generated": (result or {}).get("generated")})
    (out_dir / "status.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def readme_table(stages: list[dict], root: Path | None = None) -> str:
    rows = ["| Stage | Goal | Time | Cost | State | Proof (live from CI) |",
            "|---|---|---|---|---|---|"]
    for s in stages:
        badge = (f"![S{s['id']}](https://img.shields.io/endpoint?url="
                 f"{PAGES}/status/stage{s['id']}.json)")
        proof = f"proofs/stage{s['id']}/PROOF.md"
        link = proof if root is not None and (root / proof).exists() else "ROADMAP.md#stages"
        rows.append(f"| S{s['id']} | [{s['name']}]({link}) | {s['weeks']} "
                    f"| {s['cost']} | {STATE_LABEL.get(s['state'], s['state'])} | {badge} |")
    return "\n".join(rows)


def update_readme(root: Path) -> bool:
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit("README.md is missing the STATUS markers")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{readme_table(load_registry(root), root)}\n{END}{tail}"
    changed = new != text
    readme.write_text(new, encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Status badges and README table.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("badges")
    b.add_argument("out_dir", type=Path)
    sub.add_parser("readme")
    args = ap.parse_args(argv)
    root = find_root()
    if args.cmd == "badges":
        for s in write_badges(root, args.out_dir):
            print(f"S{s['id']}: {s['badge']['message']}")
    else:
        print("README updated" if update_readme(root) else "README already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
