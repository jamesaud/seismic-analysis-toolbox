from termcolor import colored
import matplotlib
matplotlib.use('agg')
from code.helpers import *
from code.async_client import AsyncClient
from obspy import UTCDateTime
from subprocess import PIPE, run, Popen
import re
import time
import random
from collections import namedtuple

CLIENT_NAME = 'IRIS'
client = AsyncClient(CLIENT_NAME)
img_name = 'seismictoolbox_waveform'

print("Retrieving Stations from Server...")
inventory = client.get_stations(channel='HN*', startafter=UTCDateTime(year=1980, month=1, day=1))
print("Got Stations")

count = 0

cmd = f"docker run -v {os.getcwd()}/waveforms:/data/waveforms -e PYTHONUNBUFFERED=0 \
{img_name} python main_download.py " + "--station {station} --network {network}"

colors = ['red', 'green', 'blue', 'yellow', 'white', 'blue']


codes = namedtuple('Codes', ['station', 'network'])

def path_exists(station):
    if os.path.exists(f'waveforms/{station.latitude}-{station.longitude}') or os.path.exists(f'waveforms/{station.latitude}-{station.longitude}-minmag1'):
        return True
    return False


def get_docker_commands(inventory: Inventory):
    commands = [cmd.format(station=station.code, network=network.code)
                for network in inventory
                for station in network 
                if not path_exists(station)]

    random.shuffle(commands)
    return [command.split() for command in commands]



def get_num_running_containers(image_name):
    result = run(['docker', 'ps'], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return len(re.findall(image_name, result.stdout))

def print_logs(image_name):
    result = run(['docker', 'ps'], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    res = re.findall('[\w]{12}        ' + image_name, result.stdout)
    for i, container_id in enumerate([r.split()[0] for r in res]):
        result = run(['docker', 'logs', container_id])
        if result.stdout:
            print(colored(container_id + " -> " + result.stdout, colors[i]))

def run_container(command):
    result = Popen(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)


commands = iter(get_docker_commands(inventory))

# Run infinitely to keep downloading waveforms
while True:
    num_containers = get_num_running_containers(img_name)
    if num_containers <= 10:
        run_container(next(commands))
    print_logs(img_name)
    time.sleep(1)