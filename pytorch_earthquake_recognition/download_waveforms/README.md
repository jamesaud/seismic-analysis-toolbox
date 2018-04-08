1. docker build --tag download-data .

2. docker run --name download-waveforms -e PYTHONUNBUFFERED=0 -v $(pwd):/data download-data python main_download.py

3. docker run --name download-waveforms -e PYTHONUNBUFFERED=0 Location='Costa' -v $(pwd):/data download-data python main_write.py