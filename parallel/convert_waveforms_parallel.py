from parallelize import Parallelize
import docker
from docker.types import Mount
import os
from pprint import pprint

cwd = os.getcwd()
DEBUG = True                             # Show the first container's logs to make sure everything is going okay
IMAGE = 'parallel_waveform_converter'
WRITE_PATH = '/data/spectrograms/'                              # Write spectrograms/waveforms (in the container)  
READ_PATH = '/data/mseed/'                                      # Path to MSEED (in the container)
READ_FILE = os.path.join(READ_PATH, 'GSOK029_8-2014.mseed')     # MSEED File

abs_path = lambda path: os.path.join(cwd, path)

num_containers = 8              # Number of concurrent containers
duration = 20                   # Duration of the waveform / spectrogram
separation = -5                 # Set to a postivie number to have space in between windows, negative to overlap
start = 0                       # Seconds to start from beginning of waveform  (0 would be the start)
period = 10000                  # Seconds for each container to process 
                                # Shorter time means less figures are written, taking up less memory per container
write_spectrograms = True       # Set to False to only write waveforms

volumes = {abs_path('GSOK029_8_spectrograms/'): {'bind': WRITE_PATH},
           abs_path('mseed/'): {'bind': READ_PATH}}


def generate_containers(client, start, duration, period, stop=float('inf'), separation=0):
    while start <= stop:
        end = start + period
        yield client.containers.create(IMAGE, volumes=volumes,
                                       command=f'''
                                       --start {start} 
                                       --duration {duration} 
                                       --end {end} 
                                       --write_path {WRITE_PATH} 
                                       --read_file {READ_FILE}
                                       --separation {separation}
                                       --write_spectrograms {write_spectrograms}
                                       ''')
        start = end


client = docker.from_env()
queue = generate_containers(client, start, duration=duration, period=period, separation=separation)
container = next(queue)
container.start()

if DEBUG:
    print("Starting a single container to debug the logs. This might take a moment...")
    for logs in container.logs(stream=True):
        pprint(logs)

# Run `docker ps` in terminal to see the started containers
print("Starting containers in parallel...")
with Parallelize(queue, num_containers) as batch_job:
    batch_job.start()
