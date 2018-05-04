import matplotlib
matplotlib.use('agg')

from code.events import parallel_get_event_times
from code.waveforms import parallel_write_waveforms
from obspy.core.event import Catalog
from code.helpers import *
from code.async_client import AsyncClient
import warnings
import argparse
from obspy import UTCDateTime

class NotEnoughEvents(Exception):
    pass

def get_parser():
    parser = argparse.ArgumentParser(description='Get configuration.')
    parser.add_argument('--station',
                        dest='station',
                        type=str,
                        required=True,
                        help='station code')

    parser.add_argument('--network',
                        dest='network',
                        type=str,
                        required=True,
                        help='network code')

    parser.add_argument('--starttime',
                        dest='starttime',
                        type=str,
                        help='start time')

    parser.add_argument('--endttime',
                        dest='endtime',
                        type=str,
                        help='end time')

    parser.add_argument('--duration',
                        dest='duration',
                        type=int,
                        default=20,
                        help='duration')

    return parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    NETWORK = args.network
    STATION = args.station

    NUM_EVENTS = 6000
    NUM_NOISE_EVENTS = 8000
    MAX_RADIUS = 2
    DURATION = args.duration
    PRE_PADDING = 6
    POST_PADDING = 14
    ADD_TIME = 0
    MIN_EVENTS = 500
    MIN_MAGNITUDE = 1

    print("Starting Download Script...")
    # Types
    inventory: Inventory
    network: Network
    station: Station
    local_catalog: Catalog
    noise_catalog: Catalog
    local_times: List[UTCDateTime]
    nonlocal_times: List[UTCDateTime]
    noise_times: List[UTCDateTime]

    # Code
    client = AsyncClient(CLIENT_NAME)
    inventory = client.get_stations(network=NETWORK,
                                    station=STATION)
    network = inventory.select(NETWORK)[0]
    station = network.select(STATION)[0]

    WAVEFORMS_PATH = os.path.join(os.getcwd(), f"waveforms/{station.latitude}-{station.longitude}-minmag{MIN_MAGNITUDE}")

    STARTTIME = args.starttime or station.start_date
    ENDTIME = args.endtime or min(station.end_date, UTCDateTime(year=2018, month=3, day=1))

    # Verifies that the selected station supports 'get_waveforms' - saves time to not run the rest of the code
    def validate_and_adjust_starttime(tries):
        global STARTTIME
        for i in range(tries):
            try:
                return verify_fsdn(network, station, STARTTIME)
            except Exception:
                STARTTIME += Day(180)
                
        raise Exception("Couldn't download from server.")
    
    attempts = 30
    validate_and_adjust_starttime(attempts)
   
    NOISE_START = STARTTIME
    NOISE_END = STARTTIME + Day(60)

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
                                      endtime=ENDTIME,
                                      minmagnitude=MIN_MAGNITUDE
                                      )

    if len(local_catalog) < MIN_EVENTS:
        raise NotEnoughEvents(f"{len(local_catalog)} is < min_events {MIN_EVENTS}")

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
