from .config import *
from obspy import UTCDateTime
from obspy.core.inventory import Inventory, Station, Network
from obspy.clients.fdsn import Client
import random
import math
from bisect import bisect
from typing import List

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_all_stations(max_radius) -> Inventory:
    """ Use this to find a valid station with the correct components """
    return client.get_stations(latitude=LATITUDE,
                               longitude=LONGITUDE,
                               maxradius=max_radius)

def get_channel_names(stream):
    """ Returns a list of names of each component, in the order they appear in the stream """
    return [trace.stats.channel for trace in stream]

def verify_fsdn(network, station, starttime=STARTTIME):
    """
    Makes a call to the server. Requires 'HN*' component, and the ability to 'get_waveforms' from the station
    Sometimes the stations are missing data, so it's important to actually make a request and get the waveform data.
    """
    client = Client(CLIENT_NAME)
    time = starttime + Day(365)
    waves = client.get_waveforms(network.code, station.code, "*", "HN*", time, time + DURATION)
    return True

def get_valid_stations(inventory):
    """ Attempts to get waveforms from a station, with the veriy_fsdn function. Returns valid stations. """
    valid = []
    for network in inventory:
        for station in network:
            try:
                verify_fsdn(network, station)
            except Exception:
                print("Failed station:", station.code)
            else:
                print("Succeeded station:", station.code, network.code)
                valid.append(station)
    return valid


def find_closest_index(a, x):
    """
    Find index of rightmost value less than x via binary search
    @param a: Indexable object, the list to look through - MUST BE SORTED
    @param x: Any, the item to find the closest index for in a
    """
    i = bisect(a, x)
    if i:
        return i
    return 0


def overlaps(time: Time, time2: Time):
    """
    Determines whether two times overlap.
    @returns: boolean, True if the time1 overlaps with time2
    """
    # Starts after the second time ends, or ends before the second time starts
    return not ((time.start > time2.end) or (time.end < time2.start))


def encompassed(time: Time, sorted_times: List[Time]):
    """
    Determines whether time overlaps with any times in sorted_times
    @param time: Time
    @param sorted_times: sorted list of Time - the list MUST be sorted for this to work
    @return: boolean, True if the time overlaps
    """
    index = find_closest_index(sorted_times, time)
    try:
        left = overlaps(time, sorted_times[index - 1])
        curr = overlaps(time, sorted_times[index])
        right = overlaps(time, sorted_times[index + 1])
        return any((left, curr, right))
    except IndexError:
        return True


def get_noise_times(times_to_exclude: List[UTCDateTime],
                    startafter: UTCDateTime, endbefore: UTCDateTime, amount: int, duration: float):
    """
    Generates a list of noise times, which are not in the times_to_exclude
    @param times_to_exclude: a list of times of events
    @param startafter: Generate noise windows after this time
    @param endbefore: Generate noise windows before this time
    @param amount: How many noise windows to generate
    @param duration: How long each event in times_to_exclude and noise window should be, to prevent overlapping
    """
    exclude = [Time(time - duration / 2, time + duration / 2) for time in times_to_exclude]
    exclude.sort()
    noise_times = []

    def random_time():
        return startafter + random.randint(0, math.floor(endbefore - startafter))

    # Generate a random time
    while len(noise_times) < amount:
        rt = random_time()
        rand_time = Time(rt - duration / 2, rt + duration / 2)

        if not encompassed(rand_time, exclude):
            noise_times.append(rt)
            index = bisect(exclude, rand_time)
            exclude = exclude[:index] + [rand_time] + exclude[index:]

    return noise_times

def slide(iterable, num, stagger=None):
    """
    A sliding window over an iterator, yielding sub arrays.
    @param iterable: Iterable
    @param num: int, the size of each subarray
    @param stagger: int, the number of elements to start the next subarray by

    Example:
    for arr in slide(list(range(98)), 5):
        print(arr)
    """
    stagger = num - stagger if stagger else 0
    start = 0
    end = num

    while start + stagger < len(iterable):
        yield iterable[start:end]
        start = end - stagger
        end += num - stagger