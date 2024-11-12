from locust import HttpUser, task
from core.environment.host import get_host_for_locust_testing


class FakenodoUser(HttpUser):
    min_wait = 1000
    max_wait = 3000
    host = get_host_for_locust_testing()

    @task
    def upload_dataset(self):
        response = self.client.post(
            "/fakenodo/upload",
            files={"file": ("example.csv", open("example.csv", "rb"))}
        )
        assert response.status_code == 201, f"Upload failed: {response.status_code}"

    @task
    def download_dataset(self):
        response = self.client.get("/fakenodo/download/1")
        assert response.status_code == 200, f"Download failed: {response.status_code}"

    @task
    def list_datasets(self):
        response = self.client.get("/fakenodo/datasets")
        assert response.status_code == 200, f"List datasets failed: {response.status_code}"

    @task
    def delete_dataset(self):
        response = self.client.delete("/fakenodo/dataset/1")
        assert response.status_code == 200, f"Delete failed: {response.status_code}"
