from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing
from random import randint


class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()

    @task(4)
    def open_dataset(self):
        dataset_id = randint(1, 100)
        self.client.get(f"/doi/{dataset_id}")
        print(f"Opened dataset {dataset_id}")

    @task(3)
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)

    @task(2)
    def dataset_rate(self):
        for i in range(4):
            dataset_id = i + 1
            self.client.post(f"/dataset/{dataset_id}/rate", data={"rate": (i * 2) % 5})
        print("Rated dataset")

    @task(1)
    def download_all_datasets(self):
        self.client.get("/dataset/download/all")


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
