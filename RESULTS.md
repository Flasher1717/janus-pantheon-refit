# Results — Independent refit of the Janus cosmological model on Pantheon+ SNe Ia

> **Status: in progress.** This document is written incrementally as the project advances.
> No fit has been run yet. Sections below marked *(pending)* will be filled once the
> corresponding milestone is complete. The result — whatever it is — will be reported as-is.

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
  $q_0 = 0$); if adopted as the production evaluator at the fit stage, its derivation
  will be recorded here.
- **Domain bound exported.** The prior bound $q_0 > -1/(2 z_{max})$ (§3) is exposed as
  `janus_q0_min(z_max)` so the M7/M8 prior and the model validator share one source of
  truth; a test checks it sits exactly on the domain edge.
- **Performance caveat (deferred to M7/M8):** `lcdm_mu` integrates with `scipy` `quad`
  per redshift — accurate but too slow for ~1e5 MCMC likelihood calls on 1580 SNe
  (measured 16.4 ms/call). The fit stage will use a vectorized fixed-order
  Gauss–Legendre rule mapped onto each $[0, z_i]$ (review measurement: 12 nodes agree
  with the quad oracle to 8.5e-14 mag at ~40× the speed), pinned against this oracle
  at the same < 1e-6 mag gate.

## 6. Fit methodology *(pending — will document χ², marginalization, MCMC settings)*

## 7. Results *(pending)*

## 8. Known limitations and what this does NOT prove *(pending — will include at minimum:
SNe-only constraints are weak; no CMB/BAO/growth; no statement of validation or
refutation of the Janus model as a whole)*
