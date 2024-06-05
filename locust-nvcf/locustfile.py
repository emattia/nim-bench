from locust import HttpUser, TaskSet, task, between, events

import os
import random
import time
import pandas as pd
from dotenv import load_dotenv
load_dotenv('../.env')

status_url = 'https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions'
result_url = 'https://api.nvcf.nvidia.com/v2/nvcf/pexec/status'
function_id = 'd4b187f8-3812-4eff-8f1f-5e1afabde9ea'

token = os.environ['NGC_RUN_TOKEN']
prompts = [
    "How would you explain the concept of existentialism to someone with no background in philosophy? Please provide examples from daily life.",
    "What are the potential benefits and drawbacks of implementing artificial intelligence in healthcare? Consider both the short-term and long-term impacts.",
    "Explain the significance of Gödel's incompleteness theorems in the context of mathematical logic and its implications for the field of computer science.",
    "Discuss the key strategies a startup should employ to achieve product-market fit. How can these strategies be adjusted for different industries?",
    "What are the ethical considerations of using genetic modification in agriculture? Should there be global regulations governing its use?",
    "Compare and contrast the causes and effects of the Industrial Revolution in Europe and the United States. How did these changes shape modern society?",
    "Describe the process of photosynthesis and its importance in the global carbon cycle. How might climate change affect this process?",
    "What techniques can be used to improve active listening skills in professional settings? Provide examples of how these techniques can be applied.",
    "Analyze the themes of identity and alienation in Franz Kafka's 'The Metamorphosis.' How do these themes reflect Kafka's own life experiences?",
    "Explain the concept of supply and demand. How do shifts in supply and demand curves affect market equilibrium and pricing?"
]

out_data = {
    'prompt': [],
    'response': [],
    'status_code': []
}

class GenerationTaskSet(TaskSet):
    
    @task
    def query_openai(self):
        _prompt = random.choice(prompts)
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {token}"
        }
        data = {
            "model": "meta-llama3-70b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": _prompt
                }
            ],
            "max_tokens": 300
        }
        response = self.client.post(f'/{function_id}', json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            _response_str = response_data['choices'][0]['message']['content']
            out_data['prompt'].append(_prompt)
            out_data['response'].append(_response_str)
            out_data['status_code'].append(response.status_code)
        elif response.status_code == 202:
            out_data['prompt'].append(_prompt)
            out_data['response'].append('Pending')
            out_data['status_code'].append(202)

            # TODO: polling ~ below is not working well with locust as is
            # while True:
            #     _resp = self.client.get(f"{result_url}/{function_id}" , headers=headers)
            #     if _resp.status_code == 200:
            #         _data = _resp.json()
            #         _response_str = _data['choices'][0]['message']['content']
            #         out_data['prompt'].append(_prompt)
            #         out_data['response'].append(_response_str)
            #         out_data['status_code'].append(_resp.status_code)
            #     elif _resp.status_code == 202:
            #         time.sleep(2)
            #     elif _resp.status_code in [400, 500]:
            #         out_data['prompt'].append(_prompt)
            #         out_data['response'].append("Error")
            #         out_data['status_code'].append(_resp.status_code)
            #         break

        else:
            out_data['prompt'].append(_prompt)
            out_data['response'].append("Error")
            out_data['status_code'].append(response.status_code)

class APIUser(HttpUser):
    tasks = [GenerationTaskSet]
    wait_time = between(5,20)
    host = status_url


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    df = pd.DataFrame(out_data)
    df.to_csv('data/requests.csv', index=False)
