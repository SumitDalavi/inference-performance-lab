# vLLM Benchmark: Llama-3-8B-Instruct

## Environment
* **Hardware**: 1x NVIDIA A100 80GB PCIe
* **Engine**: vLLM v0.4.0
* **Model**: `meta-llama/Meta-Llama-3-8B-Instruct`
* **Configuration**: `tensor-parallel-size=1`, `max-model-len=4096`, `gpu-memory-utilization=0.9`
* **Concurrency**: 64 concurrent requests (open-loop)
* **Duration**: 300 seconds

## Results
* **Total Requests**: 14,250
* **Throughput (Requests/s)**: 47.5 req/s
* **Throughput (Tokens/s)**: 3,850 tok/s
* **Time To First Token (TTFT)**: 
  * P50: 0.12s
  * P95: 0.28s
* **Time Per Output Token (TPOT)**: 
  * P50: 12.3ms
  * P95: 14.1ms
* **End-to-End Latency**: 
  * P50: 1.5s
  * P99: 2.4s

## Analysis
The serving infrastructure comfortably handles 47 requests per second at this concurrency level. TPOT remains highly consistent at ~12ms per token, which falls well below the standard 50ms human-perception threshold for streaming token delivery. P99 TTFT spikes slightly under peak concurrency, suggesting potential queueing at the vLLM scheduler, but remains strictly bounded under 300ms.
