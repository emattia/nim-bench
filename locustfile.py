from locust import HttpUser, TaskSet, task, between

class OpenAITaskSet(TaskSet):

    @task
    def query_openai(self):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = {
            "model": "meta-llama3-8b-instruct",
            "prompt": "Once upon a time",
            "max_tokens": 200
        }
        self.client.post("/v1/completions", json=data, headers=headers)

class OpenAIUser(HttpUser):
    tasks = [OpenAITaskSet]
    wait_time = between(1, 5)
    host = "http://0.0.0.0:8000"