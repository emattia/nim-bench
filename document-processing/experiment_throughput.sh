#!/bin/bash

GPU_UTIL_INTERVAL=1
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | tr '[:upper:]' '[:lower:]' | tr -s ' ' '_')
OUTDATA_DIR="latest-data"

if [ ! -d "$OUTDATA_DIR" ]; then
    mkdir -p "$OUTDATA_DIR"
fi

run() {
    for max_workers in 25 50 75
    do
        for num_max_tokens in 250 500 750 1000
        do 
            python3 trial.py -m $max_workers -n 100 -t $num_max_tokens
        done
    done
}

check_gpu_utilization() {
  echo "Timestamp,GPU Utilization (%),GPU Memory Utilization (%)" > $(echo $OUTDATA_DIR)/$(echo $GPU_NAME)_gpu_util.csv
  while true; do
    TIMESTAMP=$(date +%s)
    GPU_UTILIZATION=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
    MEMORY_UTILIZATION=$(nvidia-smi --query-gpu=utilization.memory --format=csv,noheader,nounits)
    echo "$TIMESTAMP,$GPU_UTILIZATION,$MEMORY_UTILIZATION" >> $(echo $OUTDATA_DIR)/$(echo $GPU_NAME)_gpu_util.csv
    sleep $GPU_UTIL_INTERVAL
  done
}

check_gpu_utilization &
GPU_UTIL_PID=$!
run
kill $GPU_UTIL_PID