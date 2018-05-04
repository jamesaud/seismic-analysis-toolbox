
# Steps to using the toolbox

Most of the code doing the heavy lifting lives in the 'code' module:

https://github.com/jamesaud/seismic-analysis-toolbox/tree/master/seismic-toolbox/code

## Pipeline

This package was made to help process a lot more data than obspy is built for.

There are usually 2 steps:

1. Download data from servers (shown here) https://github.com/jamesaud/seismic-analysis-toolbox/blob/master/seismic-toolbox/interactive_downloader.ipynb

2. Process and filter data (as shown here) https://github.com/jamesaud/seismic-analysis-toolbox/blob/master/seismic-toolbox/interactive_writer.ipynb


## Advanced Pipeline

The biggest problem in the code is MatPlotLib is horribly ineffective at producting large numbers of figures, and saving as images. There is some sort of memory leak (at least on my system), which takes up too much RAM.

The solution to this problem, and to several others, is to run in parallel with Docker containers.

Essentially, the previous 2 steps are parallelized with Docker:

1. Download data from servers https://github.com/jamesaud/seismic-analysis-toolbox/blob/master/seismic-toolbox/ultimate_downloader.py

2. Write spectrograms  https://github.com/jamesaud/seismic-analysis-toolbox/blob/master/seismic-toolbox/ultimate_writer.py


## Build the Images
> docker-compose build

Two images will be built:

1. seismictoolbox-waveform, for downloading and processing waveforms
2. seismictoolbox-spectro, for writing and processing spectrograms 

On your host machine, also use Anaconda with Python 3.6 and install requirements.txt (for TermColor, which isn't really needed).

Then run:

```
python ultimate_downloader.py
python ultimate_writer.py
```

## Tests

A few relevant tests are here:

https://github.com/jamesaud/seismic-analysis-toolbox/tree/master/seismic-toolbox/code/tests



## Notes

This code was specifically created to built a dataset for my neural network. Some settings may need to be tweaked (inside of config.py) for your situation.

At first this code was written as one big Jupyter file, and then I reformatted it (much nicer now). Howver, in config.py there are still artifacts leftover that need to be cleaned up. More tests need to be written as well.
