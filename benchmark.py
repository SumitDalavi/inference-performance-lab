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

async def make_request(session, url, prompt, auth_headers):
    start_time = time.monotonic()
    payload = {
        "model": "facebook/opt-125m",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": 100
    }
    
    try:
        async with session.post(url, json=payload, headers=auth_headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
            if response.status != 200:
                print(f"Error {response.status}: {await response.text()}")
                REQUESTS.labels(status='error').inc()
                return

            first_chunk_time = None
            last_chunk_time = None
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
                            token_count += 1
                            now = time.monotonic()
                            if first_chunk_time is None:
                                first_chunk_time = now
                                TTFT.observe(first_chunk_time - start_time)
                            else:
                                ITL.observe(now - last_chunk_time)
                            last_chunk_time = now
                    except json.JSONDecodeError:
                        pass
            
            end_time = time.monotonic()
            e2e = end_time - start_time
            E2E_LATENCY.observe(e2e)
            if token_count > 0:
                tpot = (end_time - first_chunk_time) / token_count if first_chunk_time else 0
                TPOT.observe(tpot)
                
            REQUESTS.labels(status='success').inc()
            results_log.append({
                "prompt_length": len(prompt),
                "tokens": token_count,
                "ttft": (first_chunk_time - start_time) if first_chunk_time else 0,
                "e2e": e2e,
                "success": True
            })
    except Exception as e:
        REQUESTS.labels(status='error').inc()
        print(f"Request failed: {e}")
        results_log.append({"success": False, "error": str(e)})

async def closed_loop(session, url, prompts, concurrency, duration, auth_headers):
    end_time = time.monotonic() + duration
    
    async def worker():
        while time.monotonic() < end_time:
            prompt = random.choice(prompts)
            await make_request(session, url, prompt, auth_headers)
            
    workers = [worker() for _ in range(concurrency)]
    await asyncio.gather(*workers)

async def open_loop(session, url, prompts, target_rps, duration, auth_headers):
    end_time = time.monotonic() + duration
    interval = 1.0 / target_rps
    
    tasks = []
    while time.monotonic() < end_time:
        prompt = random.choice(prompts)
        tasks.append(asyncio.create_task(make_request(session, url, prompt, auth_headers)))
        await asyncio.sleep(interval)
        
    await asyncio.gather(*tasks)

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
    
    auth_headers = {}
    if auth_token:
        auth_headers['Authorization'] = f"Bearer {auth_token}"
    
    print(f"Starting {mode} benchmark for {duration} seconds...")
    
    async with aiohttp.ClientSession() as session:
        if mode == 'closed-loop':
            await closed_loop(session, url, prompts, config.get('concurrency', 1), duration, auth_headers)
        else:
            await open_loop(session, url, prompts, config.get('target_rps', 1), duration, auth_headers)
            
    print("Benchmark complete. Metrics server remains active for 10 seconds to scrape.")
    
    # Save results
    with open('results.json', 'w') as f:
        json.dump(results_log, f, indent=2)
    print("Saved run metadata to results.json")
    
    await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
