# janus-refit

[![ci](https://github.com/Flasher1717/janus-pantheon-refit/actions/workflows/ci.yml/badge.svg)](https://github.com/Flasher1717/janus-pantheon-refit/actions/workflows/ci.yml)

**→ Full methodology and results: [RESULTS.md](RESULTS.md)**

An independent, open-source refit of the **Janus cosmological model** supernovae Ia
Hubble diagram (D'Agostini & Petit 2018) on the modern **Pantheon+** compilation
(1701 light curves) with the full STAT+SYS covariance — compared head-to-head, with the
same data and the same pipeline, against flat ΛCDM (reference) and the empty Milne
universe (over-interpretation guard).

This is a scientific-integrity project: the outcome — favorable or not to any model —
is published as-is. See [RESULTS.md](RESULTS.md) for the extracted model equations
(with page-level provenance), methodology, and results. No conclusion of the form
"model X is validated/refuted" is drawn: this is one comparative fit on one dataset.

## Status

Analysis complete (milestones M0–M10): chi-square fits, MCMC posteriors and model
comparison are done and reported in [RESULTS.md](RESULTS.md). Milestone history in
[MILESTONES.md](MILESTONES.md) and [PROGRESS.md](PROGRESS.md).

## Quickstart

Requires Python ≥ 3.12 and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run python scripts/download_data.py   # one-time network step (SHA256-verified)
uv run pytest
```

The Pantheon+ files land in `data/` (gitignored, ~34 MB). Everything after the
download runs offline.

## Layout

- `src/janus_refit/` — typed library (pyright strict): data pipeline, models,
  likelihood, fitting, MCMC, comparison, frozen reference values
- `scripts/` — `download_data.py` (the only network step), then `run_fits.py`,
  `run_mcmc.py`, `run_comparison.py` (offline, in milestone order)
- `tests/` — pytest suite; data-dependent tests skip when `data/` is absent
- `figures/` — corner plots and Hubble-diagram residuals (committed outputs)
- `RESULTS.md` — equations as extracted from the source papers, methodology, results

## Transparency

This codebase is developed AI-assisted (Claude Code), with human review and a
verification-first workflow: model equations were extracted from the source papers
(never from memory), cross-checked between the 2018 and 2024 papers, and validated by
blind re-extraction and numerical consistency checks before any fitting code was
written. Sources: D'Agostini & Petit (2018), Astrophys. Space Sci. 363:139;
Petit, Margnat & Zejli (2024), Eur. Phys. J. C 84:1226; Pantheon+ data release
([PantheonPlusSH0ES/DataRelease](https://github.com/PantheonPlusSH0ES/DataRelease)).

## License

[MIT](LICENSE)
