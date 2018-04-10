from .config import *
from typing import List
from obspy import Stream


__all__ = ['filter_waveforms', 'filter_waveform']

def filter_waveform(stream: Stream, event_start, pre_padding, post_padding):
    """
    Start PRE_PADDING before event_time, end POST_PADDING after event_time
    :param stream: stream to use
    :param event_start: time of the event
    :param pre_padding: time to start before event_start
    :param post_padding: time to end after event_start
    :return:
    """
    pad = 5
    window_start = event_start - pre_padding
    window_end = event_start + post_padding
    stream = stream.slice(window_start - pad, window_end + pad)
    stream.filter('bandpass', freqmin=MIN_FREQ, freqmax=MAX_FREQ)
    return stream.trim(window_start + pad, window_end + pad)


def filter_waveforms(waveforms: List[Stream]) -> List[Stream]:
    """
    Filters the waveforms (in place)
    Only to be used with the main_download function, because it requires coordination fot he stream starttime and the PADDING
    @return: generator -> Stream
    """
    for stream in waveforms:
        event_start = stream[0].stats.starttime + PADDING
        window_start = event_start - PRE_PADDING
        window_end = event_start + POST_PADDING
        stream.filter('bandpass', freqmin=MIN_FREQ, freqmax=MAX_FREQ)
        stream.trim(window_start, window_end)

    return waveforms


