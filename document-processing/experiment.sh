#!/bin/bash

GPU_UTIL_INTERVAL=1
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | tr '[:upper:]' '[:lower:]' | tr -s ' ' '_')

run() {

    python main.py -m $max_workers -n 1 -t 100

    # SMALL SUMMARY
    for max_workers in 1 5 10 20
    do
        python main.py -m $max_workers -n 100 -t 100
    done

    # MEDIUM SUMMARY
    for max_workers in 1 5 10 20
    do
        python main.py -m $max_workers -n 100 -t 500
    done

    # BIG SUMMARY
    for max_workers in 1 5 10 20
    do
        python main.py -m $max_workers -n 100 -t 1000
    done

}

check_gpu_utilization() {
  echo "Timestamp,GPU Utilization (%),GPU Memory Utilization (%)" > latest-data/$GPU_NAME_gpu_util.csv
  while true; do
    TIMESTAMP=$(date +%s)
    GPU_UTILIZATION=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
    MEMORY_UTILIZATION=$(nvidia-smi --query-gpu=utilization.memory --format=csv,noheader,nounits)
    echo "$TIMESTAMP,$GPU_UTILIZATION,$MEMORY_UTILIZATION" >> latest-data/$GPU_NAME_gpu_util.csv
    sleep $GPU_UTIL_INTERVAL
  done
}

check_gpu_utilization &
GPU_UTIL_PID=$!
run
kill $GPU_UTIL_PID