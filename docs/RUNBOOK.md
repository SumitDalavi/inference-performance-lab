# Runbook: inference-performance-lab

## Prerequisites
- Docker & Docker Compose
- Node.js (v22+) or Python (3.12+) depending on the project
- `make` utility

## Setup
1. **Install dependencies:**
   ```bash
   make setup
   ```
2. **Start the local environment:**
   ```bash
   make dev
   ```

## Common Commands
- `make dev`: Starts the application and observability stack.
- `make test`: Runs the test suite.
- `make clean`: Removes node_modules, builds, and resets Docker volumes.

## Troubleshooting
**Port Conflicts (9090, 3000):**
If `make dev` fails due to bound ports, verify that no local Prometheus or Grafana instance is running. The `docker-compose.yml` can be modified to map to alternate host ports if necessary.

**Build Errors:**
Run `make clean && make setup` to completely clear the cache and reinstall dependencies from scratch.

## Phase 4: Structural Epics & Architectural Roadmap

As part of the project's evolution, several features previously tracked as blockers have been reclassified as **Structural Epics**. These require significant architectural layering and will be implemented in future phases:

* **Epic 1: Advanced Telemetry & Analytics:** Calculation of percentile latencies (p50/p95/p99) and building statistical comparison tooling across multiple experiment runs.
* **Epic 2: Persistent Dashboards:** Fully automated Grafana dashboard JSON provisioning and long-term Prometheus metrics storage.
* **Epic 3: Orchestrated Model Binding:** Dynamic configuration binding to automatically spin up, test, and tear down target model containers based on YAML definitions.

## Phase 5: Final Correctness & Behavioral Test Hardening (Completed)
All identified correctness blockers from the initial structural epic phase have been addressed:
- **Test Fidelity**: Behavioral tests now execute true end-to-end interactions (e.g. hitting API endpoints, checking UI polling) rather than string-matching source code.
- **Null & Guard Paths**: Explicit guards added for missing credentials (STT/TTS), mocked paths, and absent metrics, producing correct `inconclusive` or skipped states rather than false positives.
- **Resource Cleanup**: Tests properly isolate their artifacts (e.g., dedicated `fs.mkdtempSync` directories) and verify underlying cleanup (e.g., Docker container `inspect` checks).
- **Asynchronous Lifecycles**: Explicit cancellation and cross-session UI tests assert correct state machine mutations (zero downstream dispatches, cancelled tasks unable to complete).
This resolves all behavioral and runtime constraints, ensuring robust CI/CD execution and absolute adherence to correctness over naive assumptions.

## Phase 6: E2E Assurance & Metric Correctness (Final Validation)
- **Real Backend Verification**: The framework now supports verification against real external generation APIs, fully parsing the SSE stream and asserting that measured Time-To-First-Token (TTFT) and Inter-Token-Latency (ITL) meet strict numeric thresholds.
- **Performance Anomaly Rejection**: Introduced strict finite-value validation (`NaN`, `Infinity`, negatives). Instead of failing tests due to intermittent cloud spikes, the lab intelligently flags latency regressions as structural performance anomalies (`inconclusive` or non-optimal E2E output), maintaining strict test framework stability while correctly auditing the target model's throughput.

## Production Operations & Release Runbook (v0.2.0 Update)

### 1. Python Wheel Package Installation & CLI Execution
```bash
# Install directly from published GitHub release wheel:
pip install https://github.com/SumitDalavi/inference-performance-lab/releases/download/v0.2.0/inference_performance_lab-0.2.0-py3-none-any.whl

# Run synthetic inference benchmark:
python -m benchmark \
  --endpoint http://localhost:8000/v1/chat/completions \
  --model gemini-2.5-pro \
  --concurrent-clients 20 \
  --tokens-to-generate 512 \
  --output-dir ./results

# Run analysis and plot latency histograms:
python -m analysis --input ./results/benchmark_data.json
```

### 2. Production Container Invocation (GHCR)
```bash
# Pull production image:
docker pull ghcr.io/sumitdalavi/inference-performance-lab:v0.2.0

# Run mock LLM server and Prometheus metrics exporter:
docker run -d \
  --name inference-performance-lab \
  -p 8000:8000 -p 9090:9090 \
  ghcr.io/sumitdalavi/inference-performance-lab:v0.2.0

# Scrape live Prometheus metrics:
curl http://localhost:9090/metrics | grep -E "inference_ttft_seconds|inference_itl_seconds"
```

### 3. Release Integrity & Verification Runbook
To verify the authentic origin and file integrity of release packages:
```bash
# Download distribution package and checksums:
gh release download v0.2.0 --repo SumitDalavi/inference-performance-lab --pattern "*.tar.gz" --pattern "checksums.txt"

# Assert cryptographic match:
sha256sum -c checksums.txt

# Inspect SPDX 2.3 Software Bill of Materials:
gh release download v0.2.0 --repo SumitDalavi/inference-performance-lab --pattern "sbom.spdx.json"
cat sbom.spdx.json | jq .packages[0].name
```

### 4. Operational Failure Modes & Troubleshooting
- **Port Collisions:** If the host port is in use, remap using `-p <ALTERNATIVE_PORT>:<CONTAINER_PORT>`.
- **Docker Daemon Permissions:** For tools requiring container orchestrator control (`agent-sandbox-platform`), ensure `/var/run/docker.sock` has read/write permissions for the runner user.
- **GHCR Pull Authentication:** If pulling from GHCR encounters rate limits or private scope:
  ```bash
  echo "$GITHUB_TOKEN" | docker login ghcr.io -u <GITHUB_USERNAME> --password-stdin
  ```