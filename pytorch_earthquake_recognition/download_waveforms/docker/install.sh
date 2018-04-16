conda config --add channels conda-forge
conda install nb_conda -y && conda install obspy -y
conda install pytorch torchvision cuda80 -c soumith
apt-get update && apt-get upgrade -y
pip install tensorboardX
