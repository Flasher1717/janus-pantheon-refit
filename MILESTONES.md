# Milestones

Append-only checklist. Items get checked `[x]`, never deleted or reworded.

- [x] M0 — Repo scaffolding: SPEC.md, MILESTONES.md, PROGRESS.md, git init, .gitignore
- [x] M1 — Source papers acquired (2018, 2024, 2014 if available) and equations
      extracted verbatim into RESULTS.md "Model equations as extracted" (with page numbers)
- [x] M2 — Pantheon+ DataRelease structure verified (exact file paths, URLs, column names)
- [x] M3 — Plan (5-8 steps) + extracted Janus mu(z) formula presented to Téo; GO received
- [x] M4 — Data pipeline: scripts/download_data.py (SHA256), parsing (m_b_corr, zHD),
      z > 0.01 cut, covariance load + Cholesky validation, .npz cache
- [x] M5 — ΛCDM oracle: mu(z) validated against astropy.cosmology (< 1e-6 mag on z ∈ [0.01, 2.3])
- [x] M6 — Janus mu(z) implemented from extracted equations; continuity/monotonicity tests
- [x] M7 — chi2 fits (scipy) for ΛCDM, Janus, Milne with analytic M marginalization;
      ΛCDM sanity check vs published Pantheon+ chi2
- [x] M8 — MCMC (emcee, fixed seeds, autocorrelation convergence) + corner plots
- [x] M9 — Model comparison: chi2/dof, Delta-AIC, Delta-BIC, residuals vs z
- [x] M10 — RESULTS.md complete and honest (methodology, tables, known limits,
      what the result does NOT prove)
- [x] M11 — CI GitHub Actions: ruff + pyright + pytest on push

v1.1 extension (SPEC_V11.md, 2026-06-10) — JLA controlled refit:

- [x] M12 — JLA acquisition (verified URLs, SHA256 pinned), parsing, full covariance
      C(alpha,beta) = A·C_eta·Aᵀ + diagonal terms, validation (740×740, symmetry,
      Cholesky), 2018 fit procedure extracted from P1 into RESULTS.md §9.1 with
      page/equation numbers
- [x] M13 — Arm A (2018 method reproduction). BEFORE any run: pre-register in
      RESULTS.md §9.2 (and commit) the reproduction criteria proposed at plan time
      and validated by Téo
- [x] M14 — Arm B (clean 3-model comparison on JLA) + final §9 + attribution table.
      STOP before tag v1.1.0

CI maintenance (2026-07-02) — GitHub Actions Node 24 runtime:

- [x] Bump `actions/checkout` @v4 -> @v6 and `astral-sh/setup-uv` @v5 -> @v8.2.0
      (both node24; anticipates GitHub's forced Node 24 switch on 2026-06-16).
      Committed on branch `chore/ci-node24` (3b77343); PR #1 merged 2026-07-02
      (merge commit ed29b93). CI run 28563639980 success 4/4
      (ubuntu/windows × py3.12/3.14), zero Node 20 deprecation annotation. Mirror
      of the desi-w0wa-refit sibling bump. No re-tag (tooling maintenance):
      v1.1.1 stays the latest release. CI-only: no src / tests / results / SPEC
      touched.
