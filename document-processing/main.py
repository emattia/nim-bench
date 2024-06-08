from openai import OpenAI
import concurrent.futures
import threading
import time
import os
import argparse
import random
import subprocess
from transformers import AutoTokenizer
import pandas as pd
from constants import MODEL, DOCUMENTS_DIR, OUTDATA_DIR, MAX_TOKENS_PER_PROMPT, RESULTS_FILE_COMMON

PROMPT_TOKENS = 0
COMPLETION_TOKENS = 0
TOTAL_REQUESTS = 0

def fetch_docs(docs_dir=DOCUMENTS_DIR):
    # Sign in with huggingface_hub login in CLI.
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
    documents = []
    for summary_file in os.listdir(docs_dir):
        with open(f"{docs_dir}/{summary_file}", "r") as f:
            # This is a dumb rule. 
            # We should use the full document by chunking docs with too many tokens.
            wiki_content_txt = f.read() 
            n_tokens = len(tokenizer.encode(wiki_content_txt))
            if (n_tokens + 1000) < MAX_TOKENS_PER_PROMPT:
                documents.append(wiki_content_txt)
    return documents

def get_device(): 
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True
    )
    gpu_names = result.stdout.strip().split('\n')
    if len(gpu_names) > 1:
        device = gpu_names[0]
        # TODO: the CLI doesn't do this, actually. modify this script for now.
        print('Found multiple device types. Set to %, manually change it if you ran the experiment on a different device.' % device)
    elif len(gpu_names) == 1:
        device = gpu_names[0]
    else:
        raise ValueError('No GPU found.')
    return device.lower().replace(' ', '_')

lock = threading.Lock() 
def thread_function(thread_id, documents, n=100, max_tokens=500):
    global PROMPT_TOKENS, COMPLETION_TOKENS, TOTAL_REQUESTS
    client = OpenAI(base_url="http://0.0.0.0:8000/v1", api_key="not-used")
    for i in range(n):
        print(f"Thread {thread_id}: Step {i}")
        random_doc = random.choice(documents)
        prompt = "Here is a document to summarize: " + \
                 random_doc + \
                 "\n\nSummary:"
        response = client.completions.create(
            model=MODEL,
            prompt=prompt,
            max_tokens=max_tokens
        )
        completion = response.choices[0].text
        with lock:
            PROMPT_TOKENS += response.usage.prompt_tokens
            COMPLETION_TOKENS += response.usage.completion_tokens
            TOTAL_REQUESTS += 1

def main(documents, max_workers=16, n=100, max_tokens=500):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(thread_function, thread_id, documents, n, max_tokens) 
            for thread_id in range(max_workers)    
        ]
        concurrent.futures.wait(futures)
        for future in futures:
            future.result()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max-workers", type=int, default=2)
    parser.add_argument("-n", "--num-requests", type=int, default=2)
    parser.add_argument("-t", "--max-tokens", type=int, default=500)
    parser.add_argument("-d", "--docs-dir", type=str, default=DOCUMENTS_DIR)
    args = parser.parse_args()
    
    documents = fetch_docs(docs_dir=args.docs_dir)

    t0 = time.time()
    main(documents, args.max_workers, args.num_requests, args.max_tokens)
    tf = time.time()
    t_elapsed = tf - t0

    device = get_device()
    save_path = "%s/%s_%s" % (OUTDATA_DIR, device, RESULTS_FILE_COMMON)

    if os.path.exists(save_path):
        old_df = pd.read_csv(save_path)
    else:
        old_df = pd.DataFrame()
    new_df = pd.DataFrame({
        "prompt_tokens": [PROMPT_TOKENS],
        "completion_tokens": [COMPLETION_TOKENS],
        "total_requests": [TOTAL_REQUESTS],
        "total_time": [t_elapsed],
        "concurrent_requests": [args.max_workers],
        "n_requests_per_thread": [args.num_requests],
        "max_tokens_per_request": [args.max_tokens],
        "start_ts": [t0],
        "end_ts": [tf],
        "device": [device]
    })
    df = pd.concat([old_df, new_df], ignore_index=True)
    df.to_csv(save_path, index=False)