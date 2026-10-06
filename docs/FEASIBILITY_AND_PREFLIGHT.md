# Feasibility and Preflight — Inference Performance Lab (INF)

## Purpose
Before any implementation begins, verify that all prerequisites are met. Record a GO or HOLD decision.

## Hardware and environment
- [ ] GPU access confirmed: _____________ (model, VRAM, driver version)
- [ ] OR GPU rental plan documented: _____________ (provider, budget, timeline)
- [ ] Python 3.12+ with `uv` available
- [ ] Docker / container runtime installed and functional

## Inference server
- [ ] vLLM version pinned from current stable release: _____________
- [ ] vLLM benchmark CLI arguments verified from official docs
- [ ] vLLM metric names verified from https://docs.vllm.ai/en/stable/design/metrics/
- [ ] Speculative decoding method support verified for chosen model

## Metrics stack
- [ ] Prometheus can run locally
- [ ] Grafana available
- [ ] GPU metrics exporter (dcgm-exporter or nvidia-smi-exporter) available

## Model
- [ ] Model identifier and revision pinned: _____________
- [ ] Model license reviewed and compatible
- [ ] HuggingFace token available if required (never committed)

## Budget
- [ ] GPU cost estimate documented: _____________
- [ ] No other cloud spending required

## CI constraints
- [ ] CI tests use mock OpenAI-compatible server (no GPU in CI)
- [ ] Real benchmark runs happen on GPU host via `make eval`

## Tools
- [ ] `make`, `docker compose`, `ruff`, `pytest` available

## Decision
- [ ] **GO** — all prerequisites met, proceed to INF-01
- [ ] **HOLD** — blocker identified: _________________
