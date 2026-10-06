# AGENTS.md: instructions for coding agents

## Mission
Build `inference-performance-lab`: reproducible LLM-serving experiments with trustworthy measurement.

## Hard rules
1. **Never fabricate or "illustrate" benchmark numbers.** Reports are generated only from files in `results/raw/`. Test fixtures with fake numbers must live under `tests/fixtures/` and be labeled `SYNTHETIC` in the file name and content.
2. **Verify tooling from current official docs** at implementation time: server flags, benchmark CLI arguments, metric names, speculative-decoding method support for the chosen model. Record versions and date in `docs/DECISIONS.md`. Flags change between releases.
3. **Reproducibility metadata is mandatory** in every result file (see ARCHITECTURE section 6). A run without metadata is invalid and rejected by the loader.
4. **One variable at a time.** The experiment schema enforces a declared `independent_variable`.
5. **No GPU in CI.** CI uses a mock OpenAI-compatible server for harness tests. Real runs happen on a GPU host via `make eval`.
6. Treat third-party/vendor numbers as vendor numbers; never mix them into your results tables.
7. Keep generated charts reproducible from raw data via a script.

## Layout
```text
experiments/        YAML experiment definitions
workloads/          prompt/output length distributions, datasets (small, licensed or synthetic)
harness/            Python: runner, client, metrics collector, result writer
deploy/             compose/k8s recipes for server + prometheus + grafana + gpu exporter
analysis/           notebooks/scripts to produce tables and charts from results/raw
results/raw/        immutable run outputs (JSON + metadata)
results/reports/    generated reports
tests/              unit + mock-server tests
```
