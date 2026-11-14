"""Verifier logic, tested offline with a fake DOI registry."""

from asl.refs.bibparse import parse_bibtex
from asl.refs.verify import (first_author_family, normalize_text, summarize_record, titles_match,
                             verified_count, verify_entries)

BIB = r"""
@article{bardeen1957, author={Bardeen, John and Cooper, Leon N.}, title={Theory of Superconductivity},
  journal={Physical Review}, year={1957}, doi={10.1103/PhysRev.108.1175}}
@article{wrong2020, author={Smith, A.}, title={A Paper That Does Not Exist},
  journal={J}, year={2020}, doi={10.9999/nope}}
@article{muller1986, author={M{\"u}ller, K. Alex}, title={Some Title}, journal={J}, year={1986},
  doi={10.1/m}}
@article{old1911, author={Onnes, H.}, title={Mercury}, journal={J}, year={1911},
  asl_status={todo-verify}, note={TODO: verify}}
"""

REGISTRY = {
    "10.1103/PhysRev.108.1175": {"title": "Theory of Superconductivity", "issued": {"date-parts": [[1957, 12]]},
                                 "author": [{"family": "Bardeen", "given": "J."}]},
    "10.1/m": {"title": ["Some title"], "issued": {"date-parts": [[1987]]}, "author": [{"family": "Müller"}]},
}


def fake_fetch(doi):
    return REGISTRY.get(doi)


def test_normalization_handles_latex_and_accents():
    assert normalize_text(r"Supraleitf{\"a}higkeit") == "supraleitfahigkeit"
    assert normalize_text("RETRACTED: Colossal") == "colossal"
    assert normalize_text("RETRACTED ARTICLE: Room-temperature") == "room temperature"
    assert first_author_family("Larsen, Ask Hjorth") in "hjorth larsen"  # registry family name
    assert first_author_family(r"M{\"u}ller, K. Alex and Bednorz, J.") == "muller"
    assert first_author_family("John Bardeen and Leon Cooper") == "bardeen"


def test_title_match_threshold():
    assert titles_match("Theory of superconductivity", "Theory of Superconductivity.")[0]
    assert not titles_match("Theory of superconductivity", "Metallic hydrogen")[0]


def test_summarize_csl_record():
    s = summarize_record(REGISTRY["10.1/m"])
    assert s == {"title": "Some title", "year": 1987, "first_author": "Müller"}


def test_verify_marks_ok_mismatch_unresolved_and_skips_todo():
    entries = parse_bibtex(BIB)
    out = verify_entries(entries, {}, offline=False, refresh=False, fetcher=fake_fetch, pause=0)
    assert out["bardeen1957"]["status"] == "ok"
    assert out["muller1986"]["status"] == "ok"  # year within +/- 1, accent-insensitive author
    assert out["wrong2020"]["status"] == "unresolved"
    assert "old1911" not in out
    assert verified_count(entries, out) == 2


def test_editing_an_entry_invalidates_cache():
    entries = parse_bibtex(BIB)
    cache = verify_entries(entries, {}, offline=False, refresh=False, fetcher=fake_fetch, pause=0)
    edited = parse_bibtex(BIB.replace("Theory of Superconductivity}", "Theory of Superconductors}"))
    assert verified_count(edited, cache) == 1
    offline = verify_entries(edited, cache, offline=True, refresh=False, pause=0)
    assert offline["bardeen1957"]["status"] == "unchecked"


def test_registry_replacement_character_is_a_one_letter_wildcard():
    # Crossref's record for 10.1007/BF01332932 stores "M�hlschlegel": the u-umlaut was
    # lost in the registry's own encoding. U+FFFD may stand for exactly one letter, no more.
    bib = r"""@article{m1959, author={M{\"u}hlschlegel, B.}, title={Die thermodynamischen Funktionen},
      journal={J}, year={1959}, doi={10.1/fffd}}"""
    good = {"10.1/fffd": {"title": "Die thermodynamischen Funktionen", "issued": {"date-parts": [[1959]]},
                          "author": [{"family": "M�hlschlegel"}]}}
    out = verify_entries(parse_bibtex(bib), {}, offline=False, refresh=False, fetcher=good.get, pause=0)
    assert out["m1959"]["status"] == "ok"
    assert any("U+FFFD" in n for n in out["m1959"]["notes"])  # recorded, never silent
    for wrong in ("Schmidt", "M�ller", "M�hl"):
        bad = {"10.1/fffd": {**good["10.1/fffd"], "author": [{"family": wrong}]}}
        res = verify_entries(parse_bibtex(bib), {}, offline=False, refresh=False, fetcher=bad.get, pause=0)
        assert res["m1959"]["status"] == "mismatch", wrong


def test_mismatch_detected():
    bad = BIB.replace("year={1957}", "year={1975}")
    out = verify_entries(parse_bibtex(bad), {}, offline=False, refresh=False, fetcher=fake_fetch, pause=0)
    assert out["bardeen1957"]["status"] == "mismatch"
    assert any("year" in p for p in out["bardeen1957"]["problems"])
