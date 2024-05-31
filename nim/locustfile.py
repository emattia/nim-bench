from locust import HttpUser, TaskSet, task, between


class GenerationTaskSet(TaskSet):
    
    @task
    def query_openai(self):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = {
            "model": "meta-llama3-70b-instruct",
            "prompt": "Once upon a time",
            "max_tokens": 100
        }
        self.client.post("/v1/completions", json=data, headers=headers)
        

class APIUser(HttpUser):
    tasks = [GenerationTaskSet]
    wait_time = between(1, 20) # users wait between 5 and 20 seconds to make each call
    host = "http://0.0.0.0:8000"
