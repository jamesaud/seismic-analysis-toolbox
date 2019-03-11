from collections import namedtuple
from datetime import datetime
from obspy import UTCDateTime
import pandas as pd

CATALOG_PATH = 'Benz_catalog.csv'
Timerange = namedtuple('timerange', ['start', 'end'])

def within(time, timerange: Timerange):
    return timerange.start <= time <= timerange.end
    
def to_timerange(predicted_time):
    start, end = predicted_time.split('--')
    return Timerange(UTCDateTime(start), UTCDateTime(end))
    
def make_buckets(df):
    predicted_times = df
    buckets = {0: [], 1: []}
    for i, row in predicted_times.iterrows():
        time_range = to_timerange(row['Time'])
        buckets[row['Guess']].append(time_range) 
    return buckets

def catalog_df(start=None, end=None):
    """
    Date formats given as a string
    start: '07/01/2014'
    end: '07/31/2014'
    """
    df = pd.read_csv('Benz_catalog.csv')
    
    if start is None:
        start = df.iloc[0]['Date']
    if end is None:
        end = df.iloc[-1]['Date']

    df = df[df['Date'].between(start, end, inclusive=True)]
    df['origintime'] = df['origintime'].map(lambda time: UTCDateTime(time))
    df = df.drop('Unnamed: 0', axis=1)
    return df
    
    
# Working with a different type of dataframe here
def predicted_df(path):
    df = pd.read_csv(path)
    df = df.drop_duplicates().sort_values(by=['Time'])
    df["event_start"], df["event_end"] = zip(*df['Time'].map(to_timerange))
    return df


from IPython.display import clear_output

def event_in_catalog(time_range, catalog_times):
    df = catalog_times
    """ Returns the index found in the dataframe, or -1 if not """
    # Find where the time would be in the catalog
    i = df['origintime'].searchsorted(time_range.start)[0]
    
    # Don't search out of bounds for index error
    indexes = list(range(
        max(i - 1, 0), 
        min(i + 1, len(df)-1)
    ))
        
    for i, row in df.iloc[indexes,:].iterrows():
        if within(row['origintime'], time_range):
            return i
    return - 1
            
def find_events_in_catalog(predicted_times, catalog_times):
    """ 
    :predicted_times_df: containing "event_start" and "event_end" as columns
    :catalog_df: dataframe dataframe containg "origintime" as a column 
    :return: indexes in the catalog of the events that were found
    """
    df = predicted_times
    df['timerange'] = df.apply(lambda row: Timerange(row.event_start, row.event_end), axis=1)
    df['catalog_id'] = df.apply(lambda row: event_in_catalog(row.timerange, catalog_times), axis=1)
    return df
    