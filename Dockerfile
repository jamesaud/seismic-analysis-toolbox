

FROM continuumio/anaconda3

RUN conda config --add channels conda-forge

RUN conda install nb_conda -y && conda install obspy -y

RUN conda install jupyter -y --quiet 

RUN conda install -c conda-forge jupyter_contrib_nbextensions && jupyter contrib nbextension install --user 

RUN rm -rf /root/.local/share/jupyter/nbextensions  

RUN conda install pytorch torchvision cuda80 -c soumith

RUN pip install tensorflow

RUN apt-get update && apt-get upgrade -y



# TEST
# Pytorch
RUN apt-get update
RUN conda install pytorch torchvision cuda80 -c soumith
RUN apt-get -y install sox libsox-dev libsox-fmt-all        # Pytorch Audio
RUN pip install cffi

# Tensorboardx for Tensorflow visualization
RUN pip install tensorboardX

RUN apt-get -y install libgl1-mesa-glx   # Need for tensorboardx and matplotlib to work in Docker




# Install GCC
RUN apt-get install build-essential -y

# Install GEOS\
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

# Jupyterlab
RUN conda install -c conda-forge jupyterlab

EXPOSE 8888

WORKDIR /data

CMD jupyter lab --notebook-dir=/data --ip='*' --allow-root --port=8888 --no-browser
