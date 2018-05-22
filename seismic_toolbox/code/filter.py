from .config import *
from typing import List
from obspy import Stream

PAD = 5

def filter_waveform(stream: Stream, event_start, pre_padding, post_padding, pad=PAD):
    """
    Start PRE_PADDING before event_time, end POST_PADDING after event_time
    :param stream: stream to use
    :param event_start: time of the event
    :param pre_padding: time to start before event_start
    :param post_padding: time to end after event_start
    :return:
    """
    window_start = event_start - pre_padding
    window_end = event_start + post_padding
    stream = stream.slice(window_start - pad, window_end + pad)
    resample(stream, 100)
    bandpass(stream)
    return stream.slice(window_start + pad, window_end + pad)


def filter_waveform_by_time(stream: Stream, start, end, *args, **kwargs):
    return filter_waveform(stream, start, 0, end - start, *args, **kwargs)


def filter_waveforms(waveforms: List[Stream], pre_padding=PRE_PADDING,
                     post_padding=POST_PADDING, padding=PADDING) -> List[Stream]:
    """
    Filters the waveforms (in place)
    Padding adjusts the window to the write place from the start of the stream.
    eg. if the event occurs 20 seconds intto the stream, set padding to 20
    :return: generator -> Stream
    """

    for stream in waveforms:
        event_start = stream[0].stats.starttime + padding
        window_start = event_start - pre_padding
        window_end = event_start + post_padding
        resample(stream, 100)
        bandpass(stream)
        stream.trim(window_start, window_end)

    return waveforms


def bandpass(stream, freqmin=MIN_FREQ, freqmax=MAX_FREQ):
    return stream.filter('bandpass', freqmin=freqmin, freqmax=freqmax)

def resample(stream, rate):
    return stream.resample(rate)