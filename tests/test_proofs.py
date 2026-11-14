"""Proof harness: target parsing, checking, the runner, and status output."""

import json
import textwrap
from pathlib import Path

import pytest

from asl.proofs.check import check
from asl.proofs.runner import run_stage
from asl.proofs.status import readme_table, stage_badge, write_badges
from asl.proofs.targets import Target, TargetError, parse_targets


def t(**kw):
    base = dict(id="x", quantity="q", expected=1.764, kind="meta")
    base.update(kw)
    return Target(**base)


def test_relative_tolerance():
    target = t(tolerance=0.005, tolerance_type="rel")
    assert check(target, 1.770).passed  # 0.34% off
    assert not check(target, 1.775).passed  # 0.62% off


def test_comparators():
    assert check(t(expected=40, comparator="ge"), 62).passed
    assert not check(t(expected=40, comparator="ge"), 39).passed
    assert check(t(expected=0, comparator="le"), 0).passed
    assert not check(t(expected=0, comparator="eq"), 1).passed
    assert not check(t(), None).passed


def test_physical_targets_need_bibkey():
    with pytest.raises(TargetError, match="bibkey"):
        parse_targets({"stage": 1, "targets": [{"id": "gap", "quantity": "q", "expected": 1.764}]})


def test_duplicate_ids_rejected():
    raw = {"id": "a", "quantity": "q", "expected": 1, "kind": "meta"}
    with pytest.raises(TargetError, match="duplicate"):
        parse_targets({"stage": 0, "targets": [raw, raw]})


def make_repo(tmp_path: Path, measured: str, bibkey: str = "bardeen1957") -> Path:
    (tmp_path / "proofs" / "stage1").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / "proofs" / "registry.yaml").write_text(
        "stages:\n  - {id: 1, name: Theory, weeks: '3', cost: '$0', state: in-progress, ci: true}\n")
    (tmp_path / "docs" / "references.bib").write_text(
        "@article{bardeen1957, author={B}, title={T}, journal={J}, year={1957}, doi={10.1/x}}")
    (tmp_path / "proofs" / "stage1" / "targets.yaml").write_text(textwrap.dedent(f"""
        stage: 1
        name: Theory
        targets:
          - {{id: gap_ratio, quantity: q, expected: 1.764, tolerance: 0.005,
              tolerance_type: rel, bibkey: {bibkey}}}
    """))
    (tmp_path / "proofs" / "stage1" / "prove.py").write_text(f"def measure(root):\n    return {measured}\n")
    (tmp_path / "proofs" / "stage1" / "PROOF.md").write_text("# proof\n")
    return tmp_path


def test_runner_passes_and_writes_result(tmp_path):
    root = make_repo(tmp_path, "{'gap_ratio': 1.7639}")
    assert run_stage(root, 1, quiet=True)
    result = json.loads((root / "proofs" / "stage1" / "result.json").read_text())
    assert result["passed"] and result["results"][0]["bibkey"] == "bardeen1957"


def test_runner_fails_on_unknown_bibkey(tmp_path):
    root = make_repo(tmp_path, "{'gap_ratio': 1.764}", bibkey="invented2099")
    assert not run_stage(root, 1, quiet=True)


def test_runner_fails_on_extra_or_missing_measurement(tmp_path):
    assert not run_stage(make_repo(tmp_path, "{'gap_ratio': 1.764, 'surprise': 1}"), 1, quiet=True)


def test_badges_and_table(tmp_path):
    root = make_repo(tmp_path, "{'gap_ratio': 2.0}")
    run_stage(root, 1, quiet=True)
    summary = write_badges(root, tmp_path / "status")
    assert summary[0]["badge"]["message"] == "failing 0/1"
    assert json.loads((tmp_path / "status" / "stage1.json").read_text())["color"] == "red"
    assert stage_badge({"id": 3, "ci": False}, None)["message"] == "not started"
    table = readme_table([{"id": 1, "name": "Theory", "weeks": "3", "cost": "$0", "state": "planned"}], root)
    assert "proofs/stage1/PROOF.md" in table and "status/stage1.json" in table
