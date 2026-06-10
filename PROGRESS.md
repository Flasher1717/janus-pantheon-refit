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

### Done (continued — step 3, M5/M6, after Téo's GO with strict scope)
- CLAUDE.md created (76 lines): session ritual, commands, quality gates, numeric
  gates, honesty rules, git rules.
- M5: `janus_refit.models.lcdm_mu` (quad, epsrel 1e-11) vs astropy FlatLambdaCDM:
  max |dmu| = 8.4e-13 mag over 5 (Om, H0) configs, z in [0.01, 2.3] (gate: 1e-6).
- M6: Janus implemented in BOTH published forms. Verbatim eq. (28) bracket has
  catastrophic cancellation in float64 (measured 6.0e-11 rel — cannot meet 1e-12);
  janus_mu_mattig uses the exact conjugate identity 1-s = -2q0z/(1+s) (derived from
  the (26)/(28) form alone). Cross-test (26)/(28) vs (29): max rel diff 3.9e-16 on
  z in [0.01,2.3] x q0 in [-0.21,-0.01] (gate: 1e-12). Milne nesting at q0=-1e-8:
  3.83e-8 mag, matching the analytic bound (5/ln10)|q0| z(1+z)/(2+z) <= 3.9e-8;
  first-order convergence checked. Continuity tested against the analytic derivative
  bound (dmu/dlnz ~ 11.6 mag/e-fold at the domain edge q0=-0.21, z=2.3). Domain
  guards (q0 < 0, 1+2q0z > 0, h0 > 0, 1-D non-empty finite z) + janus_q0_min(z_max)
  exported as the single source of truth for the M7/M8 prior bound.
- Two-agent review (formula fidelity + quality): fidelity PASS (independent 50-digit
  re-derivation, zero formula deviation). Quality fixes applied in-scope: h0/shape
  validation, mattig small-|q0| cancellation floor test-pinned (8.9e-9 mag at
  q0=-1e-8, ~eps/|q0| growth — Terrell form used in that regime), FloatArray moved
  to leaf module _types.py (models no longer imports pandas via data), oracles.py
  pyright directives narrowed, test grids frozen.
- Quality: ruff + format + pyright strict green; 43 tests pass.

## Session 2 — 2026-06-10

### Done
- Session interrupted by a host reboot mid-M7; state recovered from disk (ritual:
  SPEC/PROGRESS/git log/pytest). Téo re-supplied the M7 GO verbatim (strict scope:
  Cholesky-only chi2, analytic offset marginalization, production evaluators pinned
  < 1e-12 with oracles kept, LCDM-first execution order with STOP on gate failure,
  no tuning after seeing results, STOP at end of M7).
- M7 likelihood: `MarginalizedChi2` (A - B²/E offset profiling, cached Cholesky,
  never explicit inverse), validated against Goliath 2001 eq. 21 / Conley 2011
  App. C; exactness vs explicit numerical offset profiling: 2.7e-8 absolute on the
  real 1580×1580 system (~9e-16 relative).
- M7 production evaluators: `janus_mu` unified bracket 2z(1+s+z)/(1+s)² (derivation
  recorded in RESULTS.md §5.1) pinned < 1e-12 mag to BOTH published forms;
  `lcdm_mu_fast` Gauss-Legendre — measured 12 nodes = 2.231e-12 mag (fails the GO's
  own < 1e-12 condition on the full fit domain) → 16 nodes adopted (7.105e-15 mag);
  deviation from the plan's "12" documented in RESULTS.md §5.1.
- GATE EVENT (the SPEC sanity band): best-fit ΛCDM chi2 = 1387.099 < [1400, 1500] →
  full STOP per M7 GO point 3. Five-lens audit (from-scratch covariance restriction:
  bit-exact; independent quad+solve chi2: 1387.098996; formula audit; adversarial
  hunt: all mechanisms refuted by measurement; literature search). Decisive:
  Keeley, Shafieloo & L'Huillier 2024 (Universe 10, 439; arXiv:2212.07917) report
  chi2 = 1387.10 for the IDENTICAL configuration — exact external replication.
- Gate recalibrated with Téo's explicit GO (option 1): |chi2 − 1387.10| ≤ 1.0,
  pre-registered before any Janus/Milne chi2 was seen (statement in RESULTS.md
  §6.3); SPEC.md untouched; CLAUDE.md numeric gate updated; constants in
  `janus_refit.fitting`.
- M7 fits run in the mandated order (scripts/run_fits.py): ΛCDM Ω_m = 0.331631 ±
  0.018207, chi2 = 1387.099 (gate PASS); Janus q0 = -0.021010 ± 0.014767, chi2 =
  1434.719; Milne chi2 = 1436.665. Raw numbers in RESULTS.md §7; limitations seeded
  in §8 (covariance ~7% overestimated per arXiv:2212.07917 → chi2/dof < 1 is a
  dataset property, not a model merit).

### Done (continued — M8, after Téo's GO with strict scope; auto-mode active)
- M8 MCMC: janus_refit.mcmc (1-D posteriors, offset stays analytically profiled),
  priors PRE-REGISTERED and committed before the production run (RESULTS.md §6.5,
  commit 621f957): Omega_m in (0.01, 1) open, q0 in (janus_q0_min(z_max), 0) open =
  the validity domain. Fixed seeds (20260610/20260611) drive walker init AND sampler
  state; bit-reproducibility tested incl. 50-SN real-data subsample (SPEC).
- Review (3 agents, during the run): no finding invalidated the chains; emcee seed
  mechanism verified by direct execution; stubs hardened; chains now persisted
  before gates; seed-mechanism test added (different seed => different chain).
- Pre-registered PREDICTION committed before reading any chain output (§6.6,
  commit 4e10a47): Janus sigma rel. diff ~ -13.3% expected from q0=0 boundary
  truncation alone. MEASURED: -15.3% (no 20% trigger), all companion predictions
  confirmed (P(q0>-0.005): predicted 0.067, measured 0.0672).
- Production run (exit 0): LCDM Omega_m = 0.3320 (+0.0180/-0.0184), tau 23.96;
  Janus q0 = -0.0222 (+0.0123/-0.0138), tau 25.83; both pass n > 50 tau. Milne
  posterior trivial (documented). Corner plots in figures/. Post-run diagnostics
  (10tau-vs-3tau < 8e-5, half-chain splits) clean. RESULTS.md §7.2.
- M9 prep (GO point 5): Brout et al. 2022 Omega_m citation verified verbatim by two
  independent fetches; 2018-vs-here methodological differences table in §7.3.

### Next (M9 — auto-mode, after M8 STOP report)
- Delta-AIC, Delta-BIC, chi2/dof table; residuals vs z plot; same pipeline, frozen
  M7/M8 numbers; side-by-side q0 comparison with §7.3 caveats, zero interpretation
  beyond the numbers.
- Consolidate frozen M7 constants into one src module (review nit).
- M10: RESULTS.md final pass (limitations, what this does NOT prove). M11 blocked
  on push GO (perso/org undecided).
- M11 (CI badge) stays unchecked until CI actually runs green on GitHub — no push
  without explicit GO (perso/org undecided).

### Key technical insight for later sessions
- Janus mu(z) nests Milne exactly at q0 = 0 (eq. 29 at q0=0 gives z + z²/2). The
  Janus-vs-Milne ΔAIC therefore directly tests the preference for q0 < 0.
- Implement both algebraic forms (26)/(28) and (29) and test their agreement; use (29)
  for stability near q0 → 0.
