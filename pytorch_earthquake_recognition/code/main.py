from obspy.core.inventory import Inventory, Station, Network
from obspy.clients.fdsn import Client
from obspy.core.event import Catalog
from .config import *
from .helpers import *
import warnings
from .events import get_event_times

# Types
inventory: Inventory
network: Network
station: Station

# NETWORK = 'NP'
# STATION = '7202'

inventory = client.get_stations(network=NETWORK,
                                station=STATION)

# By default, get the first station and network unless specified
network = inventory.select(NETWORK)[0]
station = network.select(STATION)[0]


# Verifies that the selected station supports 'get_waveforms' - saves time to not run the rest of the code
assert verify_fsdn(network, station)


# Visualize the Station
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    network.select(STATION).plot(projection='local')

# Types
local_catalog_events: Catalog
nonlocal_catalog_events: Catalog

# Code
client = Client(CLIENT_NAME)

# Local Events
local_catalog = client.get_events(latitude=station.latitude,
                                  longitude=station.longitude,
                                  maxradius=MAX_RADIUS,  # Local
                                  starttime=STARTTIME,
                                  limit=NUM_EVENTS,
                                  endtime=ENDTIME
                                  )

# Noise Exclude Events
noise_catalog = client.get_events(latitude=station.latitude,
                                  longitude=station.longitude,
                                  starttime=NOISE_START,
                                  endtime=NOISE_END,
                                  maxradius=10
                                  )

print("LOCAL EVENTS:", len(local_catalog))
print("NOISE EVENTS to Exclude:", len(noise_catalog))


# Plot Events
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    local_catalog.plot(projection="local")

# Types
local_times: List[UTCDateTime]
nonlocal_times: List[UTCDateTime]
noise_times: List[UTCDateTime]

# Code
local_times = get_event_times(local_catalog, station)
nonlocal_times = get_event_times(nonlocal_catalog, station)
_noise_times = get_event_times(noise_catalog, station)

noise_times = get_noise_times(_noise_times,
                              NOISE_START,  # startafter
                              NOISE_END,  # endbefore
                              NUM_NOISE_EVENTS,
                              DURATION)

print("Got times")