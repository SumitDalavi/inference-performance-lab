# inference-performance-lab

> A reproducible lab for understanding LLM serving behavior: how configuration, workload shape, and speculative decoding change latency, throughput, queueing, and resource use.

Runs controlled experiments against an OpenAI-compatible inference server (vLLM as the primary target), collects server and GPU metrics via Prometheus, and produces a findings report with exact environment metadata.

**Status: personal portfolio project. All numbers in the report come from `results/` produced by the harness; none are asserted in this README.**

## Capability status

| Capability | Status |
|---|---|
| Declarative experiment definitions | Implemented |
| Load generator wrapper (open-loop and closed-loop) | Implemented |
| Workload library (short chat, long prompt, long output, mixed, shared-prefix) | Implemented |
| vLLM deployment recipes (single GPU) | Implemented |
| Prometheus + Grafana + GPU metrics | Implemented |
| Speculative decoding experiments | Planned (model/method support must be verified) |
| Result store + comparison reports | Implemented |
| Goodput / SLO analysis | Implemented |
| Cost-per-token estimator (explicit assumptions) | Implemented |
| Multi-replica / disaggregated serving (e.g., llm-d) | Stretch; not in MVP |

## Principles
1. Every result carries metadata: commit SHA, date, GPU model/driver, serving software versions, model identifier/revision, flags, workload definition, seed.
2. Report distributions (p50/p95/p99), not only means; include failed requests.
3. Change one variable at a time.
4. Warm up, then measure; document both.
5. Negative and null results are published.

## Docs
[Architecture](docs/ARCHITECTURE.md) | [Demo](docs/DEMO_SCRIPT.md)

