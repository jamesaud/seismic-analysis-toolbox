import matplotlib
matplotlib.use('agg')

from code.config import *
from code.events import parallel_get_event_times
from code.waveforms import parallel_write_waveforms
from obspy.core.event import Catalog
from code.helpers import *
from code.async_client import AsyncClient
import warnings

if __name__ == '__main__':
    print("Starting Download Script...")
    # Types
    inventory: Inventory
    network: Network
    station: Station
    local_catalog_events: Catalog
    nonlocal_catalog_events: Catalog
    local_times: List[UTCDateTime]
    nonlocal_times: List[UTCDateTime]
    noise_times: List[UTCDateTime]

    # Code
    client = AsyncClient(CLIENT_NAME)
    inventory = client.get_stations(network=NETWORK,
                                    station=STATION)
    network = inventory.select(NETWORK)[0]
    station = network.select(STATION)[0]

    # Verifies that the selected station supports 'get_waveforms' - saves time to not run the rest of the code
    assert verify_fsdn(network, station)

    # Visualize the Station
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        network.select(STATION).plot(projection='local')

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

    # Code
    local_times = parallel_get_event_times(local_catalog, station)
    _noise_times = parallel_get_event_times(noise_catalog, station,
                                            give_anyways=True)  # Even if PREM arrival can't be computed, get event times

    noise_times = get_noise_times(_noise_times,
                                  NOISE_START,  # startafter
                                  NOISE_END,  # endbefore
                                  NUM_NOISE_EVENTS,
                                  DURATION)
    print("Got times")

    # Functions
    end = lambda time: time + PADDING + ADD_TIME
    start = lambda time: time - PADDING + ADD_TIME


    def create_bulk(times):
        return [(network.code, station.code, "*", "HN*", start(time), end(time)) for time in times]


    local_bulk = create_bulk(local_times)
    noise_bulk = create_bulk(noise_times)
    print("Created Bulks")

    # Get Waveforms
    local_waveforms = client.get_waveforms_bulk(local_bulk,
                                                batch_size=5,
                                                bulk_kwargs=dict(attach_response=True),
                                                skip_errors=True)
    print("\nRetrieved Local:", len(local_waveforms))

    noise_waveforms = client.get_waveforms_bulk(noise_bulk,
                                                batch_size=5,
                                                bulk_kwargs=dict(attach_response=True),
                                                skip_errors=True)
    print("\nRetrieved Noise:", len(noise_waveforms))

    # Write Waveforms
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        parallel_write_waveforms(local_waveforms, os.path.join(WAVEFORMS_PATH, "local"))
        parallel_write_waveforms(noise_waveforms, os.path.join(WAVEFORMS_PATH, "noise"))

    print("Finished Writing")
