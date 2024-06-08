## Setup

### Hardware

TODO: What GPUs? Link to support matrix.

### Code packages
```
pip3 install pandas transformers openai wikipedia "huggingface_hub[cli]"
```

### Authenticate HuggingFace
Go here and create and account and token, if you don't have them.
```
huggingface-cli login
```

### [Optional] Get prometheus

NIM containers expose Grafana-consumable metrics on port `8000`. You can scrape them with a Prometheus server.

#### Install Prometheus
```bash
VERSION="2.52.0"
OS="linux-amd64"
wget https://github.com/prometheus/prometheus/releases/download/v$VERSION/prometheus-$VERSION.$OS.tar.gz
tar -xvzf prometheus-$VERSION.$OS.tar.gz
```

### [Optional] Get Grafana

Grafana can be used to visualize the metrics Prometheus scrapes

#### Install Grafana
```bash
wget https://dl.grafana.com/oss/release/grafana-11.0.0.linux-amd64.tar.gz
tar -zxvf grafana-11.0.0.linux-amd64.tar.gz
```

#### Change the target
Tell Prometheus to listen to `8000` by going to the `prometheus.yml` file and setting:
```yml
scrape_configs:
    ...
    static_configs:
      - targets: ["localhost:8000"]
```

## Run the NIM container
Follow instructions to start the NIM model [here](https://docs.nvidia.com/nim/large-language-models/latest/getting-started.html). You need an Nvidia Enterprise AI subscription, or access through Outerbounds.

```bash
# Choose a container name for bookkeeping
export CONTAINER_NAME=llama3-8b-instruct

# Choose a LLM NIM Image from NGC
export IMG_NAME="nvcr.io/nim/meta/${CONTAINER_NAME}:1.0.0"

# Choose a path on your system to cache the downloaded models
export LOCAL_NIM_CACHE=~/.cache/nim
mkdir -p "$LOCAL_NIM_CACHE"

# Start the LLM NIM
docker run -it --rm --name=$CONTAINER_NAME \
  --runtime=nvidia \
  --gpus all \
  --shm-size=16GB \
  -e NGC_API_KEY=$NGC_API_KEY \
  -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
  -u $(id -u) \
  -p 8000:8000 \
  $IMG_NAME
```

## [Optional] Run Prometheus and Grafana

With the NIM container running, open a new terminal, and start prometheus to watch the container port with metrics.
```bash
cd prometheus-$VERSION.$OS/
./prometheus --config.file=./prometheus.yml
```

Open a third terminal, and start Grafana:
```bash
cd grafana-v11.0.0/
./bin/grafana-server
```

Access the data on port `3000`. Use `username: admin` and `password: admin`.

You can test it with 

## Run a single trial
Run with 2 concurrent threads, each sending 1 request that the NIM model should respond to with in 100 or less tokens.
```
python3 main.py -m 2 -n 1 -t 100
```

Run with 5 concurrent threads, each sending 100 request that the NIM model should respond to with in 500 or less tokens.
```
python3 main.py -m 5 -n 100 -t 500
```

## Run an experiment
The Python script is built so that you can run it many times and easily compose the results in a pandas dfs.

### Modify `experiment.sh`
Check it out tweak it. The idea is to run the same file across multiple GPU types, and runs, to observe consistency of results and learn which workloads fit well on each GPU card type.

### Launch it, keep GPU on until it completes
```
bash experiment.sh
```

### Monitoring while it happens