# inference-performance-lab

> **Maturity:** Fully functional E2E Portfolio Project
> A reproducible lab for understanding LLM serving behavior: how configuration, workload shape, and speculative decoding change latency, throughput, queueing, and resource use.

## The Problem
Modern distributed systems and AI agents require robust operational scaffolding. Simple CRUD apps or mock loops fail when subjected to real-world edge cases, asynchronous boundaries, and security constraints.

## The Solution
Runs controlled experiments against an OpenAI-compatible inference server (vLLM as the primary target), collects server and GPU metrics via Prometheus, and produces a findings report with exact environment metadata.

## 💻 Tech Stack
- **Core Technology**: Python, asyncio, Docker
- **Architecture**: Microservices, Event-Driven

## 📚 Documentation
- [Architecture](docs/ARCHITECTURE.md) — System diagram and component details
- [Runbook](docs/RUNBOOK.md) — Setup, commands, and expected outputs
- [Demo](docs/DEMO_SCRIPT.md) — Walkthrough scenario

## 🚀 Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/SumitDalavi/inference-performance-lab.git
cd inference-performance-lab

# 2. Build and start
make setup
make dev
```

## 💻 Usage & Demo
See the [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) for the interactive walkthrough and verification steps.

## ✅ Verification

| Check | Command | Expected |
|-------|---------|----------|
| Build | `make setup` | Dependencies install successfully |
| Run | `make dev` | Services start without crashing |

## Capability Status
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

## 👨‍💻 Author
**Sumit Dalavi** — Senior DevSecOps / Platform Engineer
[GitHub](https://github.com/SumitDalavi) | [LinkedIn](https://in.linkedin.com/in/sumit-dalavi-762838129)

---
*Built with a focus on robust patterns, not toy demos.*


## October 2026 Update: Behavioral Testing & Runtime Stabilization

**Implementation Notes:**
Updated Grafana provisioning paths, configured prometheus.yml scrape targets, and implemented behavioral simulation in benchmark.py.

* Acceptance tests have been upgraded from static string-checks to end-to-end behavioral verifications.
* API boundaries and execution layers (Docker, WebSockets, Temporal, etc.) are now explicitly exercised in tests.
