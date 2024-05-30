## Setup

### Run NIM for LLMs
Follow [this guide](https://docs.nvidia.com/nim/large-language-models/latest/getting-started.html#prerequisites).

### Python dependencies
```bash
pip install locust
```

## Run single test

```bash
MAX_CONCURRENT_USERS=1 # Change this to run different treatments.
SPAWN_RATE=1           # Users per second. Keep fixed for this experiment.
TIME='20s'
MODEL='meta-llama3-8b-instruct'
locust -f locustfile.py --headless -u $MAX_CONCURRENT_USERS -r $SPAWN_RATE -t $TIME --csv data/${MODEL}_${MAX_CONCURRENT_USERS}_users
```

## Run full 8b test

```bash
bash run_experiment_8b.sh
```