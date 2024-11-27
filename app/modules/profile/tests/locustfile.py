from locust import HttpUser, task, between


class CheckDatasetUser(HttpUser):
    wait_time = between(1, 3)  # Wait between requests.

    @task
    def check_dataset_user(self):
        try:
            # 1. Visit the homepage
            response = self.client.get("/")
            if response.status_code == 200:
                print("Home page loaded successfully")
            else:
                print(f"Failed to load home page: {response.status_code}")

            # 2. Navigate to "Sample dataset 4"
            response = self.client.get("/doi/10.1234/dataset4/")  # Update this path if needed.
            if response.status_code == 200:
                print("Sample dataset 4 page loaded successfully")
            else:
                print(f"Failed to load Sample dataset 4: {response.status_code}")

            # 3. Navigate to "Doe, Jane"
            response = self.client.get("/profile/2/")  # Update this path if needed.
            if response.status_code == 200:
                print("Jane Doe's page loaded successfully")
            else:
                print(f"Failed to load Jane Doe's page: {response.status_code}")

            # 4. Navigate to "Sample dataset 2"
            response = self.client.get("/doi/10.1234/dataset2/")  # Update this path if needed.
            if response.status_code == 200:
                print("Sample dataset 2 page loaded successfully")
            else:
                print(f"Failed to load Sample dataset 2: {response.status_code}")
        except Exception as e:
            print(f"An error occurred during the test: {e}")
