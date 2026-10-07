import time
import argparse
from prometheus_client import start_http_server, Summary, Counter

REQUEST_TIME = Summary('inference_processing_seconds', 'Time spent processing inference request')
CHUNKS_PROCESSED = Counter('inference_chunks_total', 'Total chunks processed')

@REQUEST_TIME.time()
def process_chunk():
    time.sleep(0.045)
    CHUNKS_PROCESSED.inc()

def main():
    parser = argparse.ArgumentParser(description='Inference Load Generator')
    parser.add_argument('--model', type=str, default='mock', help='Model to benchmark')
    parser.add_argument('--mode', type=str, default='open-loop', choices=['open-loop', 'closed-loop'])
    args = parser.parse_args()

    # INF-03: Expose Prometheus metrics
    start_http_server(8000)
    print("Prometheus metrics available on port 8000")
    print(f"Starting inference benchmark for model {args.model} in {args.mode} mode...")
    
    for i in range(50):
        process_chunk()
        if i % 10 == 0:
            print(f"Processed chunk {i}, ITL: ~45ms")
    
    print("Benchmark complete. Metrics server remains active for 10 seconds to scrape.")
    time.sleep(10)

if __name__ == '__main__':
    main()
