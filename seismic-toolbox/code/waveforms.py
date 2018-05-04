from typing import List
from obspy import Stream
from multiprocessing import Pool
import os
from obspy import read
import glob
from .helpers import create_directory



def write_waveforms(waveforms: List[Stream], path):
    create_directory(path)
    for i, stream in enumerate(waveforms):
        stream.write(os.path.join(path, f'{i}.mseed'), format="MSEED")


def write_waveform(stream, file_path):
    print("Writing: ", os.path.basename(file_path), end='\r')
    stream.write(file_path, format="MSEED")


def parallel_write_waveforms(waveforms: List[Stream], path):
    print("Writing Waveforms...")
    create_directory(path)

    work = []

    # Prep the file paths
    for i, stream in enumerate(waveforms):
        file_path = os.path.join(path, f'{i}.mseed')

        # Add the args for each stream
        work.append(
            (stream, file_path)
        )

    # Run with multiprocess
    pool = Pool()
    pool.starmap(write_waveform, work)

    print("\nWrote Waveforms")


def remove_response(waveforms: List[Stream]):
    for stream in waveforms:
        stream.remove_response(output='DISP', water_level=140)


def read_waveforms(dir_path):
    files = glob.glob(os.path.join(dir_path, '*.mseed'))
    waveforms = [read(file) for file in files]
    return waveforms