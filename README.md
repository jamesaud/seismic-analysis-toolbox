# Seismic Toolbox

This is a toolbox for doing large scale data processing on seismic waveforms. 

It is also a showcase of some of the work that I have done.

## Getting Started

Run the following commands to build and run the Jupyter Notebook Docker image:

```
docker-compose build

docker-compose up
```

Great! Now on localhost:8000, you'll have a Jupyter Notebook running with all of the required packages. 

(TODO: Specify versions of packages and put them in .sh & requirements.txt)

## Basic Waveform Data Processing Example with Obspy

This is some basic algorithms implemented on Obspy to analyze our data with conventional techniques like STA/LTA and Template Matching:

https://github.com/jamesaud/seismic-analysis-toolbox/blob/master/notebooks/notebooks-practice/Earthquakes%20in%20Tanzania.ipynb


##### Note - this code was specifically created to built a dataset for my neural network. Some settings may need to be tweaked (inside of config.py) for your situation.
