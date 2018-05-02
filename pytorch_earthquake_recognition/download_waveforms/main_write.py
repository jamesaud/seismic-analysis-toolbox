import matplotlib
matplotlib.use('agg')
import argparse
import os
import warnings
from code.config import WAVEFORMS_PATH, SPECTROGRAM_PATH
from code.spectrograms import async_write_spectrograms
from code.waveforms import read_waveforms
from code.filter import filter_waveforms


def valid_type(string):
    string = string.strip()
    if string not in ['noise', 'local']:
        raise ValueError("Should be 'noise' or 'local'")
    return string

def get_parser():
    parser = argparse.ArgumentParser(description='Get configuration.')
    parser.add_argument('--waveform_path',
                        dest='waveform_path',
                        type=str,
                        required=True,
                        help='waveforms path')

    parser.add_argument('--spectrogram_path',
                        dest='spectrogram_path',
                        type=str,
                        required=True,
                        help='spectrogram_path')

    parser.add_argument('--type',
                        dest='type',
                        type=valid_type,
                        default=None,
                        help="Type should be 'noise' or 'local'")

    return parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    WAVEFORMS_PATH = args.waveform_path
    SPECTROGRAM_PATH = args.spectrogram_path
    val_type = args.type
    print("Preparing to write... ")

    noise_path = os.path.join(WAVEFORMS_PATH, "noise")
    local_path = os.path.join(WAVEFORMS_PATH, "local")


    def write_local():
        print("Writing local")
        local_waveforms = read_waveforms(local_path)
        local_waves = filter_waveforms(local_waveforms,
                                       pre_padding=7,
                                       post_padding=13,
                                       padding=20)
        async_write_spectrograms(local_waves, os.path.join(SPECTROGRAM_PATH, "local"))

    def write_noise():
        print("Writing noise")
        noise_waveforms = read_waveforms(noise_path)
        noise_waves = filter_waveforms(noise_waveforms,
                                       pre_padding=10,
                                       post_padding=10,
                                       padding=20)
        async_write_spectrograms(noise_waves, os.path.join(SPECTROGRAM_PATH, "noise"))


    # Write Waveforms
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if val_type is None:
            write_local()
            write_noise()

        elif val_type == 'local':
            write_local()

        elif val_type == 'noise':
            write_noise()

