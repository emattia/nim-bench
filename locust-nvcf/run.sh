TIME='1m'
MODEL='meta-llama3-70b-instruct'
SPAWN_RATE=1                  # Users per second.
MAX_CONCURRENT_USERS=20         

run_load_test() {
  locust -f locustfile.py --headless -u $MAX_CONCURRENT_USERS -r $SPAWN_RATE -t $TIME --csv data/
}

mkdir -p data
run_load_test