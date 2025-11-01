#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

RESULTS_DIR="results"
TEST_DIR="testdata"
SERVER_BIN="./server"
CLIENT_BIN="./client"
REQUESTS_PER_THREAD=20

print_msg() {
    echo -e "${GREEN}[EXPERIMENT]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

update_config() {
  cat > config.json <<EOF
{
    "server_ip": "127.0.0.1",
  "server_port": 9000,
    "server_threads": $1,
    "client_threads": $2
}
EOF
}

run_experiment() {
  local name=$1 sched=$2 quantum=$3 packet=$4 srv=$5 cli=$6
    
    print_msg "Running: $name"
    
  pkill -9 server 2>/dev/null || true
    rm -f metrics.csv
    sleep 2
    
  update_config $srv $cli
    
    local cmd="$SERVER_BIN --sched $sched --p $packet --file $TEST_DIR"
  [ "$sched" = "rr" ] && cmd="$cmd --quantum $quantum"
    
    $cmd > /dev/null 2>&1 &
  local pid=$!
    sleep 3
    
    $CLIENT_BIN --test $TEST_DIR --requests $REQUESTS_PER_THREAD > /dev/null 2>&1
    
  kill -INT $pid 2>/dev/null || true
    
    for i in {1..10}; do
  [ -f "metrics.csv" ] && break
        sleep 1
    done
    
  if [ -f "metrics.csv" ]; then
        mv metrics.csv "$RESULTS_DIR/${name}.csv"
        print_msg "✓ Saved: $name.csv"
  else
        print_error "✗ Failed: $name"
    fi
    
  kill -9 $pid 2>/dev/null || true
    sleep 1
}

mkdir -p $RESULTS_DIR
pkill -9 server 2>/dev/null || true

print_msg "=== Experiment 1: Baseline ===" 
run_experiment "exp1_fcfs" "fcfs" 0 10 4 8
run_experiment "exp1_sjf" "sjf" 0 10 4 8
run_experiment "exp1_rr_q5" "rr" 5 10 4 8
run_experiment "exp1_rr_q10" "rr" 10 10 4 8

print_msg "=== Experiment 2: Varying Clients ==="
for c in 2 4 8 16 32; do
  run_experiment "exp2_fcfs_c${c}" "fcfs" 0 10 4 $c
    run_experiment "exp2_sjf_c${c}" "sjf" 0 10 4 $c
    run_experiment "exp2_rr_c${c}" "rr" 5 10 4 $c
done

print_msg "=== Experiment 3: Varying Servers ==="
for s in 1 2 4 8 16; do
  run_experiment "exp3_fcfs_s${s}" "fcfs" 0 10 $s 8
    run_experiment "exp3_sjf_s${s}" "sjf" 0 10 $s 8
    run_experiment "exp3_rr_s${s}" "rr" 5 10 $s 8
done

print_msg "=== Experiment 4: Varying Packetization ==="
for p in 1 5 10 25 50 100; do
  run_experiment "exp4_fcfs_p${p}" "fcfs" 0 $p 4 8
    run_experiment "exp4_sjf_p${p}" "sjf" 0 $p 4 8
    run_experiment "exp4_rr_p${p}" "rr" 5 $p 4 8
done

print_msg "=== Experiment 5: Varying RR Quantum ==="
for q in 1 3 5 10 20 50; do
  run_experiment "exp5_rr_q${q}" "rr" $q 10 4 8
done

print_msg "Complete! Generated $(ls -1 $RESULTS_DIR/*.csv | wc -l) CSV files"
ls -lh $RESULTS_DIR/