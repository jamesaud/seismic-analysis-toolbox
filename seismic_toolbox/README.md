
# Steps to using the toolbox

Most of the code doing the heavy lifting lives in the 'code' module:

https://github.com/jamesaud/seismic-analysis-toolbox/tree/master/seismic_toolbox/code

## Pipeline

This package was made to help process a lot more data than obspy is built for.

There are usually 2 steps:

1. Download data from servers (shown here) https://github.com/jamesaud/seismic-analysis-toolbox/blob/master/seismic_toolbox/interactive_downloader.ipynb

2. Process and filter data (as shown here) https://github.com/jamesaud/seismic-analysis-toolbox/blob/master/seismic_toolbox/interactive_writer.ipynb


## Advanced Pipeline

The biggest problem in the code is MatPlotLib is horribly ineffective at producting large numbers of figures, and saving as images. There is some sort of memory leak (at least on my system), which takes up too much RAM.

The solution to this problem, and to several others, is to run in parallel with Docker containers.

Essentially, the previous 2 steps are parallelized with Docker (quick and dirty, going to use the Docker-Python API library when I update these files):

1. Download data from servers https://github.com/jamesaud/seismic-analysis-toolbox/blob/master/seismic_toolbox/ultimate_downloader.py

2. Write spectrograms  https://github.com/jamesaud/seismic-analysis-toolbox/blob/master/seismic_toolbox/ultimate_writer.py


## Build the Images
> docker-compose build

One image will be built: 

`seismictoolbox-toolbox`

On your host machine, use Anaconda to install requirements.txt in a separate environment:

```
conda create --name download_waveforms --file requirements.txt python=3.7

conda activate download_waveforms
```

Then run:

```
python ultimate_downloader.py
```

If you want to convert waveforms into spectrograms, use:

```
python ultimate_writer.py
```

## Tests

A few relevant tests are here:

https://github.com/jamesaud/seismic-analysis-toolbox/tree/master/seismic_toolbox/code/tests


## Notes

This code was specifically created to built a dataset for my neural network. Some settings will need to be tweaked for your situation.
