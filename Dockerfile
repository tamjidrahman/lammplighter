# The python builder image, using poetry to build the virtual environment
FROM python:3.11-buster as builder

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim-buster as runtime

# Install dependencies for lammp
RUN apt-get update && apt-get -y install cmake protobuf-compiler && apt-get install -y wget && apt-get install -y build-essential
RUN wget "https://download.lammps.org/tars/lammps-stable.tar.gz"
RUN tar -xvzf lammps-stable.tar.gz
RUN mkdir lammps-2Aug2023/build
WORKDIR lammps-2Aug2023/build

# cmake lammp
RUN cmake ../cmake -D BUILD_SHARED_LIBS=yes
RUN cmake --build .

# load python builder venv
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# cmake lammp python wrapper
RUN make install-python

# load into app directory
WORKDIR /app

# line below to copy api, but it should be mounted as a volume too for hot reloading
ADD api ./api
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]



