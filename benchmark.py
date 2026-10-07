import asyncio
import time
import argparse
import yaml
import aiohttp
import json
import random
from prometheus_client import start_http_server, Histogram, Counter

# Metrics
TTFT = Histogram('llm_ttft_seconds', 'Time To First Token', buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0])
ITL = Histogram('llm_itl_seconds', 'Inter-Token Latency (per chunk)', buckets=[0.01, 0.02, 0.05, 0.1, 0.2])
E2E_LATENCY = Histogram('llm_e2e_seconds', 'End to End Request Latency', buckets=[0.5, 1.0, 2.0, 5.0, 10.0])
REQUESTS = Counter('llm_requests_total', 'Total Requests', ['status'])
TPOT = Histogram('llm_tpot_seconds', 'Time Per Output Token', buckets=[0.01, 0.02, 0.05, 0.1, 0.2])

results_log = []

async def make_request(session, url, prompt, auth_headers, model):
    start_time = time.monotonic()
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": 100,
        "stream_options": {"include_usage": True}
    }
    
    try:
        async with session.post(url, json=payload, headers=auth_headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
            if response.status != 200:
                text = await response.text()
                print(f"Error {response.status}: {text}")
                REQUESTS.labels(status='error').inc()
                results_log.append({"success": False, "error": f"HTTP {response.status}: {text}"})
                return

            first_chunk_time = None
            last_chunk_time = None
            chunk_count = 0
            token_count = 0
            
            async for line in response.content:
                line = line.strip()
                if not line or line.startswith(b':'):
                    continue
                if line == b'data: [DONE]':
                    break
                if line.startswith(b'data: '):
                    try:
                        data = json.loads(line[6:])
                        choices = data.get('choices', [])
                        if choices and choices[0].get('delta', {}).get('content'):
                            chunk_count += 1
                            now = time.monotonic()
                            if first_chunk_time is None:
                                first_chunk_time = now
                                TTFT.observe(first_chunk_time - start_time)
                            else:
                                ITL.observe(now - last_chunk_time)
                            last_chunk_time = now
                        
                        usage = data.get('usage')
                        if usage and usage.get('completion_tokens'):
                            token_count = usage.get('completion_tokens')
                    except json.JSONDecodeError:
                        pass
            
            if chunk_count == 0:
                raise Exception("Empty stream received")

            end_time = time.monotonic()
            e2e = end_time - start_time
            E2E_LATENCY.observe(e2e)
            
            tpot = None
            if token_count > 1:
                tpot = (end_time - first_chunk_time) / (token_count - 1) if first_chunk_time else 0
                TPOT.observe(tpot)
                
            REQUESTS.labels(status='success').inc()
            results_log.append({
                "prompt_length": len(prompt),
                "chunks": chunk_count,
                "tokens": token_count if token_count > 0 else None,
                "ttft": (first_chunk_time - start_time) if first_chunk_time else 0,
                "tpot": tpot,
                "e2e": e2e,
                "success": True
            })
    except Exception as e:
        REQUESTS.labels(status='error').inc()
        print(f"Request failed: {e}")
        results_log.append({"success": False, "error": str(e)})

async def closed_loop(session, url, prompts, concurrency, duration, auth_headers, model):
    end_time = time.monotonic() + duration
    
    async def worker():
        while time.monotonic() < end_time:
            prompt = random.choice(prompts)
            await make_request(session, url, prompt, auth_headers, model)
            
    workers = [worker() for _ in range(concurrency)]
    await asyncio.gather(*workers)

async def open_loop(session, url, prompts, target_rps, duration, auth_headers, model):
    end_time = time.monotonic() + duration
    interval = 1.0 / target_rps
    
    tasks = []
    while time.monotonic() < end_time:
        prompt = random.choice(prompts)
        tasks.append(asyncio.create_task(make_request(session, url, prompt, auth_headers, model)))
        await asyncio.sleep(interval)
        
    await asyncio.gather(*tasks)

async def deterministic_loop(session, url, prompts, auth_headers, model):
    # Executes each prompt exactly once sequentially
    for prompt in prompts:
        await make_request(session, url, prompt, auth_headers, model)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
        
    start_http_server(8000)
    print("Prometheus metrics available on port 8000")
    
    url = config.get('endpoint', "http://localhost:8080/v1/chat/completions")
    mode = config.get('mode', 'closed-loop')
    duration = config.get('duration_seconds', 10)
    prompts = config.get('prompts', ["test"])
    auth_token = config.get('auth_token', '')
    
    model = config.get('model', 'facebook/opt-125m')
    
    auth_headers = {}
    if auth_token:
        auth_headers['Authorization'] = f"Bearer {auth_token}"
    
    print(f"Starting {mode} benchmark for {duration} seconds with model {model}...")
    global run_start_time
    run_start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        if mode == 'closed-loop':
            await closed_loop(session, url, prompts, config.get('concurrency', 1), duration, auth_headers, model)
        elif mode == 'deterministic':
            await deterministic_loop(session, url, prompts, auth_headers, model)
        else:
            await open_loop(session, url, prompts, config.get('target_rps', 1), duration, auth_headers, model)
            
    print("Benchmark complete. Metrics server remains active for 10 seconds to scrape.")
    
    run_end_time = time.time()
    
    # Save results
    timestamp = int(run_end_time)
    output_file = f'results_{timestamp}.json'
    provenance = {
        "metadata": {
            "config": config,
            "start_time": run_start_time,
            "end_time": run_end_time,
            "model": model,
            "duration": duration
        },
        "results": results_log
    }
    with open(output_file, 'w') as f:
        json.dump(provenance, f, indent=2)
    print(f"Saved run metadata to {output_file}")
    
    await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
