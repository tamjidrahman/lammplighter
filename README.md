# Lammplighter

Many computational tools lack containerization, despite the fact that consistent results require consistent deployment configurations.
Lammplighter offers deployment configuration, state initialization, and runtime configuration all in one UI.

The end-goal is to be a one-stop shop for auditing and recreating computational experiments
<img width="1222" alt="Screenshot 2023-12-18 at 1 00 27 PM" src="https://github.com/tamjidrahman/lammplighter/assets/134972426/d40064a5-60fe-4f5e-a638-81547e9551a6">

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

Run UI
```
docker build -t lammplighter_ui -f Dockerfile.ui . && docker run -d -t -p 3000:3000 -v $(pwd)/ui/src:/react-app/src lammplighter_ui
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
