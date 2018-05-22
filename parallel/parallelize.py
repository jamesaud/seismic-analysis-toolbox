import docker
import time
from itertools import islice
        

class Parallelize:
    def __init__(self, queue, max_containers, ping_time=2):
        self._running_containers = []
        self.containers = []
        self.queue = iter(queue)
        self.max_containers = max_containers
        self.ping_time = ping_time

    def start(self):
        self.intialize()
        self.parallelize()

    @property
    def running_containers(self):
        self.check_containers()
        return self._running_containers

    def run_container(self, container):
        print("Starting container: ", container)
        container.start()
        self.running_containers.append(container)

    def run_available(self):
        available = self.max_containers - len(self.running_containers) 
        for container in islice(self.queue, available):
            self.run_container(container)

    def intialize(self):
        for container in islice(self.queue, self.max_containers):
            self.run_container(container)
    
    def parallelize(self, ping_time=2): 
        while self.queue:
            self.run_available()
            time.sleep(ping_time)

    def has_finished(self, container):
        return container.status == 'exited'

    def check_containers(self):
        for container in self._running_containers:
            container.reload()
            if self.has_finished(container):
                self.delete_container(container)
 
    def delete_container(self, container):
        self._running_containers.remove(container)
        container.remove(force=True)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for container in self.running_containers:
            self.delete_container(container)
