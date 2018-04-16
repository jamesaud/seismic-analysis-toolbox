import matplotlib
matplotlib.use('agg')
import argparse
import os
import warnings
from code.config import WAVEFORMS_PATH, SPECTROGRAM_PATH
from code.spectrograms import async_write_spectrograms
from code.waveforms import read_waveforms
from code.filter import filter_waveforms




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

    return parser

if __name__ == '__main__':
    print("Preparing to write...")
    parser = get_parser()
    args = parser.parse_args()

    WAVEFORMS_PATH = args.waveform_path
    SPECTROGRAM_PATH = args.spectrogram_path

    noise_path = os.path.join(WAVEFORMS_PATH, "noise")
    local_path = os.path.join(WAVEFORMS_PATH, "local")

    print("Reading waveforms")
    local_waveforms = read_waveforms(local_path)
    noise_waveforms = read_waveforms(noise_path)

    print("Filtering waveforms")
    local_waves = filter_waveforms(local_waveforms,
                                   pre_padding=9,
                                   post_padding=11,
                                   padding=20)

    noise_waves = filter_waveforms(noise_waveforms,
                                   pre_padding=10,
                                   post_padding=10,
                                   padding=20)

    print("Filtered")

    print("Writing waveforms.")
    # Write Waveforms
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        async_write_spectrograms(local_waves, os.path.join(SPECTROGRAM_PATH, "local"))
        async_write_spectrograms(noise_waves, os.path.join(SPECTROGRAM_PATH, "noise"))