# Contributing

Thank you for helping. This project's value rests on being trustworthy, so the rules below are not optional. Pull requests that break them will be asked to change, however good the physics.

## The six rules

1. **Never call a candidate a superconductor.** Use *predicted* (from a model), *screened* (passed a filter), or *claimed* (asserted by someone else) precisely. Only materials with independently replicated evidence are called superconductors, and then with a citation.
2. **Every equation, critical temperature (Tc) value, and dataset carries a `[bibkey]`** that exists in [`docs/references.bib`](docs/references.bib). Never invent a citation. If you are unsure, add the entry with `asl_status = {todo-verify}` and write "TODO: verify" in its `note`.
3. **Every dataset has a provenance card** (source, version, license, and checksum). Copy [`data/PROVENANCE_TEMPLATE.md`](data/PROVENANCE_TEMPLATE.md). If the license does not clearly allow redistribution, commit a download-and-clean script plus checksums, not the rows.
4. **Every prediction states its method, approximations, and known failure modes.**
5. **One idea per file.** Ask before large design choices (open an issue first). Write a session log for each working session in [`docs/session_logs/`](docs/session_logs/). Style: US English, Oxford commas, American Psychological Association (APA) citations, and acronyms spelled out on first use.
6. **Licenses:** code is MIT ([`LICENSE`](LICENSE)); documentation is CC BY 4.0 ([`LICENSE-docs`](LICENSE-docs)).

## How a stage is proved

Each stage has `proofs/stageN/` with:

- `targets.yaml` — the frozen targets (quantity, expected value, tolerance, and `[bibkey]` for physical quantities);
- `prove.py` — defines `measure(root)` and returns a number for every target;
- `PROOF.md` — the human-readable argument and any external evidence.

`make prove-N` must pass, and Aleksander must approve (recorded in [`proofs/registry.yaml`](proofs/registry.yaml)), before the next stage begins. **Changing a target after seeing results is not allowed.** Revise targets only in a new, tagged version, and explain why in `PROOF.md`.

## Before opening a pull request

```bash
make test          # unit tests
make lint-bib      # bibliography rules
make prove-all     # every stage CI runs (verifies DOIs online)
make site          # only if you touched site/
```

## Adding a reference

1. Add the BibTeX entry with a bare DOI (for example, `doi = {10.1103/PhysRev.108.1175}`), never a `https://doi.org/` URL.
2. Run `make verify-refs`. It resolves the DOI and compares the title, year, and first author. Fix any mismatch; do not suppress it.
3. Commit `docs/references.bib` together with the updated `docs/references.verified.json`.

## Session logs

Name them `docs/session_logs/YYYY-MM-DD-sN-short-topic.md` and record what was done, what was decided (and by whom), what is open, and the commands that prove the current state.
