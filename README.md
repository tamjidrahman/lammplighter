# Installation

Recommended development within a docker container. Local installations will require a local lammps installation.

- Install poetry.
- Install lammps, with python package.
- If connecting to remote PostGres RDS, set up a $PGPASSFILE

## Run Docker Server
Build lammps and fastAPI image on top in a local docker container. 

API code is mounted as a volume for fast reloading. The first build may take a few minutes.

```
docker build -t lammplighter . && docker run -d -t -p 80:80 --env-file .env -v $PGPASSFILE:/root/.pgpass -v $(pwd)/api:/app/api -v ~/.aws:/root/.aws lammplighter
```

## Run Tests
Run
```pytest```

Note that pytest uses pytest.ini and .test.env

## Rebuilding LAMMP image
```
docker build -t lammp -f Dockerfile.lammp .
docker tag lammp:latest 217089594100.dkr.ecr.us-east-2.amazonaws.com/lammp:latest
docker push 217089594100.dkr.ecr.us-east-2.amazonaws.com/lammp:latest
```
