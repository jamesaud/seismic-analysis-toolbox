from typing import List
from obspy import Stream
from multiprocessing import Pool
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
import glob
import os
from .config import *
from .helpers import get_channel_names, create_directory
from subprocess import Popen


# def remove_borders(path):
#     """
#     Removes borders of all .png files in curr directory
#     Must have ImageMagik installed.
#     """
#     png_paths = glob.glob(f"{path}/*.png")
#
#     for file in png_paths:
#         print("Trimming: ", file, end='\r')
#         !convert $file - trim + repage $file;

def remove_borders(path):
    """
    Removes borders of all .png files in curr directory
    Must have ImageMagik installed.
    """
    png_paths = glob.glob(f"{path}/*.png")

    for file in png_paths:
        print("Trimming: ", file, end='\r')
        Popen(["convert", file, "-trim", "+repage", file])


def show_spectrogram(stream):
    figure_list = stream.spectrogram(show=False, title="")

    for figure, channel in zip(figure_list, get_channel_names(stream)):
        if channel in ('HNE', 'HNN', 'HNZ'):
            axes = figure.gca()
            axes.set_xlim([0, DURATION])
            axes.set_ylim([0, MAX_FREQ])

            # Get Rid of Whitespace
            axes.axis("off")
            axes.xaxis.set_major_locator(NullLocator())
            axes.yaxis.set_major_locator(NullLocator())

    plt.show()


def write_spectrogram(stream, path):
    """
    @param stream: Stream, the file to make a spectrogram from.
                   Each trace should be one component.

    @param path: Str, the directory to write into.

    Each component of the stream is written as its own figure, a .png file.
    Components eg. "NNE" are saved as the filename eg. "NNE.png".
    """
    create_directory(path)
    figure_list = stream.spectrogram(show=False, title="")

    for figure, channel in zip(figure_list, get_channel_names(stream)):
        axes = figure.gca()
        axes.set_xlim([0, DURATION])
        axes.set_ylim([0, MAX_FREQ])

        # Get Rid of Whitespace
        axes.axis("off")
        axes.xaxis.set_major_locator(NullLocator())
        axes.yaxis.set_major_locator(NullLocator())

        DPI = figure.get_dpi()
        figure.set_size_inches(400 / float(DPI), 336 / float(DPI))
        figure.savefig(f"{path}/{channel}.png", bbox_inches='tight', pad_inches=0, transparent=True)

        # Free memory
        figure.clf()
        plt.close("ALL")

    remove_borders(path)  # Remove borders of all the spectrograms


def write_spectrogram_ignore_exceptions(*args, **kwargs):
    try:
        return write_spectrogram(*args, **kwargs)
    except Exception as e:
        print(type(e))
        print("Failed to write spectrogram: ", e)
        return None


def write_spectrograms(waveforms, path, startat=0):
    for i, stream in enumerate(waveforms, startat):
        dir_path = os.path.join(path, str(i))
        create_directory(dir_path)
        write_spectrogram(stream, dir_path)


def async_write_spectrograms(waveforms, path, startat=0, ignoreexceptions=True):
    """
    @param waveforms: List[Stream], the waveforms to make spectrograms from.
    @param path: str, The directory to write to

    1. Calls 'write_spectrogram' on each Stream.
    2. Each stream is written to its own folder
    3. All components are written to their own file as a spectrogram .png image.
    """
    print("Writing Files...")

    work = []  # Args that will be passed to the write_spectrogram function

    # Prep the file paths
    for i, stream in enumerate(waveforms, startat):
        dir_path = os.path.join(path, str(i))
        create_directory(dir_path)

        # Add the args for each stream
        work.append(
            (stream, os.path.join(path, str(i)))  # arguments to the 'write_spectrogram' function
        )

    # Run with multiprocess
    pool = Pool()
    if ignoreexceptions:
        pool.starmap(write_spectrogram_ignore_exceptions, work)  # Map the 'write_spectrogram' function to the work
    else:
        pool.starmap(write_spectrogram, work)
    print("\nWrote Files")
