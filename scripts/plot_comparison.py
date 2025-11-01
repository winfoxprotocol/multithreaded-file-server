#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import glob

def load_experiment_data(pattern):
    files = sorted(glob.glob(pattern))
    data={}
    for f in files:
        name = os.path.basename(f).replace('.csv', '')
        df=pd.read_csv(f)
        data[name] = df
    return data

def plot_varying_clients(output_dir='plots'):
    pattern = 'results/exp2_*_c*.csv'
    data=load_experiment_data(pattern)

    if not data:
        print("No data found for varying clients experiment")
        return

    schedulers = {'fcfs': {}, 'sjf': {}, 'rr': {}}

    for name, df in data.items():
        parts = name.split('_')
        sched=parts[1]
        client_count = int(parts[2].replace('c', ''))

        if sched in schedulers:
            schedulers[sched][client_count]=df

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for sched_name, sched_data in schedulers.items():
        if not sched_data:
            continue
        client_counts = sorted(sched_data.keys())
        mean_response=[]
        mean_waiting = []
        throughput = []
        for count in client_counts:
            df = sched_data[count]
            mean_response.append(df['response_time_ms'].mean())
            mean_waiting.append(df['waiting_time_ms'].mean())
            time_span=(df['finish_time_ns'].max() - df['arrival_time_ns'].min()) / 1e9
            throughput.append(len(df) / time_span if time_span > 0 else 0)

        axes[0, 0].plot(client_counts, mean_response, marker = 'o', label=sched_name.upper())
        axes[0, 1].plot(client_counts, mean_waiting, marker='s', label=sched_name.upper())
        axes[1, 0].plot(client_counts, throughput, marker='^', label=sched_name.upper())
        if sched_name == 'fcfs':
            for count in client_counts:
                df = sched_data[count]
                percentiles = np.percentile(df['response_time_ms'], [50, 90, 95, 99])
                axes[1, 1].plot([count]*4, percentiles, 'o-', alpha=0.6,
                              label=f'{count} clients' if count==client_counts[0] else '')

    axes[0, 0].set_xlabel('Number of Client Threads')
    axes[0, 0].set_ylabel('Mean Response Time (ms)')
    axes[0, 0].set_title('Response Time vs Client Load')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha = 0.3)
    axes[0, 1].set_xlabel('Number of Client Threads')
    axes[0, 1].set_ylabel('Mean Waiting Time (ms)')
    axes[0, 1].set_title('Waiting Time vs Client Load')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    axes[1, 0].set_xlabel('Number of Client Threads')
    axes[1, 0].set_ylabel('Throughput (req/s)')
    axes[1, 0].set_title('Throughput vs Client Load')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 1].set_xlabel('Number of Client Threads')
    axes[1, 1].set_ylabel('Response Time (ms)')
    axes[1, 1].set_title('Response Time Percentiles (FCFS)')
    axes[1, 1].grid(True, alpha = 0.3)
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'varying_clients_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def plot_varying_servers(output_dir='plots'):
    pattern = 'results/exp3_*_s*.csv'
    data = load_experiment_data(pattern)
    if not data:
        print("No data found for varying servers experiment")
        return
    schedulers={'fcfs': {}, 'sjf': {}, 'rr': {}}
    for name, df in data.items():
        parts=name.split('_')
        sched = parts[1]
        server_count=int(parts[2].replace('s', ''))
        if sched in schedulers:
            schedulers[sched][server_count] = df
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for sched_name, sched_data in schedulers.items():
        if not sched_data: continue
        server_counts = sorted(sched_data.keys())
        mean_response = []
        speedup = []
        throughput = []
        parallel_efficiency=[]
        baseline_time = None
        for count in server_counts:
            df = sched_data[count]
            response = df['response_time_ms'].mean()
            mean_response.append(response)
            time_span=(df['finish_time_ns'].max() - df['arrival_time_ns'].min()) / 1e9
            tput = len(df) / time_span if time_span > 0 else 0
            throughput.append(tput)
            if baseline_time is None:
                baseline_time=response
                speedup.append(1.0)
                parallel_efficiency.append(1.0)
            else:
                sp=baseline_time / response if response > 0 else 0
                speedup.append(sp)
                parallel_efficiency.append(sp/count if count > 0 else 0)
        axes[0, 0].plot(server_counts, mean_response, marker='o', label=sched_name.upper())
        axes[0, 1].plot(server_counts, throughput, marker='s', label=sched_name.upper())
        axes[1, 0].plot(server_counts, speedup, marker='^', label=sched_name.upper())
        axes[1, 1].plot(server_counts, parallel_efficiency, marker='d', label=sched_name.upper())
    if schedulers.get('fcfs'):
        server_counts=sorted(schedulers['fcfs'].keys())
        axes[1, 0].plot(server_counts, server_counts, 'k--', alpha=0.3, label='Ideal')
    axes[0, 0].set_xlabel('Number of Server Threads')
    axes[0, 0].set_ylabel('Mean Response Time (ms)')
    axes[0, 0].set_title('Response Time vs Server Threads')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 1].set_xlabel('Number of Server Threads')
    axes[0, 1].set_ylabel('Throughput (req/s)')
    axes[0, 1].set_title('Throughput vs Server Threads')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    axes[1, 0].set_xlabel('Number of Server Threads')
    axes[1, 0].set_ylabel('Speedup')
    axes[1, 0].set_title('Parallel Speedup')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 1].set_xlabel('Number of Server Threads')
    axes[1, 1].set_ylabel('Parallel Efficiency')
    axes[1, 1].set_title('Parallel Efficiency')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    plt.tight_layout()
    output_file=os.path.join(output_dir, 'varying_servers_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def plot_varying_packetization(output_dir='plots'):
    pattern='results/exp4_*_p*.csv'
    data = load_experiment_data(pattern)
    if not data:
        print("No data found for varying packetization experiment")
        return
    schedulers = {'fcfs': {}, 'sjf': {}, 'rr': {}}
    for name, df in data.items():
        parts=name.split('_')
        sched = parts[1]
        packet_size = int(parts[2].replace('p', ''))
        if sched in schedulers:
            schedulers[sched][packet_size] = df
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for sched_name, sched_data in schedulers.items():
        if not sched_data:
            continue
        packet_sizes=sorted(sched_data.keys())
        mean_response = []
        throughput = []
        mean_service=[]
        for size in packet_sizes:
            df=sched_data[size]
            mean_response.append(df['response_time_ms'].mean())
            time_span=(df['finish_time_ns'].max() - df['arrival_time_ns'].min()) / 1e9
            throughput.append(len(df) / time_span if time_span>0 else 0)
            service_time=(df['finish_time_ns'] - df['start_time_ns']) / 1e6
            mean_service.append(service_time.mean())
        axes[0].plot(packet_sizes, mean_response, marker='o', label=sched_name.upper())
        axes[1].plot(packet_sizes, throughput, marker='s', label=sched_name.upper())
        axes[2].plot(packet_sizes, mean_service, marker='^', label=sched_name.upper())
    axes[0].set_xlabel('Packet Size (lines)')
    axes[0].set_ylabel('Mean Response Time (ms)')
    axes[0].set_title('Response Time vs Packet Size')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xscale('log')
    axes[1].set_xlabel('Packet Size (lines)')
    axes[1].set_ylabel('Throughput (req/s)')
    axes[1].set_title('Throughput vs Packet Size')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xscale('log')
    axes[2].set_xlabel('Packet Size (lines)')
    axes[2].set_ylabel('Mean Service Time (ms)')
    axes[2].set_title('Service Time vs Packet Size')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xscale('log')
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'varying_packetization_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def plot_rr_quantum_analysis(output_dir='plots'):
    pattern='results/exp5_rr_q*.csv'
    data=load_experiment_data(pattern)
    if not data:
        print("No data found for RR quantum experiment")
        return
    quantum_data={}
    for name, df in data.items():
        quantum = int(name.split('_q')[1])
        quantum_data[quantum] = df
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    quantums = sorted(quantum_data.keys())
    mean_response = []
    mean_waiting=[]
    fairness_index = []
    throughput=[]
    for q in quantums:
        df=quantum_data[q]
        mean_response.append(df['response_time_ms'].mean())
        mean_waiting.append(df['waiting_time_ms'].mean())
        time_span=(df['finish_time_ns'].max() - df['arrival_time_ns'].min()) / 1e9
        throughput.append(len(df) / time_span if time_span>0 else 0)
        response_times=df['response_time_ms'].values
        fairness=(np.sum(response_times) ** 2) / (len(response_times) * np.sum(response_times ** 2))
        fairness_index.append(fairness)
    axes[0, 0].plot(quantums, mean_response, marker='o', color='blue')
    axes[0, 0].set_xlabel('Quantum Size')
    axes[0, 0].set_ylabel('Mean Response Time (ms)')
    axes[0, 0].set_title('Response Time vs Quantum')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 1].plot(quantums, mean_waiting, marker='s', color='orange')
    axes[0, 1].set_xlabel('Quantum Size')
    axes[0, 1].set_ylabel('Mean Waiting Time (ms)')
    axes[0, 1].set_title('Waiting Time vs Quantum')
    axes[0, 1].grid(True, alpha=0.3)
    axes[1, 0].plot(quantums, throughput, marker='^', color='green')
    axes[1, 0].set_xlabel('Quantum Size')
    axes[1, 0].set_ylabel('Throughput (req/s)')
    axes[1, 0].set_title('Throughput vs Quantum')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 1].plot(quantums, fairness_index, marker='d', color='red')
    axes[1, 1].set_xlabel('Quantum Size')
    axes[1, 1].set_ylabel('Fairness Index')
    axes[1, 1].set_title('Fairness vs Quantum')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].axhline(y=1.0, color='k', linestyle='--', alpha=0.3, label='Perfect Fairness')
    axes[1, 1].legend()
    plt.tight_layout()
    output_file=os.path.join(output_dir, 'rr_quantum_analysis.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def generate_summary_table(output_dir='plots'):
    baseline_files = {
        'FCFS': 'results/exp1_fcfs.csv',
        'SJF': 'results/exp1_sjf.csv',
        'RR (Q=5)': 'results/exp1_rr_q5.csv',
        'RR (Q=10)': 'results/exp1_rr_q10.csv',
    }
    summary_data = []
    for name, file in baseline_files.items():
        if not os.path.exists(file):
            continue
        df=pd.read_csv(file)
        time_span=(df['finish_time_ns'].max()-df['arrival_time_ns'].min())/1e9
        throughput=len(df)/time_span if time_span>0 else 0
        summary_data.append({
            'Policy': name,
            'Requests': len(df),
            'Mean Response (ms)': f"{df['response_time_ms'].mean():.3f}",
            'Median Response (ms)': f"{df['response_time_ms'].median():.3f}",
            'Std Dev (ms)': f"{df['response_time_ms'].std():.3f}",
            'Mean Waiting (ms)': f"{df['waiting_time_ms'].mean():.3f}",
            'Throughput (req/s)': f"{throughput:.2f}",
        })
    if summary_data:
        summary_df=pd.DataFrame(summary_data)
        output_file=os.path.join(output_dir, 'summary_table.csv')
        summary_df.to_csv(output_file, index=False)
        print(f"\nSummary Table:\n{summary_df.to_string(index=False)}")
        print(f"\nSaved: {output_file}")

def main():
    os.makedirs('plots', exist_ok=True)
    print("Generating comparison plots...")
    print("="*60)
    plot_varying_clients()
    plot_varying_servers()
    plot_varying_packetization()
    plot_rr_quantum_analysis()
    generate_summary_table()
    print("="*60)
    print("\nAll plots generated in plots/ directory")

if __name__ == '__main__':
    main()