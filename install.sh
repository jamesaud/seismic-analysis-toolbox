# Build the toolbox images
cd seismic_toolbox
docker-compose build
cd ..

# Build the jupyter notebook image
docker-compose build

# Build the parallel converter
cd parallel
docker-compose build
cd ..