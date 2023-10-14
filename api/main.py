from fastapi import FastAPI
import lammps

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"lammps_version": f"{lammps.__version__}"}
