import pytest

from asl.refs.bibparse import BibParseError, parse_bibtex

SAMPLE = r"""
% comment line
@article{bardeen1957,
  author  = {Bardeen, John and Cooper, Leon N. and Schrieffer, J. Robert},
  title   = {Theory of {Superconductivity}},
  year    = 1957,
  doi     = "10.1103/PhysRev.108.1175"
}
@comment{ignored}
@book{tinkham2004, author={Tinkham, Michael}, title={Intro}, publisher={Dover}, year={2004},}
"""


def test_parses_entries_fields_and_lines():
    entries = parse_bibtex(SAMPLE)
    assert [e.key for e in entries] == ["bardeen1957", "tinkham2004"]
    b = entries[0]
    assert b.entry_type == "article"
    assert b.get("title") == "Theory of {Superconductivity}"
    assert b.get("year") == "1957"
    assert b.get("doi") == "10.1103/PhysRev.108.1175"
    assert b.line == 3


def test_trailing_comma_and_case_insensitive_fields():
    e = parse_bibtex("@misc{x2020, TITLE = {T}, Year = {2020},}")[0]
    assert e.get("title") == "T" and e.get("year") == "2020"


def test_unbalanced_braces_raise():
    with pytest.raises(BibParseError):
        parse_bibtex("@article{x2020, title = {oops}")


def test_duplicate_field_raises():
    with pytest.raises(BibParseError):
        parse_bibtex("@article{x2020, title={a}, title={b}}")
