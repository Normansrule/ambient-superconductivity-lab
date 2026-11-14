# Roadmap

Each stage is sized for one person working about 10 hours a week, and each ends in an automated proof. A stage is **done** only when `make prove-N` passes **and** Aleksander approves it in [`proofs/registry.yaml`](proofs/registry.yaml). The next stage does not start before then.

## North Star (milestones, not proofs)

1. An independently replicated superconductor at ambient pressure with a critical temperature (Tc) above the boiling point of liquid nitrogen at one atmosphere.
2. The same, with Tc above room temperature.

This project does not claim it will reach either milestone. Its job is to make the search, and every claim made along the way, checkable.

## Stages

| Stage | Build | Proof |
|---|---|---|
| **S0 Foundation** (1 week, $0) | Environment, continuous integration (CI), GitHub Pages, proof harness, 40+ verified references, README skeleton | CI green; Pages deploys; bibliography lint passes; `make prove-0` passes |
| **S1 Theory engine** (3 weeks, $0) | London penetration depth; Ginzburg–Landau ξ and κ; Bardeen–Cooper–Schrieffer (BCS) gap-equation solver; McMillan and Allen–Dynes Tc; visuals and a Manim scene | Δ(0)/(k_B·Tc) = 1.764 within 0.5%; ΔC/(γTc) = 1.43 within 1% [muhlschlegel1959]; Allen–Dynes reproduces measured Tc for ≥ 3 elements [allen1975] |
| **S2 Curated data and landscape** (2–3 weeks, $0) | SuperCon-derived dataset with a provenance card; deduplication; composition parsing; Tc-versus-year chart; 3D "materials galaxy" | Schema validation; documented and tested dedupe rules; ≥ 20 entries spot-checked against papers; galaxy passes the Playwright render test |
| **S3 Machine learning (ML) screening** (3–4 weeks, $0) | Composition-feature Tc regressor; energy-above-hull stability filter; uncertainty estimates | Matches or honestly reports the gap to a cited baseline on its split; leave-one-family-out results; calibrated prediction intervals |
| **S4 Claim checklist** (3 weeks, $0) — *flagship* | Evidence rubric and `asl.claims.score()` with a site page | Rubric frozen by git tag before validation; ≥ 10 confirmed superconductors score high; ≥ 5 refuted or retracted claims score low |
| **S5 Tabletop measurement** (4–6 weeks; cost cap TODO: verify) | Yttrium barium copper oxide (YBCO) Meissner and flux-pinning demos; DIY four-point probe logged by an ESP32 or Arduino; cryogen safety; bill of materials (BOM) | Resistance-versus-temperature transition midpoint inside the literature range given stated thermometry uncertainty; levitation video and log |
| **S6 First-principles check** (optional, 4–6 weeks) | Quantum ESPRESSO + Electron–Phonon Wannier (EPW) workflow on an official tutorial system [ponce2016; lee2023b] | Computed λ and Tc within published tolerance; workflow reruns from inputs |
| **S7 Preregistered predictions preprint** (4 weeks) | Ranked candidates with uncertainty and "why this could be wrong"; paper and open benchmark | Predictions frozen with a git tag and a Zenodo Digital Object Identifier (DOI); paper builds in CI; arXiv preprint posted |
| **S8 Collaboration proposal** (ongoing) | Synthesis and characterization proposal (solid-state synthesis, X-ray diffraction (XRD), magnetometry) for a partner lab | Proposal sent and response tracked; partner data scored publicly with the S4 rubric |

## Proposed amendments (awaiting Aleksander's decision)

These came out of the Stage 0 review. None is adopted until approved; each would be recorded in the stage's `targets.yaml` before that stage starts.

| Stage | Proposal | Why |
|---|---|---|
| S2 | Check the license of SuperCon and of each derived set before committing rows; if redistribution is unclear, commit a fetch-and-clean script plus checksums | Raw data may not be redistributable in a public repository |
| S3 | Name the published baseline and its split in `targets.yaml` **before** training (candidates: [stanev2018], [hamidieh2018]) | Choosing the baseline after seeing results undermines the preregistration ethos |
| S3 | Store `MP_API_KEY` as a GitHub Actions secret, and make tests use a cached snapshot | Keeps CI and forks working without the key |
| S4 | Freeze a numeric decision threshold with the rubric and report a confusion matrix | Makes "scores high" and "scores low" objective |
| S5 | Use a type-T thermocouple or a calibrated platinum resistance temperature detector (RTD), with a two-point calibration at liquid nitrogen and ice water | Type-K sensitivity is poor near 77 K, which weakens the transition-midpoint proof |
| S7 | Arrange an arXiv endorsement early; mint the Zenodo DOI from a GitHub *release*, not a bare tag | First-time cond-mat submitters may need endorsement; Zenodo's GitHub integration archives releases |
| CI | Render Manim scenes in a separate, cached job | LaTeX, ffmpeg, and Cairo are slow to install |
