# Link Scheduling - Part A

## Overview

A multithreaded client-server system implementing three scheduling policies (FCFS, SJF, RR) for file transfer operations. The system supports concurrent clients, measures performance metrics, and enables comparison of scheduling policies.

## Features

- **Multithreaded server** with configurable worker threads
- **Three scheduling policies**: First Come First Serve (FCFS), Shortest Job First (SJF), Round Robin (RR)
- **File operations**: PUT (upload) and GET (download)
- **Performance metrics**: Response time, waiting time, throughput
- **Configurable packetization**: Control network transfer granularity
- **Concurrent client testing**: Simulate multiple clients for load testing

## Project Structure

```
server.cpp          # Server implementation
client.cpp          # Client implementation
config.cpp/h        # Configuration file parser
protocol.cpp/h      # Communication protocol
scheduler.cpp/h     # Scheduling policies
utils.cpp/h         # Utility functions
Makefile            # Build system
config.json         # Configuration file
README.md           # This file
testdata/           # Test files directory
scripts/    		# Graph Plotting script
plots/    			# Generated Plots
scripts/       		# Python scripts for plot generation and analysis
results/			# Generated test outputs in csv format (58 csv's being generated- details later in 					this document)
client_outputs		# client outputs (files downloaded from server)
run_experiments		# Runs all experiments in sequence- puts client data in client_outputs and puts all 					generated reports in results folder



## Building

### Prerequisites
- g++ with C++17 support
- POSIX threads (pthread)
- Linux/Unix environment

### Instructions to run the Project

bash
make



To clean build artifacts:


bash
make clean
make

chmod +x run_experiments.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true

./run_experiments.sh  

#running the above takes about 14 minutes- due to multiple inputs for all experiments

(Optional- to generate and analyze plots)

python3 scripts/plot_comparison.py
python3 scripts/quick_analysis.py > analysis_output.txt



# Manual Demo (if not running run_experiments.sh)

##Running the Server

### Command-Line Arguments

bash
./server --sched <policy> --p <N> --file <path> [--quantum <Q>]


### Required Arguments

- --sched <policy>: Scheduling policy
  - fcfs - First Come First Serve
  - sjf - Shortest Job First
  - rr - Round Robin
- --p <N>: Packetization parameter (lines per packet)
- --file <path>: Input file or directory to preload

### Optional Arguments

- --quantum <Q>: Time quantum for Round Robin (required if --sched rr)


## Running the Client

### Interactive Mode

bash
./client --interactive

Commands in interactive mode:
put <local_file> - Upload file to server
get <remote_file> - Download file from server
quit - Exit


## Experiments (in detail alongwith manual run options)

### Experiment 1: Vary Client Threads

Fixed server threads, varying client load:

bash
# Server (keep running)
./server --sched fcfs --p 10 --file testdata/

# Run for different client thread counts
for n in 2 4 8 16 32; do
    # Update config.json with client_threads = n
    ./client --test testdata/ --requests 10
    cp metrics.csv metrics_fcfs_clients_${n}.csv
done


### Experiment 2: Vary Server Threads

Fixed client threads, varying server capacity:

bash
for n in 1 2 4 8 16; do
    # Update config.json with server_threads = n
    ./server --sched fcfs --p 10 --file testdata/
    ./client --test testdata/ --requests 20
    cp metrics.csv metrics_fcfs_servers_${n}.csv
done


### Experiment 3: Vary Packetization

Test different packet sizes:

bash
for p in 1 5 10 50 100; do
    ./server --sched fcfs --p $p --file testdata/
    ./client --test testdata/ --requests 20
    cp metrics.csv metrics_fcfs_packet_${p}.csv
done


### Experiment 4: Compare Schedulers

Run all three policies with same workload:

bash
for sched in fcfs sjf rr; do
    if [ "$sched" = "rr" ]; then
        ./server --sched $sched --quantum 5 --p 10 --file testdata/
    else
        ./server --sched $sched --p 10 --file testdata/
    fi
    ./client --test testdata/ --requests 20
    cp metrics.csv metrics_${sched}.csv
done


## Analysis

Use the provided Python script to analyze metrics:


python3 scripts/plot_comparision
python3 scripts/quick_analysis


This generates:
- Summary statistics (mean, median, std dev)
- Response time distribution plots
- Throughput calculations
- Waiting time analysis



## Authors

Girish Singh Thakur
Nitish Kumar
## License

MIT License