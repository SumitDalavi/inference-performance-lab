import asyncio
import time
import argparse
import yaml
import aiohttp
from prometheus_client import start_http_server, Histogram, Counter

# Metrics
TTFT = Histogram('llm_ttft_seconds', 'Time To First Token', buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0])
ITL = Histogram('llm_itl_seconds', 'Inter-Token Latency (per chunk)', buckets=[0.01, 0.02, 0.05, 0.1, 0.2])
E2E_LATENCY = Histogram('llm_e2e_seconds', 'End to End Request Latency', buckets=[0.5, 1.0, 2.0, 5.0, 10.0])
REQUESTS = Counter('llm_requests_total', 'Total Requests', ['status'])

async def make_request(session, url, prompt):
    start_time = time.monotonic()
    try:
        async with session.post(url, json={"prompt": prompt, "stream": True}) as response:
            first_chunk_time = None
            last_chunk_time = None
            
            async for line in response.content:
                if not line.strip() or line.startswith(b'data: [DONE]'):
                    continue
                
                now = time.monotonic()
                if first_chunk_time is None:
                    first_chunk_time = now
                    TTFT.observe(first_chunk_time - start_time)
                else:
                    ITL.observe(now - last_chunk_time)
                last_chunk_time = now
            
            E2E_LATENCY.observe(time.monotonic() - start_time)
            REQUESTS.labels(status='success').inc()
    except Exception as e:
        REQUESTS.labels(status='error').inc()
        print(f"Request failed: {e}")

async def closed_loop(session, url, prompts, concurrency, duration):
    end_time = time.monotonic() + duration
    
    async def worker():
        while time.monotonic() < end_time:
            # Pick a prompt round-robin or random
            prompt = prompts[0] 
            await make_request(session, url, prompt)
            
    workers = [worker() for _ in range(concurrency)]
    await asyncio.gather(*workers)

async def open_loop(session, url, prompts, target_rps, duration):
    end_time = time.monotonic() + duration
    interval = 1.0 / target_rps
    
    tasks = []
    while time.monotonic() < end_time:
        prompt = prompts[0]
        tasks.append(asyncio.create_task(make_request(session, url, prompt)))
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
    
    url = "http://localhost:8080/v1/chat/completions"
    mode = config.get('mode', 'closed-loop')
    duration = config.get('duration_seconds', 10)
    prompts = config.get('prompts', ["test"])
    
    print(f"Starting {mode} benchmark for {duration} seconds...")
    
    async with aiohttp.ClientSession() as session:
        if mode == 'closed-loop':
            await closed_loop(session, url, prompts, config.get('concurrency', 1), duration)
        else:
            await open_loop(session, url, prompts, config.get('target_rps', 1), duration)
            
    print("Benchmark complete. Metrics server remains active for 10 seconds to scrape.")
    await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
