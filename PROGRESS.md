# Progress log

## Session 1 — 2026-06-09

### Done
- M0: git init (`main`), repo-local identity (Téo Alletz / teo.alletz@gmail.com —
  kept separate from the global Kodia identity), SPEC.md (verbatim), MILESTONES.md,
  PROGRESS.md, .gitignore (data/ and papers/ excluded).
- M1: all three papers acquired legally (2018 + 2014 via HAL author deposits,
  2024 via Springer OA; Springer 2018 confirmed paywalled, no OA version-of-record
  exists). SHA256 recorded in RESULTS.md. PDFs rendered to PNG (pymupdf) because
  pdftoppm is unavailable on this host — helper scripts kept in papers/ (gitignored):
  `_render.py`, `_zoom.py`, `_find_pages.py`.
- M1: equations extracted visually from page renders into RESULTS.md §2
  ("Model equations as extracted", with page numbers): 2018 eqs. (1)-(10) and
  Annex A (13)-(29), Annex B (30)-(33); 2024 eqs. (93)-(96b) + Fig. 10.
  Cross-check verdict: **consistent, no blocking divergence** (2024 cites the 2018
  fit as its ref. [4]; prefactor conventions differ but are absorbed in α², no effect
  on mu(z|q0)). Found and documented a sign typo in 2018 eq. (33) (T0·H0 negative as
  printed; (32)-derived form is positive, matches their fig. 8 / table 1).
- M1: extraction verified two ways: (a) numerically — forms (26)/(28) vs (29) agree
  to ~4e-7 relative over q0 ∈ [-0.21, 0), z ∈ [0.01, 2.3]; q0→0 limit equals Milne
  z + z²/2; T0·H0(-0.087) = 1.072 ≈ paper's 1.07; (b) blind re-extraction by 3
  independent agents from the page images — all equations matched character-level.
- M2: Pantheon+ DataRelease verified via GitHub API. Files under
  `Pantheon+_Data/4_DISTANCES_AND_COVAR/`: `Pantheon+SH0ES.dat` (579,283 B, 1701 rows,
  47 cols, header confirmed: `zHD`, `m_b_corr`) and `Pantheon+SH0ES_STAT+SYS.cov`
  (33,284,960 B; line 1 = "1701", then 1701² values sequentially). Raw URLs with
  literal '+' return HTTP 200. README warns: cosmology fits MUST use the full
  covariance, not the _DIAG columns.

### In progress
- M3: plan presented to Téo at end of session 1 — **waiting for GO before any fit code**.

### Next (after GO)
- Python scaffolding (uv, pyproject, ruff, pyright strict, pytest, CI), then M4 data
  pipeline. Note: uv is NOT installed on this host yet; Python 3.14.3 is available
  (spec wants 3.12+; uv can pin the project interpreter).

### Key technical insight for later sessions
- Janus mu(z) nests Milne exactly at q0 = 0 (eq. 29 at q0=0 gives z + z²/2). The
  Janus-vs-Milne ΔAIC therefore directly tests the preference for q0 < 0.
- Implement both algebraic forms (26)/(28) and (29) and test their agreement; use (29)
  for stability near q0 → 0.
