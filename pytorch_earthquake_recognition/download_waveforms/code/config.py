import os
from collections import namedtuple
from obspy.clients.fdsn import Client
from obspy.core.utcdatetime import UTCDateTime
from types import MappingProxyType

# Holds a UTCDateTime start and end times of an event
Time = namedtuple('Time', ('start', 'end'))

class Names:
    Amatrice = 'Amatrice'
    Oklahoma = 'Oklahoma'
    SouthAmerica = 'SouthAmerica'
    California = 'California'
    Alaska = 'Alaska'
    Costa = 'Costa'
    Puerto = 'Puerto'
    Utah = 'Utah'


def Day(num):
    return 60 * 60 * 24 * num


def get_event_info(name):
    """
    Provids a dictionary (MappingProxyType) of information to populate the global variables needed in the file.
    The chosen event is in a seismologically active area. A station is chosen near the event to get data.
    @param name: Can be one of - "Amatrice", "Patitirion"
    @return: ProxyMapType, containing the information about the event.
    """
    info: MappingProxyType = None
    if name == Names.Amatrice:
        info = dict(
            Latitude='42.790',
            Longitude='13.150',
            Time="2016-08-24 03:36:32",
            StartTime="2012-08-24",
            EndTime="2018-08-24",
            Client="INGV",
            Name="Amatrice",
            PrePadding=4,
            PostPadding=16,
            StationRadius=.2,
            LocalEventRadius=.2
        )

    elif name == Names.Oklahoma:
        info = dict(
            Latitude='37.081',
            Longitude='-97.309',
            Time="2018-5-15 20:14:49",
            StartTime="2015-10-15",
            EndTime="2017-10-15",
            Client="IRIS",
            Name="Oklahoma",
            PrePadding=6,
            PostPadding=14,
            Network="GS",
            Station='KAN01',
            StationRadius=1,
        )

    elif name == Names.SouthAmerica:
        info = dict(
            Latitude='-25.3',
            Longitude='-71',
            Time="2018-02-20 23:18:32",
            StartTime="2013-10-15",
            EndTime="2018-01-15",
            Client="IRIS",
            Name="SouthAmerica",
            PrePadding=3,
            PostPadding=17,
            AddTime=10,
            Network='C',
            Station='GO02',
            StationRadius=3,
        )

    elif name == Names.California:
        info = dict(
            Latitude='33.557',
            Longitude='-115.888',
            Time="2018-02-20 23:18:32",
            StartTime="2016-10-15",
            EndTime="2018-01-15",
            Client="IRIS",
            Name="California",
            PrePadding=8,
            PostPadding=12,
            StationRadius=1,
        )

    elif name == Names.Alaska:
        info = dict(
            Latitude='61',
            Longitude='-150',
            Time="2018-02-20 23:18:32",
            StartTime="2015-01-01",
            EndTime="2017-02-26",
            Client="IRIS",
            Network="AK",
            Station="FIRE",
            Name="Alaska",
            PrePadding=5,
            PostPadding=15,
            StationRadius=2,
        )

    elif name == Names.Costa:
        info = dict(
            Latitude='19.433',
            Longitude='-155',
            Time="2005-02-20",
            StartTime="2014-05-05",
            EndTime="2018-02-26",
            Client="IRIS",
            Network="NU",
            Station="BC8A",
            Name="Costa",
            PrePadding=5,
            PostPadding=15,
            StationRadius=1,
        )

    elif name == Names.Puerto:
        info = dict(
            Latitude='18',
            Longitude='-67',
            Time="2005-02-20",
            StartTime="2014-05-05",
            EndTime="2018-02-26",
            Client="IRIS",
            Network="PR",
            Station="AGPR",
            Name="Puerto",
            PrePadding=7,
            PostPadding=13,
            StationRadius=3,
        )

    elif name == Names.Utah:
        info = dict(
            Latitude='38',
            Longitude='-112',
            Time="2006-04-20",
            StartTime="2015-10-05",
            EndTime="2018-02-26",
            Client="IRIS",
            Network="NN",
            Station="DSP",
            Name="Utah",
            PrePadding=5,
            PostPadding=15,
            StationRadius=5,
        )

    if info:
        return MappingProxyType(info)
    raise ValueError(f"Name '{name}' not found")


# Retrieving the quake information
event = get_event_info(os.environ.get('Location', 'Utah')) #get_event_info(os.env['Location'])   # dict containing the information to populate the variables

# Constants
LATITUDE = event['Latitude']  # Latitude of Event
LONGITUDE = event['Longitude']  # Longitude of Event
STARTTIME = UTCDateTime(event['StartTime'])  # Starttime of Data Collection
ENDTIME = UTCDateTime(event['EndTime'])  # Endtime of Data Collection
CLIENT_NAME = event['Client']  # Client to retrieve event from
NAME = event['Name'] + 'Quakes'  # Folder name to write spectrograms to

STATION_MAX_RADIUS = event['StationRadius']  # Pick as station within this distance of the event
MAX_RADIUS = 1.5  # How far local events can be from the station
NONLOCAL_MIN_RADIUS = 6  # Min Radius for Nonlocal Events

NUM_EVENTS = 4000                             # How many events to retrieve and write                     # Event time window duration
NUM_NOISE_EVENTS = 4000

DURATION = 20  # Time in seconds, centered around the event
PADDING = 20  # Get waveforms padding length, and then trim to the duration after filtering
ADD_TIME = event.get('AddTime', 0)  # Time to add to all events to correct for arrival times

PRE_PADDING = event['PrePadding']
POST_PADDING = event['PostPadding']

# Time period to collect noise events
NOISE_START = STARTTIME
NOISE_END = NOISE_START + Day(60)

# If specific network and station are specified
NETWORK = event.get('Network')
STATION = event.get('Station')

# Filtering Constants for the Spectrograms
MIN_FREQ = 1
MAX_FREQ = 30

# Paths
WAVEFORMS_PATH = os.path.join(os.getcwd(), f"waveforms/{NAME}")
SPECTROGRAM_PATH = os.path.join(os.getcwd(), f"spectrograms/{NAME}")

# Code
client = Client(CLIENT_NAME)

assert PRE_PADDING + POST_PADDING == DURATION