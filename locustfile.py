import random

from locust import HttpUser, between, task

# Number of seeded users (intern1 ... internN). Match the --users value you used.
USER_COUNT = 1000
PASSWORD = "Intern@12345"


class Intern(HttpUser):
    wait_time = between(1, 3)

    def csrf(self):
        return self.client.cookies.get("csrftoken", "")

    def on_start(self):
        self.client.get("/login/")
        number = random.randint(1, USER_COUNT)
        self.client.post(
            "/login/",
            {
                "username": "intern" + str(number),
                "password": PASSWORD,
                "csrfmiddlewaretoken": self.csrf(),
            },
            headers={"Referer": self.host + "/login/"},
        )

    @task(5)
    def view_projects(self):
        self.client.get("/projects/")

    @task(3)
    def view_profile(self):
        self.client.get("/profile/")

    @task(1)
    def submit_project(self):
        self.client.get("/projects/new/")
        self.client.post(
            "/projects/new/",
            {
                "title": "Load test project " + str(random.randint(1, 100000)),
                "description": "Created by the Locust load test.",
                "github_link": "https://github.com/loadtest/demo",
                "csrfmiddlewaretoken": self.csrf(),
            },
            headers={"Referer": self.host + "/projects/new/"},
            name="/projects/new/ [POST]",
        )
