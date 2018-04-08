docker run --name download-waveforms -e PYTHONUNBUFFERED=0 -v $(pwd):/data download-data python main_download.py

docker run --name download-waveforms -e PYTHONUNBUFFERED=0 Location='Costa' -v $(pwd):/data download-data python main_write.py