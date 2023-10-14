from fastapi import FastAPI
import lammps

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/lammps")
async def lammps_root():
    return {"lammps_version": f"{lammps.__version__}"}
