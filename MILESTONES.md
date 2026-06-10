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
- [ ] M9 — Model comparison: chi2/dof, Delta-AIC, Delta-BIC, residuals vs z
- [ ] M10 — RESULTS.md complete and honest (methodology, tables, known limits,
      what the result does NOT prove)
- [ ] M11 — CI GitHub Actions: ruff + pyright + pytest on push
