import matplotlib

matplotlib.use('agg')

import argparse
import obspy
from obspy.core.stream import read
import os
import sys
from pprint import pprint

cwd = os.getcwd()

from seismic_code import spectrograms
from seismic_code.helpers import slide, create_directory
from seismic_code.filter import filter_waveform_by_time
from seismic_code.spectrograms import write_spectrogram
from seismic_code.waveforms import write_waveform
import copy

PAD = 5

def make_name(starttime, endttime):
    return str(starttime) + '--' + str(endttime)


def filter_waveforms(stream, start, end, duration, separation):
    for time in range(start, end, duration + separation):
        start_time = stream[0].stats.starttime + time
        end_time = start_time + duration
        yield filter_waveform_by_time(stream, start_time, end_time, pad=PAD)


def wavenames(waveforms):
    for waveform in waveforms:
        yield waveform, make_name(waveform[0].stats.starttime, waveform[0].stats.endtime)


def write_files(wave_names, base_path, write_wave=True, write_spectro=True):
    for stream, name in wave_names:
        dir_path = os.path.join(base_path, name)
        create_directory(dir_path)

        if write_spectro:
            write_spectrogram(stream, dir_path)
            print("Wrote Spectrogram: " + name, end='\r')

        if write_wave:
            write_waveform(stream, os.path.join(dir_path, 'waveform.mseed'))
            print("Wrote Waveform: " + name, end='\r')


def get_parser():
    parser = argparse.ArgumentParser(description='Get configuration')
    parser.add_argument('--start',
                        dest='start',
                        type=int,
                        required=True,
                        help='start time in seconds')

    parser.add_argument('--duration',
                        dest='duration',
                        type=int,
                        required=True,
                        help='duration in seconds')

    parser.add_argument('--end',
                        dest='end',
                        type=int,
                        required=True,
                        help='time in seconds from start to make the duration lengthed intervals from')

    parser.add_argument('--separation',
                        dest='separation',
                        type=int,
                        default=0,
                        help='separation between interval in seconds')

    parser.add_argument('--write_path',
                        dest='write_path',
                        type=str,
                        help='spectrogram write path')

    parser.add_argument('--read_file',
                        dest='read_file',
                        type=str,
                        help='waveform read path')

    parser.add_argument('--write_spectrograms',
                        dest='write_spectrograms',
                        type=lambda x: x.lower() != 'false',
                        default=True,
                        help='enable writing spectrograms (options are "True" or "False")')
    return parser


if __name__ == '__main__':
    args = get_parser().parse_args()
    start = args.start
    duration = args.duration
    end = args.end
    separation = args.separation
    write_path = args.write_path
    path = args.read_file
    write_spectro = args.write_spectrograms

    print("Reading Stream...")
    stream = read(path)

    print("Filtering Waveforms...")
    waveforms = filter_waveforms(stream, start, end, duration, separation)
    waveform_paths = wavenames(waveforms)

    print("Writing files")
    write_files(waveform_paths, write_path, write_spectro=write_spectro)
