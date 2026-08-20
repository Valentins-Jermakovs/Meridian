import random

from locust import (
    HttpUser,
    between,
    task,
)


class AuthServiceUser(HttpUser):

    wait_time = between(1, 3)

    def on_start(self):
        self.username = "testuser01"
        self.password = "12345678"

        self.access_token = None
        self.refresh_token = None

        self.login()

    def login(self):

        response = self.client.post(
            "/auth/login",
            json={
                "login": self.username,
                "password": self.password,
            },
            name="/auth/login",
        )

        if response.status_code == 200:

            data = response.json()

            self.access_token = (
                data["access_token"]
            )

            self.refresh_token = (
                data["refresh_token"]
            )

    @task(5)
    def get_me(self):

        if self.access_token is None:
            return

        self.client.get(
            "/users/me",
            headers={
                "Authorization": (
                    f"Bearer {self.access_token}"
                )
            },
            name="/users/me",
        )

    @task(2)
    def refresh(self):

        if self.refresh_token is None:
            return

        response = self.client.post(
            "/auth/refresh",
            json={
                "refresh_token": self.refresh_token,
            },
            name="/auth/refresh",
        )

        if response.status_code == 200:

            data = response.json()

            self.access_token = (
                data["access_token"]
            )

            self.refresh_token = (
                data["refresh_token"]
            )


class AdminUser(HttpUser):

    wait_time = between(1, 3)

    def on_start(self):

        self.access_token = None

        response = self.client.post(
            "/auth/login",
            json={
                "login": "admin01",
                "password": "12345678",
            },
            name="/auth/login",
        )

        if response.status_code == 200:

            self.access_token = (
                response.json()["access_token"]
            )

    @task(5)
    def search_users(self):

        if self.access_token is None:
            return

        self.client.get(
            "/users/",
            params={
                "query": "user",
                "page": 1,
                "page_size": 20,
            },
            headers={
                "Authorization": (
                    f"Bearer {self.access_token}"
                )
            },
            name="/users/search",
        )

    @task(3)
    def search_audit(self):

        if self.access_token is None:
            return

        self.client.get(
            "/audit/",
            params={
                "query": "login",
                "page": 1,
                "page_size": 20,
            },
            headers={
                "Authorization": (
                    f"Bearer {self.access_token}"
                )
            },
            name="/audit/search",
        )