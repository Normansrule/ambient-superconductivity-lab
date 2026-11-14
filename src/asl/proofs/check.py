"""Compare one measured value against one target."""

from __future__ import annotations

import math
from dataclasses import dataclass

from asl.proofs.targets import Target


@dataclass(frozen=True)
class CheckResult:
    target_id: str
    measured: float | None
    expected: float
    allowed: float
    passed: bool
    note: str = ""


def allowed_deviation(t: Target) -> float:
    return t.tolerance * abs(t.expected) if t.tolerance_type == "rel" else t.tolerance


def check(t: Target, measured: float | None, note: str = "") -> CheckResult:
    allowed = allowed_deviation(t)
    if measured is None or (isinstance(measured, float) and math.isnan(measured)):
        return CheckResult(t.id, None, t.expected, allowed, False, note or "no measurement")
    m = float(measured)
    if t.comparator in ("approx", "eq"):
        passed = abs(m - t.expected) <= allowed
    elif t.comparator == "ge":
        passed = m >= t.expected - allowed
    else:  # "le"
        passed = m <= t.expected + allowed
    return CheckResult(t.id, m, t.expected, allowed, passed, note)


def describe(t: Target) -> str:
    sym = {"approx": "≈", "eq": "=", "ge": "≥", "le": "≤"}[t.comparator]
    tol = ""
    if t.tolerance:
        tol = f" ± {100 * t.tolerance:g}%" if t.tolerance_type == "rel" else f" ± {t.tolerance:g}"
    unit = f" {t.unit}" if t.unit else ""
    return f"{sym} {t.expected:g}{tol}{unit}"
