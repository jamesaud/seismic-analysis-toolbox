import pandas as pd
import os
pj = os.path.join
from utils import *
import numpy as np


def dataframe_from_csv(csv_path, spectrogram_path):
    """ 
    Returns a dataframe representing the events/noise data in a csv 
    CSV headers should be: 'Name', 'Guess', 'True Label'
    """
    
    df = pd.read_csv(csv_path)
    
    def make_path(path, name):
        clas = "/".join(name.split('/')[-2:])
        return pj(path, clas)
    
    df = df.drop_duplicates()
    df['Filepath'] = df['Name'].map(lambda name: make_path(spectrogram_path, name))
    df['Name'] = df['Name'].map(lambda name: name.split('/')[-1])
    return df


def make_labels(df):
    predicted_times = df
    predicted_times = predicted_times.assign(Label=np.zeros(len(predicted_times))) # New Column of Zeroes
    
    true_positives_i = (predicted_times['Guess'] == 1) & (predicted_times['True Label'] == 1)
    true_negatives_i = (predicted_times['Guess'] == 0) & (predicted_times['True Label'] == 0)
    false_positives_i = (predicted_times['Guess'] == 1) & (predicted_times['True Label'] == 0)
    false_negatives_i = (predicted_times['Guess'] == 0) & (predicted_times['True Label'] == 1)

    predicted_times['Label'][true_positives_i] = 'True Positive'
    predicted_times['Label'][true_negatives_i] = 'True Negative'
    predicted_times['Label'][false_positives_i] = 'False Positive'
    predicted_times['Label'][false_negatives_i] = 'False Negative'
    
    return predicted_times



def df_confusion_matrix(df):
    predicted_times = df
    fp = predicted_times[ predicted_times['Label'] == 'False Positive' ]
    fn = predicted_times[ predicted_times['Label'] == 'False Negative' ]
    tp = predicted_times[ predicted_times['Label'] == 'True Positive' ]
    tn = predicted_times[ predicted_times['Label'] == 'True Negative' ]
    return fp, fn, tp, tn