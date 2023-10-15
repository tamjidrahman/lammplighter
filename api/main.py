from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
import boto3
from fastapi.responses import HTMLResponse

s3_client = boto3.client("s3")

import os

if os.getenv("LAMMPS_INSTALLED") != "0":
    import lammps
else:
    import api.test.lammps_mock as lammps

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"lammps_version": f"{lammps.__version__}"}


@app.get("/")
async def main():
    content = """
<body>
<form action="/resources/inputs/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.get("/resources/inputs/")
async def get_inputs():
    return {"scripts": "calc_fcc.in", "potentials": "Al99.eam.alloy"}


@app.post("/resources/inputs/")
def post_input(files: List[UploadFile]):
    file = files[0]
    filename = file.filename
    s3_client.upload_fileobj(file.file, "lammplighter", f"inputs/{filename}")
    return {f"Uploaded: {filename}"}
