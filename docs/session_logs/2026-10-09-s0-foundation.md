# Session log — 2026-10-09 — Stage 0 (Foundation), session 1

**Who:** Claude (AI assistant), for Aleksander Norman. **Stage state after session:** in progress (not yet proved; not approved).

## What was built

- Repository skeleton matching the agreed structure, with MIT (code) and CC BY 4.0 (docs) licenses, `CITATION.cff`, `CONTRIBUTING.md` (the six rules), and `ROADMAP.md`.
- Proof harness in `src/asl/proofs/`: target schema and validation (`targets.py`), tolerance checks (`check.py`), the stage runner behind `make prove-N` and `make prove-all` (`runner.py`), and status badges plus the generated README table (`status.py`).
- Bibliography tooling in `src/asl/refs/`: a dependency-free BibTeX parser, a linter enforcing the citation rules, and an online Digital Object Identifier (DOI) verifier with a fingerprinted cache (`docs/references.verified.json`).
- `docs/references.bib`: 69 entries; 62 with DOIs (to be machine-verified), 7 flagged `todo-verify` (pre-DOI classics, Tinkham's textbook, and scikit-learn), which do not count toward the 40.
- Stage 0 proof: `proofs/stage0/` with nine targets.
- Site: Vite + React + TypeScript + react-three-fiber + drei + GSAP + KaTeX, with a phonon-pairing hero scene, vocabulary, proof loop, and live stage grid; Playwright tests for a non-blank WebGL canvas and page structure, with screenshots.
- Workflows: `ci.yml` (tests, bibliography lint, README-table drift check, `make prove-all`, site build and visual tests, Manim render) and `pages.yml` (proofs → badges → site → Pages).
- A Manim smoke-test scene (`animations/manim/scenes/title_card.py`).

## Decisions made (by Claude, open to Aleksander's veto)

| Decision | Reason |
|---|---|
| README badges come from Shields.io endpoint JSON published on Pages, not from CI committing to `main` | "Generated from CI" without bot commits or loops |
| Every DOI must verify (`bib_doi_not_ok = 0`), not just 40 | One wrong DOI undermines the bibliography's trust |
| Year match allows ±1 | Online-first and print years differ (`ko2025`, `boeri2022`) |
| Author lists use "and others" where not checked | Avoids inventing co-authors; expand before APA rendering |
| Plotly.js deferred to Stage 2 | Nothing in Stage 0 plots data; avoids a 3 MB dependency now |
| `pages.yml` deploys even if a proof fails | Badges must be able to show "failing"; `ci.yml` is the gate |
| Proposed amendments to S2–S7 recorded in `ROADMAP.md`, not adopted | Rule 5: ask before large design choices |

## Verification done this session

- `python -m pytest`: 33 passed.
- `make lint-bib`: 69 entries, 0 errors, 5 warnings (the pre-DOI classics).
- `ASL_OFFLINE=1 make prove-0`: 7 of 9 targets pass. The two DOI targets fail **by design** until `make verify-refs` runs with network access; the session's sandbox could not reach doi.org.
- All 62 DOIs were spot-checked by hand against Crossref, OpenAlex, or publisher pages: each resolves to the intended work. One expected title was corrected (`ko2025` is the thin-film La₃Ni₂O₇ paper). Registry quirks (retraction prefixes, the "Hjorth Larsen" family name, HTML and MathML in titles) were dry-run against the verifier's comparison and pass.
- `npm run build` succeeds; Playwright: 2 passed (non-blank canvas and page structure).
- Manim could not be installed in the sandbox; the scene compiles, and CI will render it.

## Open items

1. Run `make prove-0` online, commit the resulting `docs/references.verified.json`, and push.
2. Enable GitHub Pages with source "GitHub Actions" (Settings → Pages), then confirm `ci` and `pages` are green.
3. Optional: set the repository variable `ASL_CONTACT_EMAIL` so registry requests identify the project politely.
4. Decide on the proposed amendments in `ROADMAP.md`.
5. Review and approve Stage 0 by recording your name and date in `proofs/registry.yaml` (set `state: done`).
