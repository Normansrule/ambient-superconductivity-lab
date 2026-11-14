# Stage 0 proof: Foundation

**Claim.** The repository has a working environment, a continuous integration (CI) pipeline, a GitHub Pages site, a proof harness, and a bibliography of at least 40 references whose Digital Object Identifiers (DOIs) were checked by machine against the DOI registry.

**State:** in progress. Stage 0 is *done* only when every check below passes **and** Aleksander records approval in [`proofs/registry.yaml`](../registry.yaml).

## Automated checks (`make prove-0`)

`make prove-0` first runs `make verify-refs`, which resolves every DOI through DOI content negotiation (falling back to the Crossref REST API) and compares the registry's title, year, and first author against `docs/references.bib`. It then runs the targets in [`targets.yaml`](targets.yaml):

| Target | Requirement | What it proves |
|---|---|---|
| `required_files_missing` | = 0 | README, Makefile, CONTRIBUTING, CITATION.cff, ROADMAP, both licenses, the conda environment, both workflows, the site, and the provenance template exist |
| `tree_dirs_missing` | = 0 | The agreed directory structure exists |
| `bib_entries_total` | ≥ 40 | The bibliography is large enough to support Stages 1–4 |
| `bib_lint_errors` | = 0 | Keys, fields, DOI and ISBN formats, retraction links, and TODO placement are valid |
| `bib_doi_verified` | ≥ 40 | At least 40 references are verified online, not just asserted |
| `bib_doi_not_ok` | = 0 | *Every* DOI checks out; a single mismatch fails the stage |
| `citation_cff_errors` | = 0 | CITATION.cff is valid and declares the MIT code license |
| `readme_status_markers` | = 1 | The README status table is generated, not hand-edited |
| `registry_stages` | = 9 | Stages S0–S8 are all registered |

Entries marked `asl_status = {todo-verify}` (currently classic pre-DOI papers and two software or book references) are allowed but **do not count** toward the 40.

### Offline re-proof

The verifier writes `docs/references.verified.json`, keyed by bibkey with a fingerprint of the DOI, title, year, and first author. Editing an entry invalidates its fingerprint and forces a fresh online check. To re-prove from the last online verification without network access:

```bash
ASL_OFFLINE=1 make prove-0
```

## External checks (recorded here, not automated)

| Check | Evidence | Status |
|---|---|---|
| CI is green on `main` | The `ci` workflow run linked from the README badge | pending first push |
| Pages deploys | The `pages` workflow run and the live site at <https://normansrule.github.io/ambient-superconductivity-lab/> | pending first push |
| Visual proof | Playwright test `site/tests/visual.spec.ts` asserts a non-blank WebGL canvas; screenshots are uploaded as a CI artifact | pending first push |
| Approval | Aleksander's name and date in `proofs/registry.yaml` | pending |

## Known limitations

- The verifier checks that each DOI points at the paper we say it does. It does not check that the paper says what we cite it for; that remains a human responsibility at each use site, enforced by the `[bibkey]` rule.
- Several entries use "and others" for long author lists. Expand them from the registry record before rendering APA reference lists in Stage 7.
- Year matching allows ±1 year because online-first and print dates differ (for example, `ko2025` and `boeri2022`).
