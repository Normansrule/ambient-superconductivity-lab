"""Load and validate a stage's targets.yaml.

Schema (one mapping per target)::

    id: snake_case identifier, unique within the stage
    quantity: human-readable description
    expected: number
    comparator: approx | eq | ge | le      (default approx)
    tolerance: number >= 0                 (default 0)
    tolerance_type: abs | rel              (default abs)
    unit: string                           (optional)
    kind: physical | meta                  (default physical)
    bibkey: key in docs/references.bib     (required when kind is physical)
    rationale: why this target proves the stage
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

COMPARATORS = {"approx", "eq", "ge", "le"}
TOL_TYPES = {"abs", "rel"}
KINDS = {"physical", "meta"}
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class TargetError(ValueError):
    pass


@dataclass(frozen=True)
class Target:
    id: str
    quantity: str
    expected: float
    comparator: str = "approx"
    tolerance: float = 0.0
    tolerance_type: str = "abs"
    unit: str = ""
    kind: str = "physical"
    bibkey: str | None = None
    rationale: str = ""


@dataclass(frozen=True)
class StageTargets:
    stage: int
    name: str
    targets: tuple[Target, ...]


def parse_targets(data: dict) -> StageTargets:
    if not isinstance(data, dict) or "targets" not in data:
        raise TargetError("targets.yaml must be a mapping with a 'targets' list")
    stage = data.get("stage")
    if not isinstance(stage, int):
        raise TargetError("'stage' must be an integer")
    seen: set[str] = set()
    targets: list[Target] = []
    for raw in data["targets"]:
        try:
            t = Target(
                id=str(raw["id"]),
                quantity=str(raw["quantity"]),
                expected=float(raw["expected"]),
                comparator=str(raw.get("comparator", "approx")),
                tolerance=float(raw.get("tolerance", 0.0)),
                tolerance_type=str(raw.get("tolerance_type", "abs")),
                unit=str(raw.get("unit", "")),
                kind=str(raw.get("kind", "physical")),
                bibkey=raw.get("bibkey"),
                rationale=str(raw.get("rationale", "")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise TargetError(f"bad target {raw!r}: {exc}") from exc
        if not ID_RE.match(t.id):
            raise TargetError(f"target id {t.id!r} must be snake_case")
        if t.id in seen:
            raise TargetError(f"duplicate target id {t.id!r}")
        seen.add(t.id)
        if t.comparator not in COMPARATORS:
            raise TargetError(f"{t.id}: comparator must be one of {sorted(COMPARATORS)}")
        if t.tolerance_type not in TOL_TYPES:
            raise TargetError(f"{t.id}: tolerance_type must be abs or rel")
        if t.tolerance < 0:
            raise TargetError(f"{t.id}: tolerance must be >= 0")
        if t.kind not in KINDS:
            raise TargetError(f"{t.id}: kind must be physical or meta")
        if t.kind == "physical" and not t.bibkey:
            raise TargetError(f"{t.id}: physical targets must carry a bibkey (rule 2)")
        targets.append(t)
    if not targets:
        raise TargetError("a stage needs at least one target")
    return StageTargets(stage=stage, name=str(data.get("name", f"Stage {stage}")), targets=tuple(targets))


def load_targets(path: str | Path) -> StageTargets:
    return parse_targets(yaml.safe_load(Path(path).read_text(encoding="utf-8")))
