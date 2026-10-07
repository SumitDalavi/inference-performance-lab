# Demo Script

1. **Start the Stack**: Run `make dev` in the root.
   - This starts Prometheus, Grafana, the mock SSE server (8080), and runs the benchmark script.
2. **Open Grafana**: 
   - Navigate to http://localhost:3000.
3. **Explore Metrics**: 
   - Use the Explore tab to query `llm_ttft_seconds_bucket` or `llm_itl_seconds_bucket`.
   - Observe how the async load generator correctly records the initial 200ms TTFT and the subsequent 45ms ITL chunks.
4. **Change Modes**:
   - Modify `config/test.yaml` to switch from `closed-loop` to `open-loop` or adjust `concurrency`.
   - Run `make dev` again to observe how the latency distributions change under different load patterns.
