import glob
import os
import pathlib
import subprocess
from subprocess import call, Popen, PIPE, run
import random
from termcolor import colored

img_name = 'downloadwaveforms_spectro'
cwd = os.getcwd()
CMD = f"""docker run -v {cwd}/waveforms:/data/waveforms 
                     -v {cwd}/spectrograms:/data/spectrograms
                     -e PYTHONUNBUFFERED=0 
                      {img_name} 
                      python main_write.py 
                      """ + \
 "--waveform_path {waveform_path} --spectrogram_path {spectrogram_path} --type {valid_type}"

PATH = 'waveforms'
SPECTROGRAM_PATH = 'spectrograms'
LIMIT = 500

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



def get_basename(path):
    path = pathlib.Path(path)  # ensures standard format of paths
    path = os.path.basename(path)  # get folder name
    return path

def get_write_paths(spectrogram_path, read_paths):

    def make_name(path):
        path = get_basename(path)
        path = os.path.join(spectrogram_path, path)
        return path

    return map(make_name, read_paths)


def get_docker_commands(read_paths, write_paths):
    commands = []
    for read, write in zip(read_paths, write_paths):
        # Run noise/local in separate contianers to better use memory
        cmd_1 = CMD.format(waveform_path=read, spectrogram_path=write, valid_type='local')
        cmd_2 = CMD.format(waveform_path=read, spectrogram_path=write, valid_type='noise')
        commands.append(cmd_1)
        commands.append(cmd_2)

    return [cmd.strip().split() for cmd in commands]


def remove_existing_paths(read_paths, spectrogram_path):
    existing_paths = glob.glob(os.path.join(spectrogram_path, '*/'))
    basenames = map(get_basename, existing_paths)
    basenames = set(basenames)
    valid_read_paths = [path for path in read_paths
                        if get_basename(path) not in basenames]

    return valid_read_paths


colors = ['red', 'blue', 'green', 'yellow', 'white']


def run_container(cmd):
    print("Running container")
    color = random.choice(colors)
    with subprocess.Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(colored(line, color))


def make_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


make_path(SPECTROGRAM_PATH)

read_paths = get_valid_folders(PATH, LIMIT)
read_paths = remove_existing_paths(read_paths, SPECTROGRAM_PATH)
write_paths = get_write_paths(SPECTROGRAM_PATH, read_paths)

commands = reversed(get_docker_commands(read_paths, write_paths))

for cmd in commands:
    run_container(cmd)
