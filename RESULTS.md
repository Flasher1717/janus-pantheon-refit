# Results — Independent refit of the Janus cosmological model on Pantheon+ SNe Ia

> **Status: in progress.** This document is written incrementally as the project advances.
> Chi-square fits (M7) are complete; MCMC posteriors (M8) and model comparison (M9) are
> pending. Sections below marked *(pending)* will be filled once the corresponding
> milestone is complete. The result — whatever it is — will be reported as-is.

## 1. Sources and provenance

All model equations below were extracted **directly from the source papers** (rendered
page images read visually), never from memory. Page references give the page number
printed on the manuscript; for the HAL deposits the PDF page is offset by +1 because of
the HAL cover sheet.

| # | Paper | Version used | File (SHA256, first 12 hex) |
|---|-------|--------------|------------------------------|
| P1 | D'Agostini & Petit, *Constraints on Janus Cosmological model from recent observations of supernovae type Ia*, Astrophys. Space Sci. 363:139 (2018), DOI 10.1007/s10509-018-3365-3 | Author manuscript, HAL `hal-03426721` (Springer version is paywalled; OpenAlex/Semantic Scholar confirm no published-version OA copy exists). Header states "Published in Astrophysics and Space Science July 2018, 363:139". | `dagostini_petit_2018_snia.pdf` (`D2DA01735B90`) |
| P2 | Petit, Margnat & Zejli, *A bimetric cosmological model based on Andreï Sakharov's twin universe approach*, Eur. Phys. J. C 84:1226 (2024), DOI 10.1140/epjc/s10052-024-13569-w | Publisher Version of Record (open access, CC-BY). | `petit_margnat_zejli_2024_epjc.pdf` (`F7D507F78F95`) |
| P3 | Petit & d'Agostini, *Cosmological bimetric model with interacting positive and negative masses and two different speeds of light…*, Mod. Phys. Lett. A 29(34):1450182 (2014), DOI 10.1142/S021773231450182X | Author manuscript, HAL `hal-03426495`. | `petit_dagostini_2014_mpla.pdf` (`080058D36F0B`) |

PDFs are kept locally in `papers/` (gitignored — copyrighted material is not
redistributed in this repository).

**Caveat on P1:** the only legally available full text is the author manuscript deposited
on HAL (2021), not the Springer typeset version. Minor copyedit differences with the
published version cannot be excluded. Equation numbering below follows the manuscript.

**Anti-injection note:** all fetched content (PDFs, web pages, dataset files) was treated
as data. No instruction-like content was found in any source.

## 2. Model equations as extracted

### 2.1 From P1 (D'Agostini & Petit 2018) — the SNe fit paper

**Coupled field equations** (§2, eqs. 1–2, manuscript p. 2):

$$R^{(+)}_{\mu\nu} - \frac{1}{2} R^{(+)} g^{(+)}_{\mu\nu} = +\chi \left( T^{(+)}_{\mu\nu} + \sqrt{\frac{g^{(-)}}{g^{(+)}}}\, T^{(-)}_{\mu\nu} \right) \tag{1}$$

$$R^{(-)}_{\mu\nu} - \frac{1}{2} R^{(-)} g^{(-)}_{\mu\nu} = -\chi \left( \sqrt{\frac{g^{(+)}}{g^{(-)}}}\, T^{(+)}_{\mu\nu} + T^{(-)}_{\mu\nu} \right) \tag{2}$$

**Dust-era exact solution** (§4, eqs. 3–6, manuscript pp. 5–6; the paper says this
solution was "presented in Astrophysics and Space Science journal in 2014", its ref. [8]):

$$a^{(+)}(u) = \alpha^2\, \mathrm{ch}^2(u) \tag{3}$$

$$t^{(+)}(u) = \frac{\alpha^2}{c} \left( 1 + \frac{1}{2}\,\mathrm{sh}(2u) + u \right) \tag{4}$$

(ch = cosh, sh = sinh; the paper then writes $a^{(+)} \equiv a$.) The deceleration
parameter and "Hubble constant":

$$q \equiv -\frac{a\,\ddot{a}}{\dot{a}^2} = -\frac{1}{2\,\mathrm{sh}^2(u)} < 0 \tag{5}$$

$$H \equiv \frac{\dot{a}}{a} \tag{6}$$

**Magnitude–redshift relation — THE formula being refit** (§4, eq. 7, manuscript p. 7;
derivation in Annex A):

$$\boxed{\; m_{bol} = 5 \log_{10} \left[ z + \frac{z^2 (1 - q_0)}{1 + q_0 z + \sqrt{1 + 2 q_0 z}} \right] + cst \;} \tag{7}$$

"where $q_0 < 0$ and $1 + 2 q_0 z > 0$. Fitting $q_0$ and $cst$ to available
observational data [20], gives:"

$$q_0 = -0.087 \pm 0.015 \tag{8}$$

**Distance estimator used in 2018** (eq. 9, manuscript p. 7): JLA standardization

$$\mu = m_B^* - M_B + \alpha X_1 - \beta C \tag{9}$$

with $M_B$, $\alpha$, $\beta$ treated as nuisance parameters whose values were *taken
from the JLA ΛCDM best fit* (their ref. [20], Betoule et al. 2014). Published fit
quality: $\chi^2/d.o.f. = 657/738$ (740 SNe, 2 parameters). Age of the universe
(eq. 10): $T_0 = 1.07/H_0 = 15.0\,$Gyr.

**Annex A — derivation chain** (manuscript pp. 14–16), recorded in full because our
implementation tests will check internal consistency:

- (13) $a^{(+)2} \ddot{a}^{(+)} + \frac{8\pi G}{3} E = 0$, with
  $E \equiv a^{(+)3} \rho^{(+)} + a^{(-)3} \rho^{(-)} = constant < 0$
- (14) parametric solution = eqs. (3)–(4) above
- (15) $\alpha^2 = -\frac{8\pi G}{3 c^2} E$
- (16) $q \equiv -\frac{a \ddot{a}}{\dot{a}^2}$, $H \equiv \frac{\dot{a}}{a}$; solution imposes $k = -1$
- (17) $q = -\frac{1}{2\,\mathrm{sh}^2(u)} = -\frac{4\pi G}{3} \frac{|E|}{a^3 H^2}$
- (18) $(1 - 2q) = \frac{c^2}{a^2 H^2}$
- (19) $l = \int_{t_e}^{t_0} \frac{c\,dt}{a(t)} = \int_{u_e}^{u_0} \frac{1 + \mathrm{ch}(2u)}{\mathrm{ch}^2(u)} du = 2u_0 - 2u_e$
- (20) $l = \mathrm{argsh}(r)$ (Friedmann metric with $k = -1$)
- (21) $r = \mathrm{sh}(2u_0 - 2u_e)$
- (22) $u = \mathrm{argch}\sqrt{a/\alpha^2}$
- (23) $a_e = \frac{a_0}{1+z}$
- (24) $u_0 = \mathrm{argch}\sqrt{\frac{2q_0 - 1}{2q_0}} = \mathrm{argsh}\sqrt{-\frac{1}{2q_0}}$
- (25) $u_e = \mathrm{argch}\sqrt{\frac{2q_0 - 1}{2q_0(1+z)}} = \mathrm{argsh}\sqrt{-\frac{1 + 2q_0 z}{2q_0(1+z)}}$
- (26) $r = \frac{c}{a_0 H_0} \cdot \frac{q_0 z + (1 - q_0)\left(1 - \sqrt{1 + 2 q_0 z}\right)}{q_0^2 (1+z)}$ —
  the paper notes this "is similar to Mattig's work [22] with usual Friedmann solutions
  where $q_0 > 0$, here we have always $q_0 < 0$"
- (27) $E_{bol} = \frac{L}{4\pi a_0^2 r^2 (1+z)^2}$
- (28) $m_{bol} = 5 \mathrm{Log}_{10}\left[ \frac{q_0 z + (1 - q_0)(1 - \sqrt{1 + 2 q_0 z})}{q_0^2} \right] + cte$
- (29) $m_{bol} = 5 \mathrm{Log}_{10}\left[ z + \frac{z^2(1 - q_0)}{1 + q_0 z + \sqrt{1 + 2 q_0 z}} \right] + cst$,
  the Terrell rewriting (their ref. [23]), "which is valid for $q_0 = 0$"

**Annex B** (manuscript p. 17): age–$H_0$–$q_0$ relation. As printed:
$T_0 H_0 = 2 q_0 (1 - 2q_0)^{-3/2} \left( \mathrm{argsh}\sqrt{\frac{-1}{2 q_0}} - \frac{\sqrt{1 - 2 q_0}}{2 q_0} \right)$ (33),
derived from (30)–(32) where (32) carries a $-2q_0$ prefactor.

*Extraction-stage erratum note:* evaluating (33) as printed at $q_0 = -0.087$ gives
$T_0 H_0 = -1.072$ (negative), while substituting $u_0$ from (24) into (32) gives
$+1.072$, matching the paper's own positive values (eq. 10: $T_0 = 1.07/H_0$; fig. 8;
table 1). Eq. (33) as printed therefore dropped the minus sign of the $-2q_0$ prefactor
of (32) — a typo in the manuscript, with no impact on $\mu(z)$ or the fit. Our age
computation will use the (32)-derived form.

### 2.2 From P2 (Petit, Margnat & Zejli 2024) — cross-check

Section 10, p. 16 (printed pagination of the journal version):

- (93) $g = -a^6 \sin^2\theta$, $\bar{g} = -\bar{a}^6 \sin^2\theta$
- (94) $\rho c^2 a^3 + \bar{\rho} \bar{c}^2 \bar{a}^3 = E = \text{cst}$ ("conservation of
  energy, extended to both populations")
- (95) $k = \bar{k} = -1$ ("The exact solution, referring to two dust universes")
- (96a) $a^2 \frac{d^2 a}{dx^{0\,2}} = -\frac{4\pi G}{c^2} E$
- (96b) $\bar{a}^2 \frac{d^2 \bar{a}}{dx^{0\,2}} = +\frac{4\pi G}{\bar{c}^2} E$

Text (p. 16, right column): "The evolution of the positive species will correspond to an
acceleration if the energy $E$ of the system is negative. […] Numerical data have been
successfully compared with observational data [4]. The corresponding curve is shown in
Fig. 10." Fig. 10 (p. 16) is the same Hubble diagram as P1's fig. 7: "ΛCDM with
$(\Omega_M, \Omega_\Lambda) = (0.295, 0.705)$" vs "Bimetric with $q_0 = -0.087$".
Reference [4] of P2 is exactly P1 (verified in the reference list, p. 24).

### 2.3 Cross-check verdict (2018 vs 2024)

**Consistent — no blocking divergence.** The 2024 paper does not re-derive or modify the
magnitude–redshift relation; it reproduces the 2018 fit verbatim (same $q_0 = -0.087$,
same figure) and cites the 2018 paper as its reference [4] for the SNe comparison. Both
papers share the same structure: dust-era exact solution with $k = -1$ and
$a^2\ddot{a} = \text{negative constant}$, giving the one-parameter family $\mu(z\,|\,q_0)$.

One nuance, recorded for honesty: the field-equation prefactor conventions differ —
P1 eq. (13) writes $a^2\ddot{a} = -\frac{8\pi G}{3}E$ with $E$ in *mass* units
($E \equiv a^3\rho + \bar{a}^3\bar{\rho}$), while P2 eq. (96a) writes
$a^2 \frac{d^2a}{dx^{0\,2}} = -\frac{4\pi G}{c^2}E$ with $E$ in *energy* units
($E \equiv \rho c^2 a^3 + \bar{\rho}\bar{c}^2\bar{a}^3$) and $x^0$ a "chronological
coordinate (time marker)". These constants are absorbed into the integration constant
$\alpha^2$ of the parametric solution and **do not enter** the observable
$\mu(z\,|\,q_0)$: the fitted functional form is identical in both papers. This is a
units/convention difference, not a model divergence, so the STOP condition (divergent
equations between papers) is not triggered.

### 2.4 From P3 (Petit & d'Agostini 2014, MPLA) — context only

P3 introduces the bimetric framework and the two-speeds-of-light system (its §3,
eqs. 4a–4b, manuscript p. 5) but contains **no magnitude–redshift fit formula**; the
SNe fit methodology enters the literature with the Astrophys. Space Sci. 2014 paper
(P1's ref. [8], not in our source list) and is fully developed in P1. P3 is kept as
provenance for the field equations only.

## 3. Implementation mapping (what the code will actually compute)

From P1 eq. (26), the luminosity distance is $d_L = a_0 r (1+z)$:

$$d_L(z) = \frac{c}{H_0} \cdot \frac{q_0 z + (1 - q_0)\left(1 - \sqrt{1 + 2 q_0 z}\right)}{q_0^2}$$

and the distance modulus $\mu(z) = 5\log_{10}(d_L/10\,\mathrm{pc})$, equivalently (P1
eq. 29, numerically stable at $q_0 \to 0$):

$$\mu(z) = 5 \log_{10}\left[ z + \frac{z^2 (1 - q_0)}{1 + q_0 z + \sqrt{1 + 2 q_0 z}} \right] + 5\log_{10}\frac{c/H_0}{10\,\mathrm{pc}}$$

Implementation decisions, with reasons:

- **Single shape parameter $q_0$** (with $q_0 < 0$ and $1 + 2 q_0 z > 0$ over the whole
  sample, i.e. $q_0 > -1/(2 z_{max})$; for Pantheon+ $z_{max} \approx 2.26$ this gives
  $q_0 > -0.221$, and the prior bound will be set accordingly and documented). The additive constant
  $5\log_{10}(c/H_0) - M$ is degenerate with the absolute magnitude and is
  **marginalized analytically**, exactly as the paper itself fits "$q_0$ and $cst$".
- **Both algebraic forms (26)/(28) and (29) will be implemented and tested for
  agreement** — a cheap, strong internal-consistency check of our extraction.
- **Milne nesting:** at $q_0 \to 0$, eq. (29) reduces to
  $5\log_{10}[z + z^2/2] + cst$, which is exactly the empty-universe (Milne) Hubble
  relation. The Janus parametrization therefore *nests* Milne at $q_0 = 0$: the
  Janus-vs-Milne comparison directly measures whether $q_0 < 0$ is preferred by the
  data. (P1's published $q_0 = -0.087 \pm 0.015$ is ~5.8σ from 0 on JLA — one thing
  this refit will check on Pantheon+ is whether that displacement survives the full
  STAT+SYS covariance.)
- **Dataset difference, stated upfront:** P1 fit 740 JLA SNe with fixed JLA nuisance
  parameters ($M_B, \alpha, \beta$ from the ΛCDM best fit — a methodological choice we
  inherit *in spirit* but not in detail: Pantheon+ publishes `m_b_corr` already
  Tripp-standardized, so the only remaining nuisance is the additive offset, which we
  marginalize). Reproduction of the published $q_0$ is therefore an
  *order-of-magnitude* check, not an exact one; the corresponding test will be marked
  `xfail`-tolerant and the difference documented here.

## 4. Dataset *(verified 2026-06-09)*

- Repo: `github.com/PantheonPlusSH0ES/DataRelease`, branch `main`.
- Table: `Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat` — 1701 rows,
  47 whitespace-delimited columns; we use `zHD` ("Hubble Diagram Redshift (with CMB and
  VPEC corrections)") and `m_b_corr` ("Tripp1998 corrected/standardized m_b magnitude").
- Covariance: `Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov` —
  first line `1701`, then 1701×1701 values sequentially. The release README warns the
  `_DIAG` error columns must not be used for cosmology: "YOU MUST USE THE FULL
  COVARIANCE".
- *Measured file property:* the released matrix is not bit-exactly symmetric — max
  $|C - C^T| = 3\times10^{-8}$ mag², a decimal-rounding artifact of the text format
  (diagonal entries are $\sim 0.03$ mag², six orders of magnitude larger). The pipeline
  validates symmetry within a $10^{-6}$ relative tolerance, then uses
  $(C + C^T)/2$. Positive definiteness is checked by Cholesky factorization.
- SHA256 of the downloaded files (pinned in `scripts/download_data.py`):
  `Pantheon+SH0ES.dat` = `1cb0fc37…198cf8`, `Pantheon+SH0ES_STAT+SYS.cov` =
  `abf806d9…df0fdc`.
- Cut: $z_{HD} > 0.01$ to limit peculiar-velocity contamination, plus exclusion of the
  Cepheid-host calibrator rows (`IS_CALIBRATOR == 0`) — the standard cosmology-only
  choice when not using the SH0ES Cepheid calibration. **Realized sample: 1580 SNe**
  ($z_{HD} \in [0.01016, 2.26137]$), matching the cosmology sample size of the
  Pantheon+ analysis (Brout et al. 2022).

## 5. Model implementations and oracle validation *(milestones M5-M6, 2026-06-09)*

All three models live in `src/janus_refit/models.py`; each function cites its source
equation from §2. Validation results (measured on this host, float64):

| Check | Requirement | Measured |
|---|---|---|
| ΛCDM $\mu(z)$ vs `astropy.cosmology.FlatLambdaCDM` (5 configs $\Omega_m \in [0.2, 1.0]$, $H_0 \in [67, 73]$, $z \in [0.01, 2.3]$) | < 1e-6 mag | **8.4e-13 mag** |
| Janus eq. (26)/(28) vs eq. (29), grid $z \in [0.01, 2.3] \times q_0 \in [-0.21, -0.01]$ | rel. < 1e-12 | **3.9e-16** |
| Milne nesting: $|\mu_J(q_0{=}-10^{-8}) - \mu_M|$ | < 1e-7 mag (analytic bound 3.9e-8, see below) | **3.83e-8 mag** |
| Milne vs astropy empty universe (`LambdaCDM(Om0=0, Ode0=0)`) | < 1e-6 mag | **7.1e-15 mag** |

Notes, recorded for transparency:

- **Numerical stabilization of the Mattig form (28).** Evaluated verbatim in float64,
  the printed bracket $[q_0 z + (1-q_0)(1-\sqrt{1+2q_0 z})]/q_0^2$ suffers catastrophic
  cancellation at small $|q_0| z$: measured max relative error **6.0e-11** on the test
  grid (worst at $q_0 = -0.01$, $z = 0.01$) — it cannot meet a 1e-12 cross-check on its
  own. `janus_mu_mattig` therefore evaluates it through the exact conjugate identity
  $1 - \sqrt{1+2q_0z} = -2q_0z/(1+\sqrt{1+2q_0z})$, derived from the (26)/(28)
  expression alone (independence from form (29) preserved), giving
  $z(\sqrt{1+2q_0z} - 1 + 2q_0)/(q_0(1+\sqrt{1+2q_0z}))$. This is exact algebra, not a
  tolerance adjustment. A regression test additionally pins the verbatim printed form
  to the stabilized one within its measured 1e-9 cancellation floor.
- **Milne-nesting tolerance, justified.** Expanding the eq. (29) bracket around
  $q_0 = 0$: $f(q_0) - f(0) = -q_0 z^2(1+z)/2 + O(q_0^2)$, hence
  $|\Delta\mu| \approx (5/\ln 10)\,|q_0|\, z(1+z)/(2+z) \le 3.9\times10^{-8}$ mag at
  $q_0 = -10^{-8}$, $z \le 2.3$. The test asserts $< 10^{-7}$ (2.5× margin); the
  measured value (3.83e-8) matches the analytic bound. A second test checks the
  convergence is first order in $q_0$ (ratio of deviations at $q_0 = -10^{-6}$ vs
  $-10^{-8}$ within [80, 120]).
- **Continuity near the domain edge.** $d\mu/d\ln z$ grows like $1/\sqrt{1+2q_0z}$
  toward the validity boundary (≈ 11.6 mag per e-fold at $q_0 = -0.21$, $z = 2.3$), so
  the continuity test bounds each grid step by the analytic derivative
  $f'(z) = (\sqrt{1+2q_0z} - 1 + q_0)/(q_0\sqrt{1+2q_0z})$ rather than a fixed
  threshold. Monotonicity (strictly increasing $\mu(z)$) holds on the whole grid for
  $q_0 \in \{-0.21, -0.087, -0.01\}$, both forms.
- **Residual cancellation in the Mattig form at $q_0 \to 0^-$ (measured, test-pinned).**
  Even stabilized, the (26)/(28) numerator computes $\sqrt{1+\epsilon} - 1$, leaving an
  error of order $\epsilon_{machine}/|q_0|$ in magnitude: measured
  $|\mu_{28} - \mu_{29}| = 8.9\times10^{-9}$ mag at $q_0 = -10^{-8}$, growing as
  $1/|q_0|$. A test pins this floor (bound $10^{-15}/|q_0|$ mag, ~10× margin). The
  Milne-nesting tests and any small-$|q_0|$ evaluation therefore use the Terrell form
  (regular at $q_0 = 0$). The review derived a fully cancellation-free equivalent
  bracket, $2z(1+s+z)/(1+s)^2$ with $s = \sqrt{1+2q_0z}$ (verified exactly equal to
  both published forms at 50-digit precision, no division by $q_0$, regular at
  $q_0 = 0$); adopted at M7 as the production evaluator `janus_mu` — derivation
  recorded in §5.1 below.
- **Domain bound exported.** The prior bound $q_0 > -1/(2 z_{max})$ (§3) is exposed as
  `janus_q0_min(z_max)` so the M7/M8 prior and the model validator share one source of
  truth; a test checks it sits exactly on the domain edge.
- **Performance caveat (resolved at M7):** `lcdm_mu` integrates with `scipy` `quad`
  per redshift — accurate but too slow for ~1e5 MCMC likelihood calls on 1580 SNe
  (measured 16.4 ms/call). The fit stage uses a vectorized fixed-order
  Gauss–Legendre rule mapped onto each $[0, z_i]$ (review measurement: 12 nodes agree
  with the quad oracle to 8.5e-14 mag at ~40× the speed), pinned against this oracle —
  see §5.1 for the adopted node count and the measured errors on the full fit domain.

### 5.1 Production evaluators adopted at M7 *(2026-06-10)*

**Janus — unified cancellation-free bracket (`janus_mu`).** With $s = \sqrt{1 + 2q_0 z}$,
the eq. (29) bracket reduces exactly:

- $2 q_0 z = s^2 - 1$, hence $1 + q_0 z + s = \frac{s^2 + 2s + 1}{2} = \frac{(1+s)^2}{2}$;
- $1 - q_0 = \frac{2z + 1 - s^2}{2z}$;
- therefore
  $z + \frac{z^2 (1 - q_0)}{1 + q_0 z + s}
  = z + \frac{z\,(2z + 1 - s^2)}{(1+s)^2}
  = z\,\frac{(1+s)^2 + 2z + 1 - s^2}{(1+s)^2}
  = \boxed{\frac{2z\,(1 + s + z)}{(1+s)^2}}$

Every term is non-negative for $z > 0$ (no subtraction, no division by $q_0$), and the
expression is regular at $q_0 \to 0^-$: $s \to 1$ gives $z + z^2/2$ (Milne) exactly.
Permanent tests pin `janus_mu` to **both** published forms at < 1e-12 mag — to the
Terrell form (29) over $q_0 \in [-0.21, -0.01]$ plus $\{-10^{-3}, -10^{-5}, -10^{-8}\}$,
and to the Mattig form (26)/(28) over $q_0 \in [-0.21, -0.01]$ (above its measured
cancellation floor, §5). Both published forms keep their own oracle tests.

**ΛCDM — Gauss–Legendre node count (`lcdm_mu_fast`), deviation from plan documented.**
The M7 GO authorized 12 nodes *conditional on* a permanent < 1e-12 mag pin against the
quad oracle. Measured on $z \in [0.01, 2.3]$ (200 points) ×
$\Omega_m \in \{0.2, 0.3, 0.5, 1.0\}$ × $H_0 \in \{67, 70, 73\}$:

| Nodes | max $|\Delta\mu|$ vs quad oracle |
|---|---|
| 12 | 2.231e-12 mag — **fails the < 1e-12 condition** |
| 16 | **7.105e-15 mag** (float64 floor) |

The earlier 8.5e-14 figure for 12 nodes (§5 note above) was measured during the M5–M6
review on a narrower $\Omega_m$ range; on the full fit domain (prior upper bound
$\Omega_m = 1.0$, where the integrand is least polynomial-like) 12 nodes do not meet
the GO's own condition. **16 nodes were therefore adopted** — a deviation from the
plan's "12", forced by the plan's stricter accuracy condition. Permanent test:
`test_lcdm_fast_pinned_to_quad_oracle` (< 1e-12 mag, 4 configurations); the quad
oracle keeps its astropy validation (§5).

## 6. Fit methodology *(M7, 2026-06-10 — chi2 stage; MCMC settings will be added at M8)*

### 6.1 Chi-square with full covariance and analytic offset marginalization

With $\Delta_i = m_{b,corr,i} - \mu_{model}(z_i; \theta)$ and $C$ the full STAT+SYS
covariance restricted to the 1580-SN sample (§4):

$$\chi^2(\theta) = A - \frac{B^2}{E}, \quad
A = \Delta^T C^{-1} \Delta, \quad B = \Delta^T C^{-1} \mathbf{1}, \quad
E = \mathbf{1}^T C^{-1} \mathbf{1}$$

This is exactly the chi-square *profiled* over the additive offset (the degenerate
combination of $M_B$ and $5\log_{10}(c/H_0)$ — the "$cst$" the 2018 paper itself fits),
attained at offset $= B/E$; the standard form of Goliath et al. 2001 (A&A 380, 6,
eq. 21) and Conley et al. 2011 (ApJS 192, 1, Appendix C). The full Bayesian
flat-prior marginalization would add $+\ln(E/2\pi) = 9.322$ (measured,
$E = 70266.44$), a model-independent constant on shared data/covariance: it shifts no
minimum and no $\Delta\chi^2$ between models, and is omitted. All $C^{-1}$ products go
through one cached Cholesky factorization (`scipy cho_factor/cho_solve`); the
covariance is never explicitly inverted. The same `MarginalizedChi2` object (same
data, same factorization) is shared by all three models. $H_0$ is fixed at
70 km/s/Mpc and is fully degenerate with the profiled offset (test:
$\chi^2$ invariant under $H_0 \in [60, 80]$ within $10^{-9}$ relative).

Exactness checks (measured): explicit numerical minimization over the offset agrees
with $A - B^2/E$ to 2.7e-8 absolute on the real 1580×1580 system
($A \approx 2.6\times10^7$, i.e. ~9e-16 relative — float64 floor) and to machine
precision on synthetic systems.

### 6.2 Optimizer and uncertainties

Bounded scalar minimization (`scipy minimize_scalar`, `xatol` = 1e-8):
$\Omega_m \in [0.01, 1.0]$; Janus $q_0 \in (q_{0,min}(1 - 10^{-6}),\ q_{0,min}\cdot10^{-6})$
with $q_{0,min} =$ `janus_q0_min(z_max)` $= -0.2211$ — the single exported source of
truth for the domain/prior bound (§3, §5). Milne has no shape parameter. The quoted
1σ uncertainties are local-curvature (Hessian) estimates
$\sigma = \sqrt{2/\chi^{2\prime\prime}}$ (central second difference at the minimum) —
placeholders until the M8 MCMC posteriors. Both minima were verified interior and
parabolic (five-point scan).

### 6.3 ΛCDM sanity gate: recalibrated with explicit GO, pre-registered

- **The SPEC gate was a-priori.** SPEC.md (immutable, kept verbatim) expects the
  best-fit ΛCDM chi2 in "~1400-1500 for ~1580 points". That band was the SPEC
  author's prior estimate, written before any literature check of this exact
  statistic.
- **Measured value:** best-fit ΛCDM $\chi^2 = 1387.099$ — below the band. Per the M7
  GO ("outside the band = pipeline bug until proven otherwise"), work STOPPED and a
  five-lens audit ran before any other fit: (a) from-scratch covariance restriction —
  bit-exact match to the pipeline matrix, text-file spot checks by raw line number;
  (b) fully independent chi2 recomputation (`scipy quad` + `np.linalg.solve`, no
  project likelihood/fitting code): 1387.098996, grid-scan minimum
  $\Omega_m = 0.33164$, curvature $\sigma = 0.0181$; (c) marginalization formula
  validated against Goliath 2001 / Conley 2011 (above); (d) adversarial bug hunt —
  stale cache, symmetrization, redshift column, optimizer artifacts, covariance
  scale, duplicate handling: all refuted by direct measurement (e.g. symmetrization
  changes the restricted matrix by exactly 0: all 778 asymmetric raw entries lie in
  rows removed by the cut); (e) literature search.
- **Decisive external replication:** Keeley, Shafieloo & L'Huillier 2024 (Universe
  10, 439; arXiv:2212.07917), analyzing the *identical* configuration — Pantheon+
  full STAT+SYS covariance, $z > 0.01$, SH0ES calibrators excluded ($N = 1580$),
  offset profiled — report best-fit flat-ΛCDM $\chi^2 = 1387.10$. Our 1387.099
  replicates the published value to its quoted precision. No published source
  reports a value in [1400, 1500] for this configuration.
- **Recalibrated gate (Téo's explicit GO, 2026-06-10):**
  $|\chi^2_{\Lambda CDM} - 1387.10| \le 1.0$ — an exact-replication anchor,
  *tighter* than the superseded a-priori band, not looser. Implemented in
  `janus_refit.fitting` (`LCDM_CHI2_REFERENCE`, `LCDM_CHI2_TOLERANCE`), enforced by
  `tests/test_fitting.py` and `scripts/run_fits.py` (which still refuses to run
  Janus/Milne if the gate fails).
- **Pre-registration statement.** No Janus or Milne chi2 value was displayed,
  recorded or inspected by anyone before this recalibration was decided and
  implemented. (For completeness: a finiteness-only pytest case had *executed*
  Janus/Milne fits in process memory without exposing any value; no number from
  those fits existed anywhere a human or the assistant could read before the gate
  was fixed.) The recalibration therefore could not have been influenced by the
  comparative outcome.

### 6.4 Execution order

ΛCDM fit first; gate checked; Janus and Milne fits run only after the gate passed
(`scripts/run_fits.py` enforces the order and the STOP).

### 6.5 MCMC settings *(M8 — pre-registered 2026-06-10, committed before the production run)*

Everything in this subsection was fixed and committed **before** the production
chains were run (verifiable from the git history of this section).

- **Sampler:** `emcee` EnsembleSampler (stretch move, default scale), 32 walkers,
  4000 steps per model, one-dimensional posteriors:
  $\log L(\theta) = -\chi^2_{marg}(\theta)/2$ (§6.1) under flat priors. The additive
  offset stays profiled analytically — the identical likelihood object is shared by
  all models.
- **Pre-registered priors (flat, open intervals):**
  - flat ΛCDM: $\Omega_m \in (0.01,\ 1.0)$;
  - Janus: $q_0 \in (q_{0,min}(z_{max}),\ 0) = (-0.221105,\ 0)$ — both bounds are
    the model's validity domain ($q_0 < 0$ from $E < 0$; $1 + 2 q_0 z > 0$), not
    tuning choices. If posterior mass piles up against the $q_0 = 0$ boundary, that
    is itself a result and will be reported as such;
  - Milne: no shape parameter — the posterior is the single point
    $\chi^2 = 1436.665$ (M7, frozen). Documented as trivial; nothing to sample.
- **log-prob hygiene:** $-\infty$ is returned strictly outside the open prior
  *before* the model is evaluated (model validators raise outside their domain by
  design).
- **Seeds (fixed):** ΛCDM 20260610, Janus 20260611. Both the walker initialization
  (uniform over the prior, inset by a relative $10^{-9}$ so no walker starts exactly
  on a boundary — an initialization detail, not a prior change) and the sampler's
  internal random state derive from the seed; chains are bit-reproducible (tested,
  including on a fixed 50-SN subsample of the real data per the SPEC determinism
  requirement).
- **Pre-registered convergence criterion:** $n_{steps} > 50\,\tau$ with $\tau$ the
  integrated autocorrelation time (Sokal estimator, emcee implementation). Failure
  ⇒ the production script STOPs and the failure is reported; no post-hoc loosening.
- **Burn-in / thinning (fixed convention, emcee documentation):**
  burn-in $= \lceil 3\tau \rceil$, thinning $= \max(1, \lfloor \tau/2 \rfloor)$.
- **Cross-validation gate (M8 GO point 3):** posterior std vs the frozen M7
  curvature $\sigma$ — relative difference reported; an absolute relative difference
  above 20% triggers investigation before any contour is published.
- **M7 numbers are frozen** (M8 GO point 4): no re-fit, no re-tuning of §7.

## 7. Results — chi2 stage *(M7, measured 2026-06-10 on this host)*

Sample: 1580 SNe, $z_{HD} \in [0.01016, 2.26137]$, full STAT+SYS covariance, additive
offset profiled analytically (§6.1). `n_params` counts the profiled offset.

| Model | Shape parameter (curvature 1σ) | $\chi^2$ | dof | $\chi^2$/dof |
|---|---|---|---|---|
| Flat ΛCDM | $\Omega_m = 0.331631 \pm 0.018207$ | 1387.099 | 1578 | 0.8790 |
| Janus | $q_0 = -0.021010 \pm 0.014767$ | 1434.719 | 1578 | 0.9092 |
| Milne | (offset only) | 1436.665 | 1579 | 0.9099 |

Arithmetic differences on the shared pipeline:
$\chi^2_{Janus} - \chi^2_{\Lambda CDM} = +47.620$;
$\chi^2_{Milne} - \chi^2_{\Lambda CDM} = +49.566$;
$\chi^2_{Milne} - \chi^2_{Janus} = +1.946$ (Janus has one more fitted parameter than
Milne). Model-comparison statistics (ΔAIC, ΔBIC), residual diagrams and MCMC
posteriors are deferred to M8–M9. For later reference, the 2018 published Janus fit
(different dataset and standardization: JLA, 740 SNe, fixed JLA nuisance parameters)
was $q_0 = -0.087 \pm 0.015$ (§2, eq. 8); the comparison is deferred to M9–M10.

## 8. Known limitations and what this does NOT prove *(seeded at M7; completed at M10)*

- **The released Pantheon+ covariance likely overestimates uncertainties.** Keeley,
  Shafieloo & L'Huillier 2024 (arXiv:2212.07917) find the same $\chi^2 = 1387.10$
  "suspiciously small": none of their 10,000 mock realizations drawn from the
  released covariance reach a $\chi^2$ that low (> 3.9σ), and they attribute it to
  ~7% overestimated distance-modulus errors (the intrinsic-scatter term is tuned to
  reduced $\chi^2 = 1$ *before* the systematic matrix is added). Consequences for
  this project: (a) parameter uncertainties derived with this covariance are
  conservative; (b) $\chi^2/\mathrm{dof} < 1$ is a property of the dataset's
  covariance, not a merit of any model — absolute $\chi^2/\mathrm{dof}$ values must
  not be read as goodness-of-fit evidence; only differences between models on the
  same covariance are meaningful here.
- SNe-only constraints are weak; no CMB/BAO/growth information enters this project.
  *(Full discussion at M10.)*
- Nothing here validates or refutes the Janus model as a whole: this is one
  comparative fit on one dataset. *(Full discussion at M10.)*
