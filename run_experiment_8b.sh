TIME='2m'
MODEL='meta-llama3-8b-instruct'
SPAWN_RATE=100                # Users per second.
MAX_CONCURRENT_USERS=1000
INTERVAL=1                    # Interval in seconds to check GPU utilization

run_load_test() {
  locust -f locustfile.py --headless -u $MAX_CONCURRENT_USERS -r $SPAWN_RATE -t $TIME --csv data/${MODEL}_users &
}

check_gpu_utilization() {
  echo "Timestamp,GPU Utilization (%)" > data/gpu_util.csv
  while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    GPU_UTILIZATION=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
    echo "$TIMESTAMP,$GPU_UTILIZATION" >> data/${MODEL}_gpu_util.csv
    sleep $INTERVAL
  done
}

mkdir -p data
run_load_test
check_gpu_utilization &
wait