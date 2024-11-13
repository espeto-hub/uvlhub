from locust import HttpUser, task, between


class FakenodoUser(HttpUser):
    wait_time = between(1, 9)
    host = "http://web_app_container:5000"

    @task
    def test_connection(self):
        self.client.get("/fakenodo/api")

    @task
    def create_deposition(self):
        self.client.post("/fakenodo/api")

    @task
    def create_deposition_files(self):
        deposition_id = 123
        self.client.post(f"/fakenodo/api/{deposition_id}/files")

    @task
    def delete_deposition(self):
        deposition_id = 123
        self.client.delete(f"/fakenodo/api/{deposition_id}")

    @task
    def publish_deposition(self):
        deposition_id = 123
        self.client.post(f"/fakenodo/api/{deposition_id}/actions/publish")

    @task
    def get_deposition(self):
        deposition_id = 123
        self.client.get(f"/fakenodo/api/{deposition_id}")
