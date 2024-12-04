from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing


class BotBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task
    def index(self):
        response = self.client.get("/bot")

        if response.status_code != 200:
            print(f"Bot index failed: {response.status_code}")


class BotUser(HttpUser):
    tasks = [BotBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
