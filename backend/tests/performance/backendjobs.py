from locust import HttpLocust, TaskSet, task, between

class UserBehavior(TaskSet):

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        # login(self)

    def on_stop(self):
        pass

    def login(self):
        """ login user """
        pass

    @task
    def getjobs(self):
        self.client.get("/api/jobs/")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)
