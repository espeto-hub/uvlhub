import functools

from faker import Faker
from locust import HttpUser, TaskSet, task
from locust.exception import InterruptTaskSet

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token

faker = Faker()


def logged_in(func):
    @functools.wraps(func)
    def _impl(self, *method_args, **method_kwargs):
        self.client.get("/logout")
        response = self.client.get("/login")
        if response.status_code != 200 or "Login" not in response.text:
            print("Already logged in or unexpected response, redirecting to logout")
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/login", data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf_token}
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")

        func(self, csrf_token, *method_args, **method_kwargs)

        self.client.get("/logout")

    return _impl


class BotBehavior(TaskSet):
    @task
    def list_get_not_logged_in(self):
        response = self.client.get("/bots/list")

        if response.status_code != 200:
            raise InterruptTaskSet(f"Unexpected response: {response.status_code}")
        if "Login" not in response.text:
            raise InterruptTaskSet("Expected login page, but got something else")

    @task
    @logged_in
    def list_get_logged_in(self, token):
        with self.client.get("/bots/list", headers={"X-CSRF-TOKEN": token}, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")
            if "My bots" not in response.text:
                response.failure("Expected bots page, but got something else")

    @task
    def create_get_not_logged_in(self):
        with self.client.get("/bots/create", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")
            if "Login" not in response.text:
                response.failure("Expected login page, but got something else")

    @task
    @logged_in
    def create_get_logged_in(self, token):
        with self.client.get("/bots/create", headers={"X-CSRF-TOKEN": token}, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")
            if "Create bot" not in response.text:
                response.failure("Expected create bot page, but got something else")

    @task
    @logged_in
    def create_post_test(self, token):
        data = {
            "name": faker.pystr(min_chars=3, max_chars=50),
            "service_name": "Discord",
            "service_url": "discord://webhook_id/webhook_token",
            "enabled": "true",
            "on_download_dataset": "true",
            "on_download_file": "true",
            'is_tested': 'false',
            'submit': 'true',
        }
        with self.client.post(
                "/bots/create", data=data, headers={"X-CSRF-TOKEN": token}, catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")

    @task
    @logged_in
    def create_post_submit(self, token):
        data = {
            "name": faker.pystr(min_chars=3, max_chars=50),
            "service_name": "Discord",
            "service_url": "discord://webhook_id/webhook_token",
            "enabled": "true",
            "on_download_dataset": "true",
            "on_download_file": "true",
            'is_tested': 'true',
            'submit': 'true',
        }
        with self.client.post(
                "/bots/create", data=data, headers={"X-CSRF-TOKEN": token}, catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")
            if "✔" not in response.text:
                response.failure("Expected success message, but got something else")

    @task
    def edit_get_not_logged_in(self):
        with self.client.get("/bots/edit/1", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")
            if "Login" not in response.text:
                response.failure("Expected login page, but got something else")

    @task
    @logged_in
    def edit_get_logged_in(self, token):
        with self.client.get("/bots/edit/1", headers={"X-CSRF-TOKEN": token}, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")
            if "Edit bot" not in response.text:
                response.failure("Expected edit bot page, but got something else")

    @task
    @logged_in
    def edit_post_test(self, token):
        data = {
            "enabled": "false",
            'is_tested': 'false',
            'submit': 'true',
        }
        with self.client.post(
                "/bots/edit/1", data=data, headers={"X-CSRF-TOKEN": token}, catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")

    @task
    @logged_in
    def edit_post_submit(self, token):
        data = {
            "enabled": "false",
            'is_tested': 'true',
            'submit': 'true',
        }
        with self.client.post(
                "/bots/edit/1", data=data, headers={"X-CSRF-TOKEN": token}, catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")
            if "✔" not in response.text:
                response.failure("Expected success message, but got something else")

    @task
    def delete_post_not_logged_in(self):
        with self.client.post("/bots/delete/1", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")
            if "Login" not in response.text:
                response.failure("Expected login page, but got something else")

    @task
    @logged_in
    def delete_post_logged_in(self, token):
        with self.client.post("/bots/delete/1", headers={"X-CSRF-TOKEN": token}, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected response: {response.status_code}")


class BotUser(HttpUser):
    tasks = [BotBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
