

FROM continuumio/anaconda3:5.0.1

RUN conda config --add channels conda-forge

RUN apt-get update && apt-get upgrade -y

RUN apt-get update

RUN conda install nb_conda -y && conda install obspy -y

# Need for matplotlib to work in Docker
RUN apt-get -y install libgl1-mesa-glx

# Install GCC
RUN apt-get install build-essential -y

# Install GEOS
RUN apt-get install binutils libproj-dev gdal-bin -y

RUN wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2 \
    && tar xjf geos-3.4.2.tar.bz2

RUN cd geos-3.4.2 \
&& ./configure \
&& make \
&& make install \
&& cd ..


# Install Basemap
RUN pip install https://github.com/matplotlib/basemap/archive/v1.0.7rel.tar.gz

# Install ImageMagick
RUN apt-get install php5 php5-common gcc -y

RUN apt-get install imagemagick -y

WORKDIR /data

COPY . .