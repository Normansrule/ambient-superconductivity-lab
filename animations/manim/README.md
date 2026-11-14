# Manim scenes

Each scene lives in `scenes/` (one scene per file). CI renders every scene at low quality (`-ql`) and uploads the videos as an artifact; `make manim` does the same locally.

| Scene | Stage | Status |
|---|---|---|
| `title_card.py` — pipeline smoke test | S0 | renders in CI |
| "Why resistance vanishes" | S1 | planned |

Equations shown in a scene follow the same rule as everywhere else: each one carries a `[bibkey]`, listed in the scene's docstring.
