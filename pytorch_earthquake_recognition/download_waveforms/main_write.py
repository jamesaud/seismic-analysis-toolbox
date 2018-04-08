import matplotlib
matplotlib.use('agg')

import os
import warnings
from code.config import WAVEFORMS_PATH, SPECTROGRAM_PATH
from code.spectrograms import async_write_spectrograms
from code.waveforms import read_waveforms
from code.filter import filter_waveforms

noise_path =  os.path.join(WAVEFORMS_PATH, "noise")
local_path =  os.path.join(WAVEFORMS_PATH, "local")

local_waveforms = read_waveforms(local_path)
noise_waveforms = read_waveforms(noise_path)

local_waves = filter_waveforms(local_waveforms)
noise_waves = filter_waveforms(noise_waveforms)

print("Filtered")

# Write Waveforms
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    async_write_spectrograms(local_waves, os.path.join(SPECTROGRAM_PATH, "local"))
    async_write_spectrograms(noise_waves, os.path.join(SPECTROGRAM_PATH, "noise"))