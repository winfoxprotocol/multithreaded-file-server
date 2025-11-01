#!/usr/bin/env python3
"""
Quick analysis to extract key insights for the report
"""

import pandas as pd
import numpy as np
import os
import re

RESULTS_DIR = 'results'

def extract_number_from_filename(filename, pattern):
    """Safely extract number from filename using regex"""
    match = re.search(pattern, filename)
    if match:
        return int(match.group(1))
    return None

def analyze_baseline():
    """Analyze baseline experiment"""
    print("=" * 60)
    print("BASELINE COMPARISON (Experiment 1)")
    print("=" * 60)
    
    schedulers = {
        'FCFS': 'exp1_fcfs.csv',
        'SJF': 'exp1_sjf.csv',
        'RR (Q=5)': 'exp1_rr_q5.csv',
        'RR (Q=10)': 'exp1_rr_q10.csv'
    }
    
    results = {}
    for name, file in schedulers.items():
        path = os.path.join(RESULTS_DIR, file)
        if os.path.exists(path):
            df = pd.read_csv(path)
            
            time_span = (df['finish_time_ns'].max() - df['arrival_time_ns'].min()) / 1e9
            throughput = len(df) / time_span if time_span > 0 else 0
            
            response_times = df['response_time_ms'].values
            fairness = (np.sum(response_times) ** 2) / (len(response_times) * np.sum(response_times ** 2))
            
            results[name] = {
                'mean_response': df['response_time_ms'].mean(),
                'median_response': df['response_time_ms'].median(),
                'std_response': df['response_time_ms'].std(),
                'mean_waiting': df['waiting_time_ms'].mean(),
                'throughput': throughput,
                'fairness': fairness,
                'p95_response': np.percentile(df['response_time_ms'], 95),
                'p99_response': np.percentile(df['response_time_ms'], 99)
            }
    
    if not results:
        print("No baseline data found!")
        return None
    
    best_mean = min(results.items(), key=lambda x: x[1]['mean_response'])
    best_median = min(results.items(), key=lambda x: x[1]['median_response'])
    most_consistent = min(results.items(), key=lambda x: x[1]['std_response'])
    best_throughput = max(results.items(), key=lambda x: x[1]['throughput'])
    fairest = max(results.items(), key=lambda x: x[1]['fairness'])
    
    print(f"\n✓ Best Mean Response Time: {best_mean[0]} = {best_mean[1]['mean_response']:.2f} ms")
    print(f"✓ Best Median Response Time: {best_median[0]} = {best_median[1]['median_response']:.2f} ms")
    print(f"✓ Most Consistent (lowest std dev): {most_consistent[0]} = {most_consistent[1]['std_response']:.2f} ms")
    print(f"✓ Best Throughput: {best_throughput[0]} = {best_throughput[1]['throughput']:.2f} req/s")
    print(f"✓ Fairest: {fairest[0]} = {fairest[1]['fairness']:.4f}")
    
    print("\nDetailed Comparison:")
    print(f"{'Scheduler':<12} {'Mean (ms)':<12} {'Median (ms)':<12} {'Std (ms)':<12} {'P95 (ms)':<12} {'Throughput':<12} {'Fairness':<10}")
    print("-" * 90)
    for name, metrics in results.items():
        print(f"{name:<12} {metrics['mean_response']:>10.2f}  {metrics['median_response']:>10.2f}  "
              f"{metrics['std_response']:>10.2f}  {metrics['p95_response']:>10.2f}  "
              f"{metrics['throughput']:>10.2f}  {metrics['fairness']:>8.4f}")
    
    return results

def analyze_client_scaling():
    """Analyze how schedulers handle increasing clients"""
    print("\n" + "=" * 60)
    print("CLIENT SCALING ANALYSIS (Experiment 2)")
    print("=" * 60)
    
    import glob
    
    for scheduler in ['fcfs', 'sjf', 'rr']:
        files = sorted(glob.glob(os.path.join(RESULTS_DIR, f'exp2_{scheduler}_c*.csv')))
        if not files:
            continue
        
        print(f"\n{scheduler.upper()}:")
        print(f"{'Clients':<10} {'Mean Resp (ms)':<15} {'Throughput':<15} {'Mean Wait (ms)':<15}")
        print("-" * 55)
        
        data_points = []
        for f in files:
            client_count = extract_number_from_filename(os.path.basename(f), r'_c(\d+)\.csv')
            if client_count is None:
                continue
            
            df = pd.read_csv(f)
            
            time_span = (df['finish_time_ns'].max() - df['arrival_time_ns'].min()) / 1e9
            throughput = len(df) / time_span if time_span > 0 else 0
            
            data_points.append((client_count, df['response_time_ms'].mean(), throughput, df['waiting_time_ms'].mean()))
        
        data_points.sort(key=lambda x: x[0])
        
        for client_count, mean_resp, throughput, mean_wait in data_points:
            print(f"{client_count:<10} {mean_resp:>13.2f}  {throughput:>13.2f}  {mean_wait:>13.2f}")

def analyze_server_scaling():
    """Analyze parallel scaling"""
    print("\n" + "=" * 60)
    print("SERVER SCALING ANALYSIS (Experiment 3)")
    print("=" * 60)
    
    import glob
    
    for scheduler in ['fcfs', 'sjf', 'rr']:
        files = sorted(glob.glob(os.path.join(RESULTS_DIR, f'exp3_{scheduler}_s*.csv')))
        if not files:
            continue
        
        print(f"\n{scheduler.upper()}:")
        print(f"{'Servers':<10} {'Mean Resp (ms)':<15} {'Speedup':<15} {'Efficiency':<15} {'Throughput':<15}")
        print("-" * 70)
        
        data_points = []
        for f in files:
            server_count = extract_number_from_filename(os.path.basename(f), r'_s(\d+)\.csv')
            if server_count is None:
                continue
            
            df = pd.read_csv(f)
            
            mean_resp = df['response_time_ms'].mean()
            time_span = (df['finish_time_ns'].max() - df['arrival_time_ns'].min()) / 1e9
            throughput = len(df) / time_span if time_span > 0 else 0
            
            data_points.append((server_count, mean_resp, throughput))
        
        data_points.sort(key=lambda x: x[0])
        
        baseline = None
        for server_count, mean_resp, throughput in data_points:
            if baseline is None:
                baseline = mean_resp
                speedup = 1.0
                efficiency = 1.0
            else:
                speedup = baseline / mean_resp if mean_resp > 0 else 0
                efficiency = speedup / server_count if server_count > 0 else 0
            
            print(f"{server_count:<10} {mean_resp:>13.2f}  {speedup:>13.2f}  "
                  f"{efficiency:>13.2f}  {throughput:>13.2f}")

def analyze_packetization():
    """Analyze packet size impact"""
    print("\n" + "=" * 60)
    print("PACKETIZATION ANALYSIS (Experiment 4)")
    print("=" * 60)
    
    import glob
    
    for scheduler in ['fcfs', 'sjf', 'rr']:
        files = sorted(glob.glob(os.path.join(RESULTS_DIR, f'exp4_{scheduler}_p*.csv')))
        if not files:
            continue
        
        print(f"\n{scheduler.upper()}:")
        print(f"{'Packet Size':<12} {'Mean Resp (ms)':<15} {'Throughput':<15}")
        print("-" * 42)
        
        data_points = []
        for f in files:
            packet_size = extract_number_from_filename(os.path.basename(f), r'_p(\d+)\.csv')
            if packet_size is None:
                continue
            
            df = pd.read_csv(f)
            
            time_span = (df['finish_time_ns'].max() - df['arrival_time_ns'].min()) / 1e9
            throughput = len(df) / time_span if time_span > 0 else 0
            
            data_points.append((packet_size, df['response_time_ms'].mean(), throughput))
        
        data_points.sort(key=lambda x: x[0])
        
        for packet_size, mean_resp, throughput in data_points:
            print(f"{packet_size:<12} {mean_resp:>13.2f}  {throughput:>13.2f}")

def analyze_rr_quantum():
    """Analyze RR quantum tuning"""
    print("\n" + "=" * 60)
    print("ROUND ROBIN QUANTUM ANALYSIS (Experiment 5 / Experiment 1)")
    print("=" * 60)
    
    import glob
    
    files = sorted(glob.glob(os.path.join(RESULTS_DIR, 'exp5_rr_q*.csv')))
    if not files:
        files = sorted(glob.glob(os.path.join(RESULTS_DIR, 'exp1_rr_q*.csv')))
    
    if not files:
        print("No RR quantum data found")
        return
    
    print(f"\n{'Quantum':<10} {'Mean Resp (ms)':<15} {'Throughput':<15} {'Fairness':<15}")
    print("-" * 55)
    
    data_points = []
    for f in files:
        quantum = extract_number_from_filename(os.path.basename(f), r'_q(\d+)\.csv')
        if quantum is None:
            continue
        
        df = pd.read_csv(f)
        
        time_span = (df['finish_time_ns'].max() - df['arrival_time_ns'].min()) / 1e9
        throughput = len(df) / time_span if time_span > 0 else 0
        
        response_times = df['response_time_ms'].values
        fairness = (np.sum(response_times) ** 2) / (len(response_times) * np.sum(response_times ** 2))
        
        data_points.append((quantum, df['response_time_ms'].mean(), throughput, fairness))
    
    data_points.sort(key=lambda x: x[0])
    
    for quantum, mean_resp, throughput, fairness in data_points:
        print(f"{quantum:<10} {mean_resp:>13.2f}  {throughput:>13.2f}  {fairness:>13.4f}")

def main():
    print("\n" + "═" * 60)
    print("SCHEDULING EXPERIMENT QUICK ANALYSIS")
    print("═" * 60)
    
    analyze_baseline()
    analyze_client_scaling()
    analyze_server_scaling()
    analyze_packetization()
    analyze_rr_quantum()
    
    print("\n" + "═" * 60)
    print("Analysis complete! Use these insights to fill in the report.")
    print("═" * 60 + "\n")

if __name__ == '__main__':
    main()
