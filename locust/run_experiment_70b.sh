TIME='10m'
MODEL='meta-llama3-70b-instruct'
SPAWN_RATE=20                  # Users per second.
MAX_CONCURRENT_USERS=10000
INTERVAL=1                    

source nim/bin/activate

run_load_test() {
  locust -f locustfile.py --headless -u $MAX_CONCURRENT_USERS -r $SPAWN_RATE -t $TIME --csv data/${MODEL}_users &
}

check_gpu_utilization() {
  echo "Timestamp,GPU Utilization (%),GPU Memory Utilization (%)" > data/${MODEL}_gpu_util.csv
  while true; do
    TIMESTAMP=$(date +%s)
    GPU_UTILIZATION=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
    MEMORY_UTILIZATION=$(nvidia-smi --query-gpu=utilization.memory --format=csv,noheader,nounits)
    echo "$TIMESTAMP,$GPU_UTILIZATION,$MEMORY_UTILIZATION" >> data/${MODEL}_gpu_util.csv
    sleep $INTERVAL
  done
}

mkdir -p data
run_load_test
check_gpu_utilization &
wait
