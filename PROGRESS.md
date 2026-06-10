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

### Done (continued — after Téo's GO)
- M3: GO received from Téo for plan steps 1-2.
- Scaffolding: uv 0.11.19 installed via pip --user (invoke as `python -m uv`),
  pyproject (deps + ruff + pyright strict + pytest), src/janus_refit (typed, py.typed),
  README (EN, AI-assisted mention), MIT LICENSE, CI matrix (ubuntu/windows × 3.12/3.14).
- M4: data pipeline. `scripts/download_data.py` (stdlib urllib, 60 s timeout, SHA256
  pinned: .dat 1cb0fc37…, .cov abf806d9…, idempotent, atomic .tmp+replace).
  `janus_refit.data`: parse (zHD, m_b_corr, IS_CALIBRATOR), cut z > 0.01 AND
  calibrator exclusion → 1580 SNe (z: 0.01016-2.26137), covariance validation (square/finite/symmetric
  within 1e-6 rel/Cholesky PD) returning the symmetrized matrix, immutable SNSample
  (read-only arrays, shape check), self-healing atomic .npz cache keyed on
  v{schema}:sha256(dat):sha256(cov).
- Found: released STAT+SYS matrix is not bit-exactly symmetric (max |C-C^T| = 3e-8,
  text rounding) — tolerated, symmetrized, documented in RESULTS.md §4.
- Two-agent review (quality + simplicity lenses) applied before commit; notable fixes:
  NaN/Inf gate in validate_covariance (NaN comparisons are False → would have passed!),
  non-atomic/non-self-healing cache, silent NaN row drops, missing failure-mode tests.
- Quality: ruff + format + pyright strict + pytest all green (17 tests, 3 on real data).

### Next
- Step 3 (M5/M6): models module — ΛCDM mu(z) vs astropy oracle (<1e-6 mag), Janus
  mu(z) both forms (eq. 26/28 vs 29) + monotonicity/continuity + Milne nesting tests.
- Then step 4: chi2 with full covariance (Cholesky solve) + analytic offset
  marginalization (chi2_p = a - b^2/e), identical pipeline for all 3 models.

### Key technical insight for later sessions
- Janus mu(z) nests Milne exactly at q0 = 0 (eq. 29 at q0=0 gives z + z²/2). The
  Janus-vs-Milne ΔAIC therefore directly tests the preference for q0 < 0.
- Implement both algebraic forms (26)/(28) and (29) and test their agreement; use (29)
  for stability near q0 → 0.
