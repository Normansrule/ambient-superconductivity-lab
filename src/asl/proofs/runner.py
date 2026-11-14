"""Run a stage proof: ``python -m asl.proofs.runner 0`` or ``--all``.

A stage lives in proofs/stageN/ and provides:

* targets.yaml  the frozen targets (see asl.proofs.targets);
* prove.py      defines ``measure(root: Path) -> dict``, mapping each target id
                to a number or to ``{"value": number, "note": str}``;
* PROOF.md      the human-readable argument, including external proofs.

The runner checks that every target is measured, that every bibkey exists in
docs/references.bib, writes proofs/stageN/result.json, and exits non-zero on
any failure.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import yaml

from asl.proofs.check import CheckResult, check, describe
from asl.proofs.targets import load_targets
from asl.refs.bibparse import load_bib


def find_root(start: Path | None = None) -> Path:
    env = os.environ.get("ASL_ROOT")
    if env:
        return Path(env).resolve()
    here = (start or Path.cwd()).resolve()
    for p in (here, *here.parents):
        if (p / "proofs" / "registry.yaml").exists():
            return p
    raise SystemExit("could not find repo root (proofs/registry.yaml); set ASL_ROOT")


def load_registry(root: Path) -> list[dict]:
    return yaml.safe_load((root / "proofs" / "registry.yaml").read_text(encoding="utf-8"))["stages"]


def _git_sha(root: Path) -> str:
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        return sha
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _import_prove(path: Path):
    spec = importlib.util.spec_from_file_location(f"asl_prove_{path.parent.name}", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "measure"):
        raise SystemExit(f"{path} must define measure(root)")
    return mod


def run_stage(root: Path, n: int, *, quiet: bool = False) -> bool:
    stage_dir = root / "proofs" / f"stage{n}"
    if not stage_dir.is_dir():
        raise SystemExit(f"no proofs/stage{n}/ directory")
    for required in ("targets.yaml", "prove.py", "PROOF.md"):
        if not (stage_dir / required).exists():
            raise SystemExit(f"proofs/stage{n}/{required} is missing")

    spec = load_targets(stage_dir / "targets.yaml")
    if spec.stage != n:
        raise SystemExit(f"targets.yaml says stage {spec.stage}, expected {n}")

    bibkeys = {e.key for e in load_bib(root / "docs" / "references.bib")}
    measured = _import_prove(stage_dir / "prove.py").measure(root)

    results: list[CheckResult] = []
    for t in spec.targets:
        if t.bibkey and t.bibkey not in bibkeys:
            results.append(CheckResult(t.id, None, t.expected, 0.0, False,
                                       f"bibkey {t.bibkey!r} not in references.bib"))
            continue
        raw = measured.get(t.id)
        value, note = (raw.get("value"), raw.get("note", "")) if isinstance(raw, dict) else (raw, "")
        results.append(check(t, value, note))
    extra = sorted(set(measured) - {t.id for t in spec.targets})

    passed = all(r.passed for r in results) and not extra
    payload = {
        "stage": n,
        "name": spec.name,
        "passed": passed,
        "generated": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "commit": _git_sha(root),
        "results": [asdict(r) | {"target": describe(t), "quantity": t.quantity, "bibkey": t.bibkey}
                    for r, t in zip(results, spec.targets)],
        "unexpected_measurements": extra,
    }
    (stage_dir / "result.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if not quiet:
        print(f"\nStage {n}: {spec.name}")
        width = max(len(t.id) for t in spec.targets)
        for r, t in zip(results, spec.targets):
            mark = "PASS" if r.passed else "FAIL"
            val = "—" if r.measured is None else f"{r.measured:g}"
            line = f"  [{mark}] {t.id:<{width}}  measured {val:>8}  target {describe(t)}"
            if t.bibkey:
                line += f"  [{t.bibkey}]"
            if r.note:
                line += f"  ({r.note})"
            print(line)
        for key in extra:
            print(f"  [FAIL] prove.py measured unknown target {key!r}")
        print(f"Stage {n}: {'PASSED' if passed else 'FAILED'}")
    return passed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run stage proofs.")
    ap.add_argument("stage", nargs="?", type=int)
    ap.add_argument("--all", action="store_true", help="run every stage with ci: true in the registry")
    args = ap.parse_args(argv)
    root = find_root()
    if args.all:
        stages = [s["id"] for s in load_registry(root) if s.get("ci")]
    elif args.stage is not None:
        stages = [args.stage]
    else:
        ap.error("give a stage number or --all")
    ok = [run_stage(root, n) for n in stages]
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
