from asl.refs.bibparse import parse_bibtex
from asl.refs.lint import isbn_ok, lint_entries

GOOD = """@article{cooper1956, author={Cooper, Leon N.}, title={Bound Electron Pairs},
journal={Physical Review}, year={1956}, doi={10.1103/PhysRev.104.1189}}"""


def errors(text):
    return [i.message for i in lint_entries(parse_bibtex(text)) if i.level == "error"]


def test_good_entry_is_clean():
    assert errors(GOOD) == []


def test_duplicate_keys():
    assert any("duplicate key" in m for m in errors(GOOD + GOOD))


def test_bad_key_and_missing_field():
    msgs = errors("@article{Cooper56, author={A}, title={T}, year={1956}, doi={10.1/x.y}}")
    assert any("key must look like" in m for m in msgs)
    assert any("'journal'" in m for m in msgs)


def test_doi_must_be_bare():
    msgs = errors(GOOD.replace("10.1103/PhysRev.104.1189", "https://doi.org/10.1103/PhysRev.104.1189"))
    assert any("DOI must be bare" in m for m in msgs)


def test_todo_only_in_note():
    msgs = errors(GOOD.replace("Bound Electron Pairs", "TODO title"))
    assert any("'TODO' found" in m for m in msgs)


def test_todo_verify_requires_note():
    text = "@article{x1950, author={A}, title={T}, journal={J}, year={1950}, asl_status={todo-verify}}"
    assert any("TODO: verify" in m for m in errors(text))
    ok = text.replace("}}", "}, note={TODO: verify page}}")
    assert errors(ok) == []


def test_no_locator_needs_manual_or_todo():
    text = "@article{x1950, author={A}, title={T}, journal={J}, year={1950}}"
    assert any("no locator" in m for m in errors(text))
    manual = text.replace("}}", "}, asl_status={manual}, asl_check={checked scan, p. 3}}")
    assert errors(manual) == []


def test_retracted_requires_retraction_doi():
    text = GOOD.replace("}}", "}, asl_record={retracted}}")
    assert any("asl_retraction_doi" in m for m in errors(text))


def test_isbn_checksums():
    assert isbn_ok("978-0-486-43503-9")
    assert isbn_ok("0-486-43503-2")
    assert not isbn_ok("978-0-486-43503-8")
