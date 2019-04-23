from obspy.core import Stream
from obspy.core.event.event import Event
from pprint import pprint
from obspy.taup import TauPyModel
from obspy.geodetics.base import gps2dist_azimuth
from obspy.geodetics import kilometers2degrees
from multiprocessing import Pool
from functools import partial
from obspy.taup.helper_classes import SlownessModelError
from obspy.core.inventory import Station
from obspy.core.event import Catalog
from obspy.core import UTCDateTime
from typing import List
from collections import defaultdict
import math
from .helpers import create_directory
import os

# Constants
model = TauPyModel(model="prem")


def get_magnitudes(catalog: Catalog):
    """
    :return: dict, the range -1 to 0, 0 to 1, 1 to 2, etc. as magntitude buckets.
    """
    mags = defaultdict(lambda: 0)
    for event in catalog:
        magnitude = event.magnitudes[0].mag
        mags[math.trunc(magnitude)] += 1
    return mags


def write_events(catalog, path):
    create_directory(path)
    catalog.write(os.path.join(path, 'events.xml'), format="QUAKEML")


def get_event_time(station, event, give_anyways=False) -> UTCDateTime:
    """ Corrects an event time when it arrived at a station, correcting for the PREM distance.
    :param give_anyways: If the p_arrival can't be computed, give back the original time anyways
    :return: List[UTCDateTime]
             Errors will be stored as 'None' in the list, so that parallelization won't encounter Exceptions. I'm sure there's a better way to parallize the code.
    """
    event_time = event.origins[0].time
    try:
        p_arrival, s_arrival = compute_distance(station, event)
    except (SlownessModelError, IndexError) as e:
        if not give_anyways:
            return None
        p_arrival = 0
        s_arrival = 0
    event_time += s_arrival
    return event_time


def get_event_times(catalog: Catalog, station: Station) -> List[UTCDateTime]:
    """
    Gets event times from a catalog and returns a list of them, corrected with the above functino.
    """
    times = [get_event_time(station, event) for event in catalog]
    times = filter(lambda time: time is not None, times)  # Remove errored times
    return list(times)


def compute_distance(station: Station, event: Event):
    """ Computes the time offset of an event to reach a station, based on PREM """
    origin = event.origins[0]

    event_distance = gps2dist_azimuth(station.latitude, station.longitude,
                                      origin.latitude, origin.longitude)[0]

    depth = origin.depth / 1000
    distance = kilometers2degrees(event_distance / 1000)  # Meter to kilometer to degrees
    arrivals = model.get_travel_times(source_depth_in_km=depth,  # meter to kilometer
                                      distance_in_degree=distance,
                                      phase_list=["p", "s", "P", "S"]
                                      )

    p, s = arrivals[0].time, arrivals[1].time  # Time in seconds
    return p, s


def parallel_get_event_times(catalog: Catalog, station, give_anyways=False):
    """
    Parallelizes the 'get_event_time' function to make computation faster.
    :param give_anyways: call 'get_event_time' with give_anyways set to True
    """
    work = catalog  # Args that will be passed to the function

    # Run with multiprocess
    pool = Pool()
    if give_anyways:
        times = pool.map(partial(get_event_time, station, give_anyways=True), work)  # Map the args
    else:
        times = pool.map(partial(get_event_time, station), work)
    times = filter(lambda time: time is not None, times)  # Remove errored times
    return list(times)