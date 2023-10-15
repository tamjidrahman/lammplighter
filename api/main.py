import io
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
import boto3
from fastapi.responses import FileResponse, HTMLResponse

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
    files = s3_client.list_objects_v2(
        Bucket="lammplighter", Prefix="resources/inputs/"
    ).get("Contents")

    filenames = None
    if files:
        filenames = [file.get("Key").split("/")[-1] for file in files]
    return {"resources/inputs/": filenames}


@app.get("/outputs")
async def get_outputs(filename: str):
    with open(f"outputs_{filename}", "w+b") as f:
        s3_client.download_fileobj("lammplighter", f"outputs/{filename}", f)

    return FileResponse(
        f"outputs_{filename}",
        media_type="application/octet-stream",
        filename=f"outputs_{filename}",
    )


@app.post("/resources/inputs/")
def post_input(files: List[UploadFile]):
    filenames = [file.filename for file in files]
    for file in files:
        s3_client.upload_fileobj(
            file.file, "lammplighter", f"resources/inputs/{file.filename}"
        )
    return {f"Uploaded: {filenames}"}


@app.post("/execute")
def run(input_filename: str):
    lmp = lammps.lammps()

    s3_client.download_file(
        "lammplighter",
        f"resources/inputs/{input_filename}",
        f"api/resources/inputs/{input_filename}",
    )

    lmp.file(f"api/resources/inputs/{input_filename}")
    with open("log.lammps", "rb") as log_file:
        s3_client.upload_fileobj(log_file, "lammplighter", f"outputs/{input_filename}")
    return {f"Executed {input_filename}"}
