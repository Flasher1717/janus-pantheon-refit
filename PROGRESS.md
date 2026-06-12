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

### Done (continued — M9 and M10, auto-mode)
- M9: janus_refit.reference (frozen measured values, single source), comparison.py
  (AIC/BIC), MarginalizedChi2.best_offset, scripts/run_comparison.py. Measured:
  dAIC vs LCDM = +47.620 (Janus) / +47.566 (Milne); dBIC = +47.620 / +42.201;
  Janus-vs-Milne dAIC +0.054, dBIC +5.419 (nested at q0=0, noted next to the
  numbers). Residuals figure (frozen fits): Janus/Milne -LCDM at z_max = +0.4803 /
  +0.4041 mag; < 0.0490 mag below z = 0.5. RESULTS.md §6.7 + §7.4.
- M10: RESULTS.md §8 completed (8.1 dataset/covariance incl. standardization
  inheritance with its direction stated, 8.2 method incl. prior dependence and
  boundary truncation, 8.3 what this does NOT prove incl. the pile-up reading
  guard). Three-lens honesty review (no-overclaim / numerical traceability /
  internal consistency): traceability PASS — every load-bearing number reproduced
  by independent recomputation; all should-fix findings applied (evaluative
  adjectives removed, §3 forward promises closed with measured numbers, SPEC's
  xfail order-of-magnitude q0 test added to tests/test_fitting.py).

### Done (continued — M11, publication, after Téo's GO with strict scope)
- Pre-push verification: repo-local identity confirmed on every commit (author AND
  committer = Téo Alletz / teo.alletz@gmail.com, zero Kodia identity in history);
  uv.lock consistent with pyproject (CI uses --frozen); gh CLI switched from the
  active Kodiaquebec account to the personal Flasher1717 account per the GO.
- README publication pass (only file touched): CI badge + direct RESULTS.md link at
  the top, Status updated, Layout corrected to actual contents (planned notebooks/
  never existed; scripts/ + figures/ listed instead).
- Published: github.com/Flasher1717/janus-pantheon-refit (public, one-line
  description, topics: cosmology, supernovae, pantheon-plus, reproduction-study,
  model-comparison). First CI run GREEN on the full matrix (ubuntu/windows x
  3.12/3.14, run 27308754465).
- Tag v1.0.0 + GitHub Release (factual notes: dataset, the three chi2, q0 measured
  vs published 2018, link to RESULTS.md at the tag).
- No result, RESULTS.md section 5-7 or test was modified at publication time.

## Project closed (v1.0) — 2026-06-10

All milestones M0-M11 complete. Published at
github.com/Flasher1717/janus-pantheon-refit (v1.0.0). The repository is the record:
SPEC.md (verbatim spec), RESULTS.md (equations, methodology, results, limitations),
MILESTONES.md (all checked), this file (session history). Out of scope forever per
SPEC: CMB/BAO/N-body, SH0ES calibration, any "validated/refuted" conclusion.
- M11 (CI badge) stays unchecked until CI actually runs green on GitHub — no push
  without explicit GO (perso/org undecided).
Reopened the same day by the v1.1 extension (SPEC_V11.md) — Session 3 below.

### Key technical insight for later sessions
- Janus mu(z) nests Milne exactly at q0 = 0 (eq. 29 at q0=0 gives z + z²/2). The
  Janus-vs-Milne ΔAIC therefore directly tests the preference for q0 < 0.
- Implement both algebraic forms (26)/(28) and (29) and test their agreement; use (29)
  for stability near q0 → 0.

## Session 3 — 2026-06-10 (v1.1 extension: controlled JLA refit, SPEC_V11.md)

### Done
- v1.1 kickoff: SPEC_V11.md committed verbatim (immutable), M12-M14 appended to
  MILESTONES.md. Ritual run first (pytest green: 78 passed, 1 xpassed).
- Research before plan: P1 fit procedure extracted first-hand + 3 blind agent
  extractions, all concordant — central finding: P1 NEVER defines its chi2 error
  model (no covariance, no sigma, anywhere). JLA data located on the live
  first-party host supernovae.in2p3.fr; both v6 tarballs downloaded twice
  independently, SHA256 concordant, structure verified to the byte. Betoule
  Table 10 anchors verified on two renderings (a WebFetch summarizer error was
  caught and rejected in the process). Release-internal divergence found and
  pre-registered away: ReadMe says "both zcmb and zhel are needed" while the
  executable reference test.cc (which reproduces the published 682.9) uses zcmb
  alone -> primary convention = test.cc, heliocentric factor as labeled
  sensitivity.
- Plan reviewed by a SPEC-coverage agent (must-fix integrated: pre-registration
  commit BEFORE the anchor run, whose chi2 would leak variant A4's fate);
  Téo's GO with 3 decisions: criteria validated as-is, no MCMC, grid of 8
  closed at the section 9.2 commit + path-dependence sentence mandated for 9.5.
- M12: download_data.py extended (2 archives + 10 members SHA256-pinned);
  janus_refit.jla (mu_hat per Betoule eqs 4-5 with the host step at
  scriptmcut 10.0 strict; C(alpha,beta) by stride-3 reduction of the interleaved
  2220x2220 C_eta + the three diagonal terms verbatim from the release
  example.py); covariance verified element-wise (< 1e-14) against an independent
  dense-A construction; RESULTS.md sections 9.1 + 9.2 committed before any
  real-data fit. Anchor run: Omega_m = 0.295471 +/- 0.033512 vs published
  0.295 +/- 0.034 (gate PASS at 0.014 sigma), chi2 = 682.892 vs published 682.9
  (0.008) — exact external replication of the Betoule likelihood.
- M13 (arm A, grid closed at 8): verdict per pre-registered criteria —
  0/8 pass C1^C2^C3 -> NON-REPRODUCTION; blocking criterion is C3 (chi2)
  everywhere (no variant within +/-20 of the published 657). Principal variant
  (selection rule): diag-propagated / no-step, q0 = -0.088737 +/- 0.014892
  (matches published -0.087 +/- 0.015 to 0.12 sigma and 1% on sigma), chi2
  780.257. Sensitivities (zhel; Table 10 stat row, double-verified at use time):
  |delta q0| < 0.001. All 8 results pinned in tests (reproducibility only).
- M14 (arm B = v1.0 pipeline on JLA): LCDM 682.892 (= anchor); Janus
  q0 = -0.066887 +/- 0.028259, chi2 691.308, dAIC +8.416; Milne 696.347,
  dAIC +11.455, dBIC +6.848; Janus-vs-Milne dchi2 = -5.039 (AIC -3.039,
  BIC +1.567 — opposite signs; on Pantheon+ both were positive). Janus minimum
  parabolic (0.955/1.050 at +/-1 sigma) and 2.37 sigma from the q0 = 0 bound —
  the 9.2 no-MCMC justification anticipated >= 5 sigma; the no-trigger call is
  documented as post-hoc and unilateral in 9.4, flagged for Téo at the pre-tag
  STOP. Non-regression green: the arm-B code path re-derives the frozen v1.0
  Pantheon+ numbers at recorded precision.
- Section 9.5 attribution: gap (published 2018 vs v1.0 Pantheon+) -0.065990 =
  Delta_data -0.045877 (~70%, JLA vs Pantheon+ at fixed v1.0 method) +
  Delta_method -0.021850 (~33%, on JLA; its error-model/step sub-split is
  path-dependent and reported under both orderings) + residual +0.001737
  (= the arm-A reproduction distance). Mandated path-dependence statement
  included; no significance attached (overlapping compilations).
- Three-lens honesty review before the final commit (traceability: every
  number in section 9 reproduced digit-for-digit from fresh runs; no-overclaim:
  1 must-fix corrected — the Delta_method sub-split dominance claim was
  path-dependent; consistency: pre-registration commit order verified in git).
- Quality: ruff + format + pyright strict green; 88 passed + 1 xpassed.

- Pre-tag GO (Téo, 2026-06-10): the flagged post-hoc call was replaced by a
  measured cross-check — express MCMC of the arm-B Janus posterior on JLA,
  section 6.5 protocol, NEW seed 20260612, truncated-Gaussian prediction
  committed before the run (commit 7591857). Measured: tau 24.40 (n/tau 164,
  converged), q0 = -0.065431 (+0.027424/-0.026888) median 16/84%, std 0.026595
  = 0.9411 x curvature sigma -> 20% STOP gate PASS; std prediction confirmed
  within 3%; predicted asymmetry direction unresolved (1.6 MC-std); the
  P(q0 > -0.02) excess (3 MC-std) tracks the measured profile
  non-parabolicity. RESULTS.md section 9.4 updated with the
  prediction/measurement pair.

## v1.1 closed — 2026-06-10

M12-M14 plus the pre-tag GO addendum (MCMC cross-check) complete. Tag v1.1.0
pushed to github.com/Flasher1717/janus-pantheon-refit with a GitHub release
(factual notes: anchor, arm-A verdict, the three q0 of the attribution chain,
link to RESULTS.md section 9 at the tag). CI green on the full matrix
(ubuntu/windows x 3.12/3.14, run 27319840660) before this closing note, per the
v1.0 M11 rule. No v1.0 result was modified; the frozen Pantheon+ numbers
re-derive through the arm-B code path (non-regression test, green).

## Doc erratum — 2026-06-12

Attribution fix in RESULTS.md §4 (doc-only, no number changed): the 1580-SN
count was credited to Brout et al. 2022; the string "1580" does not appear in
that paper. 1580 is the Hubble-diagram count of the SH0ES-mode selection as
used by Keeley et al. 2024 — the very configuration our §6.3 gate is anchored
to. Mechanics established at the sources in the companion project
desi-w0wa-refit (RESULTS.md §2.2, published at its tag v1.0.0). Erratum note
left inline in §4. Tag v1.1.1 (doc-only) pending Téo's push GO.
