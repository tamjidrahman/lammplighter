# Installation

This repo uses poetry, but the lammps build is a custom build (see Dockerfile)

# Getting started

## Development
Build lammps and fastAPI image on top in a local docker container. 

API code is mounted as a volume for fast reloading. The first build may take a few minutes.

```
docker build -t lammplighter . && docker run -d -t -p 80:80 -v $(pwd)/api:/app/api lammplighter
``````