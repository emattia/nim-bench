from openai import OpenAI
import concurrent.futures
import threading
import time
import os
import argparse
import random
from transformers import AutoTokenizer
import pandas as pd


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
MODEL = "meta-llama3-8b-instruct"
PROMPT_TOKENS = 0
COMPLETION_TOKENS = 0
TOTAL_REQUESTS = 0
MAX_TOKENS_PER_PROMPT = 8192

documents = []
for summary_file in os.listdir("data"):
    with open(f"data/{summary_file}", "r") as f:
        # This is a dumb rule. 
        # We should use the full document by chunking docs with too many tokens.
        wiki_content_txt = f.read() 
        n_tokens = len(tokenizer.encode(wiki_content_txt))
        if (n_tokens + 1000) < MAX_TOKENS_PER_PROMPT:
            documents.append(wiki_content_txt)

lock = threading.Lock()

def thread_function(thread_id, n=100, max_tokens=500):
    global PROMPT_TOKENS, COMPLETION_TOKENS, TOTAL_REQUESTS
    client = OpenAI(base_url="http://0.0.0.0:8000/v1", api_key="not-used")
    for i in range(n):
        print(f"Thread {thread_id}: Step {i}")
        random_doc = random.choice(documents)
        prompt = "Here is a document to summarize: " + \
                 random_doc + \
                 "\n\nSummarize the document above.\n\nSummary:"
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

def main(max_workers=16, n=100, max_tokens=500):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(thread_function, thread_id, n, max_tokens) 
            for thread_id in range(max_workers)    
        ]
        concurrent.futures.wait(futures)
        for future in futures:
            future.result() 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max_workers", type=int, default=2)
    parser.add_argument("-n", "--n", type=int, default=2)
    parser.add_argument("-t", "--max_tokens", type=int, default=500)
    args = parser.parse_args()
    
    t0 = time.time()
    main(args.max_workers, args.n, args.max_tokens)
    t_elapsed = time.time() - t0

    if os.path.exists("results.csv"):
        old_df = pd.read_csv("results.csv")
    else:
        old_df = pd.DataFrame()
    new_df = pd.DataFrame({
        "prompt_tokens": [PROMPT_TOKENS],
        "completion_tokens": [COMPLETION_TOKENS],
        "total_requests": [TOTAL_REQUESTS],
        "total_time": [t_elapsed],
        "concurrent_requests": [args.max_workers],
        "n_requests_per_thread": [args.n],
        "max_tokens_per_request": [args.max_tokens]
    })
    df = pd.concat([old_df, new_df], ignore_index=True)
    df.to_csv("results.csv", index=False)