"""Frozen measured results, single source of truth for scripts and tests.

Every value here was measured in this repository and recorded in RESULTS.md before
being frozen (M7: section 7.1, commit 7809067; M8: section 7.2, commit 661038d).
The freeze rule (M8 GO point 4) forbids re-fitting or re-tuning them; downstream
stages (model comparison, plots, tests) must import these constants instead of
re-deriving or duplicating them.
"""

M7_LCDM_OMEGA_M = 0.331631
M7_LCDM_SIGMA = 0.018207
M7_LCDM_CHI2 = 1387.099

M7_JANUS_Q0 = -0.021010
M7_JANUS_SIGMA = 0.014767
M7_JANUS_CHI2 = 1434.719

M7_MILNE_CHI2 = 1436.665

N_SNE = 1580
"""Cosmology sample size after the zHD > 0.01 and calibrator cuts (RESULTS.md §4)."""

N_PARAMS = {"FlatLCDM": 2, "Janus": 2, "Milne": 1}
"""Fitted parameters per model, counting the analytically profiled offset."""
