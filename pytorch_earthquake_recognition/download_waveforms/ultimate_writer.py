import glob
import os
import pathlib
import subprocess
from subprocess import call, Popen, PIPE, run

from termcolor import colored

cwd = os.getcwd()
CMD = f"""docker run -v {cwd}/waveforms:/data/waveforms 
                     -v {cwd}/spectrograms:/data/spectrograms
                     -e PYTHONUNBUFFERED=0 
                      downloadwaveforms_spectro-dind 
                      python main_write.py 
                      """ + \
      "--waveform_path {waveform_path} --spectrogram_path {spectrogram_path}"

img_name = 'downloadwaveforms_spectro-dind'

PATH = 'waveforms'
SPECTROGRAM_PATH = 'spectrograms'
LIMIT = 1000

def get_valid_folders(path, limit):
    dirs = glob.glob(os.path.join(path, '*/'))

    def is_valid(directory):
        local = 'local'
        noise = 'noise'
        local_files = os.path.join(directory, local)
        noise_files = os.path.join(directory, noise)

        def bigger_than_limit(path):
            return len(os.listdir(path)) > limit

        return bigger_than_limit(local_files) and bigger_than_limit(noise_files)

    return filter(is_valid, dirs)


def get_write_paths(spectrogram_path, read_paths):

    def make_name(path):
        path = pathlib.Path(path)  # ensures standard format of paths
        path = os.path.basename(path) # get folder name
        path = os.path.join(spectrogram_path, path)
        return path

    return map(make_name, read_paths)


def get_docker_commands(read_paths, write_paths):
    commands = []
    for read, write in zip(read_paths, write_paths):
        commands.append(CMD.format(waveform_path=read, spectrogram_path=write))
    return [cmd.strip().split() for cmd in commands]

import random
colors = ['red', 'blue', 'green', 'yellow', 'white']

def run_container(cmd):
    print("Running container")
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
        for line in p.stdout:
            print(colored(line, random.choice(colors)))


def make_path(path):
    if not os.path.exists(path):
        os.mkdir(path)

make_path(SPECTROGRAM_PATH)

read_paths = list(get_valid_folders(PATH, LIMIT))
write_paths = list(get_write_paths(SPECTROGRAM_PATH, read_paths))
commands = get_docker_commands(read_paths, write_paths)

run_container(commands[0])