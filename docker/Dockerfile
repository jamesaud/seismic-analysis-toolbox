

FROM seismictoolbox_toolbox

RUN conda install jupyter -y --quiet 

RUN conda install -c conda-forge jupyter_contrib_nbextensions && jupyter contrib nbextension install --user 

RUN rm -rf /root/.local/share/jupyter/nbextensions  

RUN apt-get update && apt-get upgrade -y

# Jupyterlab
RUN conda install -c conda-forge jupyterlab

# Install Docker inside of Docker!!
RUN  apt-get update && \
     apt-get -y install apt-transport-https \
     ca-certificates \
     curl \
     gnupg2 \
     software-properties-common && \
     curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg > /tmp/dkey; apt-key add /tmp/dkey && \
     add-apt-repository \
     "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
     $(lsb_release -cs) \
     stable" && \
     apt-get update && \
     apt-get -y install docker-ce

RUN pip install --user nodejs

RUN conda install -c conda-forge tqdm==4.31.1

EXPOSE 8888

WORKDIR /data

# Fix basemap env variable issue
CMD jupyter lab --notebook-dir=/data --ip='0.0.0.0' --allow-root --port=8888 --no-browser --NotebookApp.token=''
