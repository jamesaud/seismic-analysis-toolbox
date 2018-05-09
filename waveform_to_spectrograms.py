import docker
import time
from itertools import islice

client = docker.from_env()


def api():
    with client.parallelize(docker_containers_generator, max_containers) as batch_job:
        batch_job.start()

    
    queue = [] 
    container.create(image, '--starttime xx --endttime xx --duration xx')


class ParallelClient:

    def __init__(self, queue, max_containers, ping_time=2):
        self._running_containers = []
        self.queue = iter(queue)
        self.max_containers = max_containers
        self.ping_time = ping_time

    def start(self):
        self.intialize()
        self.parallelize()

    @property
    def running_containers(self):
        self.check_containers()
        return self.running_containers

    def run_container(self, container):
        cid = container.run(detach=True)
        self.running_containers.append(cid)

    def run_available(self):
        available = len(self.running_containers) - self.max_containers
        for container in islice(self.queue, available):
            self.run_container(container)

    def intialize(self):
        for container in islice(self.queue, self.max_containers):
            self.run_container(container)
    
    def parallelize(self, ping_time=2): 
        while self.queue:
            self.run_available()
            time.sleep(ping_time)

    def check_containers(self):
        for container in self.running_containers:
            if container.is_stopped():
                self.delete_container(container)

    def delete_container(self, container):
        container.delete()
        self.running_containers.remove(container)


    def __open__(self):
        pass

    def __close__(self):
        for container in self.running_containers:
            self.delete_container(container)