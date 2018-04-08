from .config import *
from typing import List
from obspy import Stream

def filter_waveforms(waveforms: List[Stream]) -> List[Stream]:
    """
    Filters the waveforms (in place)
    @return: generator -> Stream
    """
    assert PRE_PADDING + POST_PADDING == DURATION
    for stream in waveforms:
        event_start = stream[0].stats.starttime + PADDING
        window_start = event_start - PRE_PADDING
        window_end = event_start + POST_PADDING
        stream.filter('bandpass', freqmin=MIN_FREQ, freqmax=MAX_FREQ)
        stream.trim(window_start, window_end)

    return waveforms