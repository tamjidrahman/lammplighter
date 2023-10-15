from fastapi import FastAPI
from unittest.mock import MagicMock

import os

if os.getenv("LAMMPS_INSTALLED") != "0":
    import lammps
else:
    import api.test.lammps_mock as lammps

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"lammps_version": f"{lammps.__version__}"}
