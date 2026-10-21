# Inference Performance Lab

[![CI Pipeline](https://github.com/SumitDalavi/inference-performance-lab/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/SumitDalavi/inference-performance-lab/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/SumitDalavi/inference-performance-lab?color=0969da&label=release&logo=github)](https://github.com/SumitDalavi/inference-performance-lab/releases)
[![Release Workflow](https://github.com/SumitDalavi/inference-performance-lab/actions/workflows/release.yml/badge.svg)](https://github.com/SumitDalavi/inference-performance-lab/actions/workflows/release.yml)
[![SBOM](https://img.shields.io/badge/SBOM-SPDX%202.3-blueviolet?logo=spdx)](https://github.com/SumitDalavi/inference-performance-lab/releases/tag/v0.2.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> Benchmarking and profiling suite for LLM inference serving, measuring streaming response latencies, Time-to-First-Token (TTFT), and token generation throughput across configurable concurrent client workloads.

---

## Key Capabilities & Architectural Highlights
- **Streaming**: response chunk parser measuring client-perceived TTFT and Inter-Token Latency (ITL)
- **Statistical**: percentile distributions (p50/p95/p99) with finite-value outlier guards
- **Published**: distribution wheel (`.whl`) and sdist (`.tar.gz`) for instant pip installation
- **Full**: OCI container distribution via GitHub Container Registry (GHCR)

## Technology Stack
- **Languages & Frameworks:** Python 3.12, uv, aiohttp, prometheus_client, PyYAML, Docker
- **Container Registry:** `ghcr.io/sumitdalavi/inference-performance-lab:v0.2.0`
- **License:** MIT Open Source

---

## Documentation Index
- [Architecture Specification](docs/ARCHITECTURE.md) — Detailed system diagrams, state machines, and design contracts.
- [Production Runbook](docs/RUNBOOK.md) — Deployment instructions, configuration options, and operations.
- [Demo Script & Walkthrough](docs/DEMO_SCRIPT.md) — Step-by-step verification scenario.
- [Changelog](CHANGELOG.md) — Full release notes and version history.

---

## Quickstart & Installation

### Option 1: Run with Docker Container (GHCR)
```bash
docker pull ghcr.io/sumitdalavi/inference-performance-lab:v0.2.0
docker run -d -p 8000:8000 -p 9090:9090 ghcr.io/sumitdalavi/inference-performance-lab:v0.2.0
```

### Option 2: Install via pip (Python Package Wheel)
```bash
pip install https://github.com/SumitDalavi/inference-performance-lab/releases/download/v0.2.0/inference_performance_lab-0.2.0-py3-none-any.whl

# Run the benchmark CLI:
inference-benchmark --help
```

### Option 3: Local Developer Setup
```bash
git clone https://github.com/SumitDalavi/inference-performance-lab.git
cd inference-performance-lab
make setup
make test
```

---

## Release & Security Verification

This repository adheres to the Portfolio Release Standard with verifiable supply-chain security attestations:

- **Distribution Archive:** `inference-performance-lab-v0.2.0.tar.gz`
- **SHA-256 Digest:** `a11bac3dcf8fec11b5a1faab11dfc86d94574fc1620d4198f447347fb6a60e72`
- **Software Bill of Materials (SBOM):** Anchore SPDX 2.3 JSON specification (`sbom.spdx.json`).

### Verification Commands
```bash
# 1. Download Release Bundle & Checksums
gh release download v0.2.0 --repo SumitDalavi/inference-performance-lab --pattern "*.tar.gz" --pattern "checksums.txt"

# 2. Verify Cryptographic Integrity
sha256sum -c checksums.txt

# 3. Inspect SPDX SBOM
gh release download v0.2.0 --repo SumitDalavi/inference-performance-lab --pattern "sbom.spdx.json"
cat sbom.spdx.json | jq .spdxVersion
```

---

## License
MIT License. Copyright (c) 2026 Sumit Dalavi.
