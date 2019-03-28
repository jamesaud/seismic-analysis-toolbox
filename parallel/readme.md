# Parallel Covnerter

This script converts continuous waveform data to spectrograms in parallel.

Steps to run:

1. Run `docker-compose build`
2. Open the `convert_waveforms_parallel.py` file and specify globals variables at the top. 
3. Then run the script `python convert_waveforms_parallel.py'

The 'parallelize.py' file does the 'heavy lifting' of working with the docker api to make sure a certain amount of containers are running concurrently to convert the waveforms.  

