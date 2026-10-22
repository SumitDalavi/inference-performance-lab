# Inference Performance Lab

[![CI Pipeline](https://github.com/SumitDalavi/inference-performance-lab/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/SumitDalavi/inference-performance-lab/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/SumitDalavi/inference-performance-lab?color=0969da&label=release&logo=github)](https://github.com/SumitDalavi/inference-performance-lab/releases)
[![Release Workflow](https://github.com/SumitDalavi/inference-performance-lab/actions/workflows/release.yml/badge.svg)](https://github.com/SumitDalavi/inference-performance-lab/actions/workflows/release.yml)
[![SBOM](https://img.shields.io/badge/SBOM-SPDX%202.3-blueviolet?logo=spdx)](https://github.com/SumitDalavi/inference-performance-lab/releases/tag/v0.2.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> Distributed via GitHub Container Registry (`ghcr.io/sumitdalavi/inference-performance-lab:v0.2.0`) and tagged GitHub Releases with Anchore SPDX 2.3 SBOM and SHA-256 digest attestation.

---

## The Problem
Modern distributed systems and AI agents require robust operational scaffolding. Simple CRUD apps or mock loops fail when subjected to real-world edge cases, asynchronous boundaries, and security constraints.

## The Solution
Runs controlled experiments against an OpenAI-compatible inference server (vLLM as the primary target), collects server and GPU metrics via Prometheus, and produces a findings report with exact environment metadata.

---

## Key Capabilities & Architectural Highlights
- **Streaming Chunk Parser**: Client-perceived Time-to-First-Token (TTFT) and Inter-Token Latency (ITL) measurement.
- **Statistical Distributions**: p50/p95/p99 latency quantiles with finite-value outlier rejection.
- **PyPI Wheel Distribution**: Official `.whl` and `.tar.gz` attached to releases for direct pip installation.
- **Full OCI Distribution**: Published to GitHub Container Registry (GHCR).

## 💻 Tech Stack
- **Container Registry:** `ghcr.io/sumitdalavi/inference-performance-lab:v0.2.0`
- **Security & Attestation:** Anchore SPDX 2.3 SBOM, SHA-256 Checksums
- **License:** MIT Open Source

---

## 📚 Documentation Index
- [Architecture Specification](docs/ARCHITECTURE.md) — System diagram, component contracts, and container distribution architecture.
- [Production Runbook](docs/RUNBOOK.md) — Operational runbook, live execution commands, and verification recipes.
- [Demo Walkthrough](docs/DEMO_SCRIPT.md) — Step-by-step interactive demonstration scenario.
- [Changelog](CHANGELOG.md) — Full version history following Keep a Changelog and SemVer.

---

## 🚀 Quickstart & Installation

### Option 1: Run with Docker Container (GHCR)
```bash
docker pull ghcr.io/sumitdalavi/inference-performance-lab:v0.2.0
docker run -d -p 8000:8000 -p 9090:9090 ghcr.io/sumitdalavi/inference-performance-lab:v0.2.0
```

### Option 2: Install via pip (Python Package Wheel)
```bash
pip install https://github.com/SumitDalavi/inference-performance-lab/releases/download/v0.2.0/inference_performance_lab-0.2.0-py3-none-any.whl

# Run the benchmark CLI:
python -m benchmark --model gemini-2.5-pro --concurrent 10
```

### Option 3: Local Developer Setup
```bash
# 1. Clone the repository
git clone https://github.com/SumitDalavi/inference-performance-lab.git
cd inference-performance-lab

# 2. Build and start
make setup
make dev
```

---

## 🎮 Usage & Demo
See [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) for the interactive walkthrough and verification steps.

## Principles

1. Every result carries metadata: commit SHA, date, GPU model/driver, serving software versions, model identifier/revision, flags, workload definition, seed.
2. Report distributions (p50/p95/p99), not only means; include failed requests.
3. Change one variable at a time.
4. Warm up, then measure; document both.
5. Negative and null results are published.

---

## ✅ Verification

### Operational Verification
| Check | Command | Expected |
|---|---|---|
| Build | `make setup` | Dependencies install successfully |
| Run | `make dev` | Services start without crashing |
| Test | `make test` | Behavioral test suite passes |

### Cryptographic & Supply Chain Verification
To verify the authentic origin, integrity, and software composition of release artifacts:
```bash
# 1. Download Release Bundle & Checksums
gh release download v0.2.0 --repo SumitDalavi/inference-performance-lab --pattern "*.tar.gz" --pattern "checksums.txt"

# 2. Verify SHA-256 Digest
sha256sum -c checksums.txt

# 3. Inspect SPDX 2.3 Software Bill of Materials
gh release download v0.2.0 --repo SumitDalavi/inference-performance-lab --pattern "sbom.spdx.json"
cat sbom.spdx.json | jq .spdxVersion
```

---

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

---

## 🔌 Dual-Mode Execution: Live-First with Graceful Mock Fallback

This platform operates in **Dual-Mode**, dynamically selecting between live LLM inference servers and embedded streaming simulators based on environment variables:

| Component | Environment Variable | Live Mode Behavior | Fallback Mode (Unset / Empty) |
|---|---|---|---|
| **Inference Server** | `INFERENCE_ENDPOINT` | Streams tokens from live vLLM, Ollama, TGI, or OpenAI-compatible endpoint | Binds to bundled FastAPI streaming simulation harness on port `8080` |
| **Serving Model** | `INFERENCE_MODEL` | Requests specific target model (e.g. `meta-llama/Llama-3-8B-Instruct`) | Defaults to lightweight test model identifier (`facebook/opt-125m`) |
| **Authentication** | `INFERENCE_AUTH_TOKEN` | Injects Authorization Bearer header for protected cloud endpoints | Runs unauthenticated against local test servers |
| **Metrics Collector** | `PROMETHEUS_PORT` | Exposes metrics on custom port for Prometheus scrape scraping | Binds metrics exporter to default port `8000` |

---

## 👨‍💻 Author
**Sumit Dalavi** — Senior DevSecOps / Platform Engineer  
[GitHub](https://github.com/SumitDalavi) | [LinkedIn](https://in.linkedin.com/in/sumit-dalavi-762838129)

---

## 📄 License
This project is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Sumit Dalavi.