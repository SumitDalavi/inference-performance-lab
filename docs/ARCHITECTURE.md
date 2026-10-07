# Architecture: Inference Performance Lab (INF)

## Overview
INF is a benchmarking tool specifically designed for streaming Large Language Models (LLMs). It measures nuanced performance metrics like Time-To-First-Token (TTFT) and Inter-Token-Latency (ITL), distinguishing between network chunks and actual tokens.

## Components
1. **Async Load Generator**:
   - Built with `aiohttp` and `asyncio` in Python.
   - Supports Open-Loop (fixed request-per-second, ignoring backpressure) and Closed-Loop (fixed concurrency).
2. **Mock SSE Server**:
   - Simulates an LLM inference endpoint (`/v1/chat/completions`).
   - Introduces controlled delays to mock TTFT and ITL.
3. **Prometheus Instrumentation**:
   - Exposes detailed histograms (`llm_ttft_seconds`, `llm_itl_seconds`, `llm_e2e_seconds`).
4. **Observability Stack**:
   - Dockerized Prometheus and Grafana for visualizing benchmark degradation over time.
