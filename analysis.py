import json
import pandas as pd
import matplotlib.pyplot as plt
import argparse

def analyze(results_file):
    with open(results_file, 'r') as f:
        data = json.load(f)
        
    results_list = data.get("results", data) if isinstance(data, dict) else data
    df = pd.DataFrame(results_list)
    
    if df.empty or 'success' not in df.columns:
        print("No valid data to analyze.")
        return
        
    success_df = df[df['success'] == True]
    failed_df = df[df['success'] == False]
    
    print(f"Total Requests: {len(df)}")
    print(f"Successful: {len(success_df)}")
    print(f"Failed: {len(failed_df)}")
    
    if success_df.empty:
        return
        
    print("\n--- Percentiles ---")
    metrics = ['ttft', 'e2e']
    if 'tpot' in success_df.columns:
        metrics.append('tpot')
        
    for metric in metrics:
        if metric in success_df.columns:
            print(f"{metric.upper()} (seconds):")
            print(f"  P50: {success_df[metric].quantile(0.50):.4f}")
            print(f"  P90: {success_df[metric].quantile(0.90):.4f}")
            print(f"  P95: {success_df[metric].quantile(0.95):.4f}")
            print(f"  P99: {success_df[metric].quantile(0.99):.4f}")
            
    # Throughput
    total_tokens = success_df['tokens'].sum()
    total_time_span = 1
    if isinstance(data, dict) and "metadata" in data:
        total_time_span = data["metadata"]["end_time"] - data["metadata"]["start_time"]
    else:
        total_time_span = success_df['e2e'].max()
        
    if total_time_span > 0:
        print(f"\nApproximate Throughput: {total_tokens / total_time_span:.2f} tokens/sec")

    # Generate charts
    plt.figure(figsize=(10, 5))
    plt.hist(success_df['ttft'], bins=20, alpha=0.7, color='blue')
    plt.title('TTFT Distribution')
    plt.xlabel('Seconds')
    plt.ylabel('Count')
    plt.savefig('ttft_distribution.png')
    print("Saved ttft_distribution.png")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=str, default='results.json')
    args = parser.parse_args()
    analyze(args.results)
