from collections import namedtuple
from datetime import datetime
from obspy import UTCDateTime
import pandas as pd

Timerange = namedtuple('timerange', ['start', 'end'])

def within(time, timerange: Timerange):
    return timerange.start <= time <= timerange.end


def time_within(time, start, end):
    return start <= time <= end
    
    
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


def catalog_df(catalog_path, start=None, end=None):
    """
    Date formats given as a string
    start: '07/01/2014'
    end: '07/31/2014'
    """
    df = pd.read_csv(catalog_path)
    
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
    df = df.rename(index=str, columns={"Name": "Time"})
    df = df.drop_duplicates().sort_values(by=['Time'])
    df["event_start"], df["event_end"] = zip(*df['Time'].map(to_timerange))
    return df


def event_in_catalog(time_range, catalog_times):
    df = catalog_times
    """ Returns the index found in the dataframe, or -1 if not """
    # Find where the time would be in the catalog
    i = df['origintime'].searchsorted(time_range.start)[0]
    
    # Search nearby indexes, just to be safe
    # Don't search out of bounds for index error
    indexes = list(range(
        max(i - 10, 0), 
        min(i + 10, len(df)-1)
    ))
        
    idx_found = []
    for i, row in df.iloc[indexes,:].iterrows():
        if within(row['origintime'], time_range):
            idx_found.append(i)
            
    return idx_found or -1
            
    
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
    