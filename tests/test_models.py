import numpy as np
import pytest
from oracles import astropy_empty_universe_mu, astropy_flat_lcdm_mu

from janus_refit._types import FloatArray
from janus_refit.models import (
    janus_mu_mattig,
    janus_mu_terrell,
    janus_q0_min,
    lcdm_mu,
    milne_mu,
)

H0_REF = 70.0

Z_GRID: FloatArray = np.geomspace(0.01, 2.3, 200)
Z_GRID.flags.writeable = False

FINE_GRID: FloatArray = np.geomspace(0.01, 2.3, 2000)
FINE_GRID.flags.writeable = False


class TestLcdmOracle:
    """M5 gate: |mu_ours - mu_astropy| < 1e-6 mag on z in [0.01, 2.3]."""

    @pytest.mark.parametrize(
        ("omega_m", "h0"),
        [(0.2, 67.0), (0.3, 70.0), (0.334, 73.0), (0.5, 70.0), (1.0, 70.0)],
    )
    def test_against_astropy(self, omega_m: float, h0: float) -> None:
        ours = lcdm_mu(Z_GRID, omega_m, h0)
        reference = astropy_flat_lcdm_mu(Z_GRID, omega_m, h0)
        assert float(np.max(np.abs(ours - reference))) < 1e-6

    def test_rejects_negative_omega_m(self) -> None:
        with pytest.raises(ValueError, match="omega_m"):
            lcdm_mu(Z_GRID, -0.1, H0_REF)


class TestJanusForms:
    """M6 gate: the two published algebraic forms agree to < 1e-12 relative."""

    def test_forms_agree_on_grid(self) -> None:
        worst = 0.0
        for q0 in np.linspace(-0.21, -0.01, 201):
            terrell = janus_mu_terrell(Z_GRID, float(q0), H0_REF)
            mattig = janus_mu_mattig(Z_GRID, float(q0), H0_REF)
            worst = max(worst, float(np.max(np.abs(mattig - terrell) / np.abs(terrell))))
        assert worst < 1e-12

    def test_printed_form_28_matches_within_its_cancellation_floor(self) -> None:
        """The verbatim eq. (28) bracket loses ~6e-11 relative precision in float64
        at small |q0| z (catastrophic cancellation), which is why janus_mu_mattig
        evaluates it through the exact conjugate identity. This regression test pins
        the printed form to the implementation within that measured floor.
        """
        worst = 0.0
        for q0 in np.linspace(-0.21, -0.01, 51):
            root = np.sqrt(1.0 + 2.0 * q0 * Z_GRID)
            printed = (q0 * Z_GRID + (1.0 - q0) * (1.0 - root)) / q0**2
            stable = Z_GRID * (root - 1.0 + 2.0 * q0) / (q0 * (1.0 + root))
            worst = max(worst, float(np.max(np.abs(printed - stable) / np.abs(stable))))
        assert worst < 1e-9

    @pytest.mark.parametrize("q0", [-1e-4, -1e-6, -1e-8])
    def test_mattig_residual_cancellation_floor_at_small_q0(self, q0: float) -> None:
        """The stabilized Mattig form keeps a sqrt(1+eps)-1 cancellation as q0 -> 0^-:
        |mu_mattig - mu_terrell| grows like eps_machine/|q0| (measured 8.9e-9 mag at
        q0 = -1e-8, coefficient ~0.9e-16). The bound asserts 1e-15/|q0| (~10x margin).
        This is why the Milne-nesting tests use the Terrell form, which is regular
        at q0 = 0.
        """
        delta = janus_mu_mattig(Z_GRID, q0, H0_REF) - janus_mu_terrell(Z_GRID, q0, H0_REF)
        assert float(np.max(np.abs(delta))) < 1e-15 / abs(q0)


class TestMilneNesting:
    """M6 gate: mu_Janus(q0 -> 0^-) converges to mu_Milne.

    Leading order of the eq. (29) bracket around q0 = 0:
    bracket(q0) - bracket(0) = -q0 z^2 (1+z)/2 + O(q0^2), hence
    |Delta mu| ~= (5/ln 10) |q0| z(1+z)/(2+z) <= 3.9e-8 mag for q0 = -1e-8, z <= 2.3.
    The assertions use 2.5x margins on these analytic bounds.
    """

    def test_convergence_at_q0_1e8(self) -> None:
        delta = janus_mu_terrell(Z_GRID, -1e-8, H0_REF) - milne_mu(Z_GRID, H0_REF)
        assert float(np.max(np.abs(delta))) < 1e-7

    def test_convergence_is_first_order_in_q0(self) -> None:
        delta_small = float(
            np.max(np.abs(janus_mu_terrell(Z_GRID, -1e-8, H0_REF) - milne_mu(Z_GRID, H0_REF)))
        )
        delta_large = float(
            np.max(np.abs(janus_mu_terrell(Z_GRID, -1e-6, H0_REF) - milne_mu(Z_GRID, H0_REF)))
        )
        assert 80.0 < delta_large / delta_small < 120.0

    def test_milne_against_astropy_empty_universe(self) -> None:
        reference = astropy_empty_universe_mu(Z_GRID, H0_REF)
        ours = milne_mu(Z_GRID, H0_REF)
        assert float(np.max(np.abs(ours - reference))) < 1e-6


class TestJanusDomain:
    def test_rejects_zero_q0(self) -> None:
        with pytest.raises(ValueError, match="q0 < 0"):
            janus_mu_terrell(Z_GRID, 0.0, H0_REF)

    def test_rejects_positive_q0(self) -> None:
        with pytest.raises(ValueError, match="q0 < 0"):
            janus_mu_mattig(Z_GRID, 0.05, H0_REF)

    def test_rejects_q0_violating_root_positivity(self) -> None:
        with pytest.raises(ValueError, match="must stay positive"):
            janus_mu_terrell(Z_GRID, -0.25, H0_REF)

    def test_q0_min_is_the_exact_domain_edge(self) -> None:
        bound = janus_q0_min(float(Z_GRID.max()))
        assert bound == -0.5 / 2.3
        janus_mu_terrell(Z_GRID, bound * 0.999, H0_REF)
        for q0 in (bound, bound * 1.001):
            with pytest.raises(ValueError, match="must stay positive"):
                janus_mu_terrell(Z_GRID, q0, H0_REF)

    def test_rejects_non_positive_redshift(self) -> None:
        bad = np.array([0.0, 0.1])
        with pytest.raises(ValueError, match="strictly positive"):
            janus_mu_terrell(bad, -0.1, H0_REF)
        with pytest.raises(ValueError, match="strictly positive"):
            milne_mu(bad, H0_REF)
        with pytest.raises(ValueError, match="strictly positive"):
            lcdm_mu(bad, 0.3, H0_REF)

    def test_rejects_empty_or_multidimensional_redshifts(self) -> None:
        empty = np.array([], dtype=np.float64)
        square = np.ones((2, 2))
        for bad in (empty, square):
            with pytest.raises(ValueError, match="one-dimensional and non-empty"):
                janus_mu_terrell(bad, -0.1, H0_REF)
            with pytest.raises(ValueError, match="one-dimensional and non-empty"):
                lcdm_mu(bad, 0.3, H0_REF)

    @pytest.mark.parametrize("h0", [0.0, -70.0])
    def test_rejects_non_positive_h0(self, h0: float) -> None:
        with pytest.raises(ValueError, match="h0 must be positive"):
            janus_mu_terrell(Z_GRID, -0.1, h0)
        with pytest.raises(ValueError, match="h0 must be positive"):
            janus_mu_mattig(Z_GRID, -0.1, h0)
        with pytest.raises(ValueError, match="h0 must be positive"):
            milne_mu(Z_GRID, h0)
        with pytest.raises(ValueError, match="h0 must be positive"):
            lcdm_mu(Z_GRID, 0.3, h0)


class TestShapeRegularity:
    """M6 gate: mu(z) finite, strictly increasing, and continuous on the domain.

    Continuity check for Janus: each grid step is compared against the analytic
    derivative bound. From the eq. (26)/(28) d_L bracket f(z) (the eq. (26) form with
    its 1/(1+z) removed by d_L = a0 r (1+z)), f'(z) = (s - 1 + q0)/(q0 s)
    with s = sqrt(1 + 2 q0 z), so d mu / d ln z = (5/ln 10) z f'/f. On a log grid
    of step h, |mu_{i+1} - mu_i| <= max(d_i, d_{i+1}) * h * (1 + 5% curvature slack).
    The derivative grows like 1/s near the domain edge (q0 = -0.21, z = 2.3 gives
    d ~= 11.6 mag per e-fold), which a fixed threshold would miss.
    """

    @pytest.mark.parametrize("q0", [-0.21, -0.087, -0.01])
    def test_janus_monotonic_finite_continuous(self, q0: float) -> None:
        z = FINE_GRID
        root = np.sqrt(1.0 + 2.0 * q0 * z)
        f = z * (root - 1.0 + 2.0 * q0) / (q0 * (1.0 + root))
        f_prime = (root - 1.0 + q0) / (q0 * root)
        dmu_dlnz = (5.0 / np.log(10.0)) * z * f_prime / f
        log_step = float(np.log(z[1] / z[0]))
        step_bound = np.maximum(dmu_dlnz[:-1], dmu_dlnz[1:]) * log_step * 1.05

        for form in (janus_mu_terrell, janus_mu_mattig):
            mu = form(z, q0, H0_REF)
            assert bool(np.isfinite(mu).all())
            steps = np.diff(mu)
            assert bool((steps > 0.0).all())
            assert bool((steps <= step_bound).all())

    def test_lcdm_and_milne_monotonic_finite_continuous(self) -> None:
        for mu in (lcdm_mu(FINE_GRID, 0.3, H0_REF), milne_mu(FINE_GRID, H0_REF)):
            assert bool(np.isfinite(mu).all())
            steps = np.diff(mu)
            assert bool((steps > 0.0).all())
            assert float(steps.max()) < 0.02
