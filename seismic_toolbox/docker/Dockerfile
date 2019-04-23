

FROM continuumio/anaconda3:latest

RUN conda config --add channels conda-forge

RUN apt-get update && apt-get upgrade -y

RUN conda install -c conda-forge obspy==1.1.1 -y

# Need for matplotlib to work in Docker
RUN apt-get -y install libgl1-mesa-glx

# Install GCC
RUN apt-get install build-essential -y

# Install GEOS requirements
RUN apt-get install binutils libproj-dev gdal-bin -y

# Install ImageMagick
RUN apt-get install gcc -y
RUN apt-get install imagemagick -y

# Fix for basemap when running anaconda as base: https://github.com/conda-forge/basemap-feedstock/issues/30
ENV PROJ_LIB /opt/conda/share/proj

WORKDIR /data

COPY . .

