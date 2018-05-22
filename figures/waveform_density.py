import matplotlib as mpl
#mpl.use('TkAgg')
import glob
from obspy import read
from os.path import join as pj
from os.path import basename
from helpers import *
import pandas as pd
from collections import namedtuple
import os
from multiprocessing import Pool
from matplotlib import pyplot as plt
import datetime
from itertools import islice


InfoTimes = namedtuple('InfoTimes', ('info', 'times'))


def mseed_paths(waveform_path):
    return glob.glob(pj(waveform_path, 'local/*.mseed'))


def get_time(waveform_path):
    waveform = read(waveform_path)
    return waveform[0].stats.starttime


def parallel_times(path):
    mseeds = mseed_paths(path)
    with Pool() as p:
        time_list = p.map(get_time, mseeds)
    return time_list


def dataframe(wave_times):
    df = pd.DataFrame({'time': wave_times})
    df["time"] = df["time"].astype("datetime64[ns]")
    return df


def minmag(name):
    return 'minmag' in name


def remove_minmag(name):
    return name.split('-minmag1')[0]


def fix_name(name):
    return remove_minmag(name) if minmag(name) else name


def clean(information):
    int_cols = ['Amount Correct Noise', 'Amount Total Noise', 'Amount Correct Local', 'Amount Total Local']
    cols = ['Name', 'Amount Correct Noise', 'Amount Total Noise', 'Amount Correct Local', 'Amount Total Local',
            'Total Percent Correct']
    information = information[cols]
    information = information.round({'Total Percent Correct': 4})

    for col in int_cols:
        information[col] = information[col].astype('int32')

    information['Name'] = information['Name'].apply(fix_name)
    information.drop_duplicates('Name', inplace=True)
    return information


def Info(name):
    df = information.loc[information['Name'] == name]
    return df  # Panda Series


def info_times(paths):
    for path in paths:
        name = os.path.basename(path)
        time = parallel_times(path)
        time = dataframe(time)
        info = Info(name)
        yield InfoTimes(info, time)


def valid_paths(paths, keep_paths):
    keep = map(basename, keep_paths)
    keep = set(keep)
    return [path for path in paths if basename(path) in keep]


def get_waveform_paths(path):
    waveform_paths = glob.glob(pj(waveforms_path, '*'))
    waveform_paths = valid_paths(waveform_paths, information['Name'])
    waveform_paths = list(set(map(fix_name, waveform_paths)))
    return waveform_paths


def plot_time_freq(df, by='week', xlabels='number', axis_on=True, title=False, **kwargs):
    """
    by: 'week' or 'day' or 'month'
    labels: 'number' or 'date'
    kwargs: passed to dataframe.plot()
    """
    if title:
        kwargs['title'] = f'Event Frequency Per {by.title()}'

    if by == 'month':
        frame = df.groupby([df["time"].dt.year, df["time"].dt.month]).count()

    elif by == 'week':
        frame = df.groupby([df["time"].dt.year, df["time"].dt.month, df["time"].dt.week]).count()

    elif by == 'day':
        frame = df.groupby([df["time"].dt.year, df["time"].dt.month, df["time"].dt.day]).count()

    frame = frame.plot(legend=False, **kwargs)
    frame.xaxis.label.set_visible(False)

    def labeltimes(num_parts):
        start, end = df.min()[0].to_pydatetime(), df.max()[0].to_pydatetime()
        part = (end - start) / num_parts
        parts = [start + (part * i) for i in range(num_parts)]
        return [dt.strftime('%D') for dt in parts]

    def labelnums(num):
        nums = list(range(1, num + 1))
        return nums

    def set_xlabels(label_type):
        label_len = len([item.get_text() for item in frame.get_xticklabels()])

        if label_type == 'number':
            labels = labelnums(label_len)

        elif label_type == 'date':
            labels = labeltimes(label_len)

        elif label_type == 'none':
            labels = [' '] * label_len

        frame.set_xticklabels(labels)

    if xlabels:
        set_xlabels(xlabels)

    if not axis_on:
        plt.axis('off')

    return frame


csv = '/home/audretj/developer-projects/waveforms/notebooks/combine-csv/results-complete.csv'
information = pd.read_csv(csv, index_col=0)

information = clean(information)
waveforms_path = '/home/audretj/developer-projects/waveforms/seismic_toolbox/waveforms'
waveform_paths = get_waveform_paths(waveforms_path)

def plot_info_table(info, position='top', scale=(1, 1), collabels=True):
    dc = info
    table = plt.table(cellText=dc.values,
                      colWidths=[1 / len(dc.columns)] * len(dc.columns),
                      colLabels=dc.columns.values if collabels else None,
                      cellLoc='center', rowLoc='center',
                      loc=position)

    table.auto_set_font_size(False)
    # table.set_fontsize(10)
    table.scale(*scale)  # may help


if __name__ == '__main__':


    infotimes = info_times(waveform_paths[:3])


    for i, (info, times) in enumerate(infotimes, 1):
        frame = plot_time_freq(times, by='week', figsize=(8, 3), kind='bar', axis_on=False)
        #giplot_info_table(info, collabels=False, position='left')
        plt.plot()
        plt.pause(.001)

    plt.show()

