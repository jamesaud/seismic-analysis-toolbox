from parallelize import Parallelize
import docker
from docker.types import Mount
import os

cwd = os.getcwd()

IMAGE = 'parallel_waveform_converter'
WRITE_PATH = '/data/spectrograms'
READ_PATH = '/data/mseed/GSOK029_7-2014.mseed'
abs_path = lambda path: os.path.join(cwd, path)
num_containers = 5

volumes = {abs_path('spectrograms/'): {'bind' : '/data/spectrograms/'},
           abs_path('mseed/'):        {'bind' : '/data/mseed/'}}


def generate_containers(client, start=0, duration=20, period=2000, stop=float('inf'), separation=0):
    while start <= stop:
        end = start + period
        yield client.containers.create(IMAGE, volumes=volumes, 
                                       command=f'''
                                       --start {start} 
                                       --duration {duration} 
                                       --end {end} 
                                       --write_path {WRITE_PATH} 
                                       --read_path {READ_PATH}
                                       --separation {separation}
                                       ''')
        start = end

client = docker.from_env()
queue = generate_containers(client, duration=20, period=1800, separation=-15)
container = next(queue)
container.start()

with Parallelize(queue, num_containers) as batch_job:
    batch_job.start()
    
    