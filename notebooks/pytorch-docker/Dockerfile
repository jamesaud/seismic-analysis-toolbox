FROM continuumio/anaconda3

# Jupyter Notebook
RUN conda config --add channels conda-forge

RUN conda install nb_conda -y && conda install obspy -y

RUN conda install jupyter -y --quiet 

RUN conda install -c conda-forge jupyter_contrib_nbextensions && jupyter contrib nbextension install --user 

RUN rm -rf /root/.local/share/jupyter/nbextensions  

# Pytorch
RUN apt-get update
RUN conda install pytorch torchvision cuda80 -c soumith
RUN apt-get -y install sox libsox-dev libsox-fmt-all        # Pytorch Audio
RUN pip install cffi

# Tensorboardx for Tensorflow visualization
RUN pip install tensorboardX

RUN apt-get -y install libgl1-mesa-glx   # Need for tensorboardx and matplotlib to work in Docker

EXPOSE 8888

WORKDIR /data

CMD jupyter notebook --notebook-dir=/data --ip='*' --allow-root --port=8888 --no-browser