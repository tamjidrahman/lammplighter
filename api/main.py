import os
from datetime import datetime
from multiprocessing import Process
from typing import List

import boto3
from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse

s3_client = boto3.client("s3")


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
async def get_outputs(run_id: str, file_type: str = "log"):
    return {
        s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": "lammplighter",
                "Key": f"outputs/{run_id}/{run_id}.{file_type}",
            },
            ExpiresIn=60,
        )
    }


@app.post("/resources/inputs/")
def post_input(files: List[UploadFile]):
    filenames = [file.filename for file in files]
    for file in files:
        s3_client.upload_fileobj(
            file.file, "lammplighter", f"resources/inputs/{file.filename}"
        )
    return {f"Uploaded: {filenames}"}


def lamp_run(input_filename, run_id):
    lmp = lammps.lammps()

    output_dir = f"outputs/{run_id}"
    os.mkdir(output_dir)

    log_filename = f"{output_dir}/{run_id}.log"
    lmp.command(f"log {log_filename}")
    lmp.command(f"dump 1 all atom 10 {output_dir}/{run_id}.atom.dump")

    lmp.file(f"api/resources/inputs/{input_filename}")

    for filename in os.listdir(output_dir):
        with open(f"{output_dir}/{filename}", "rb") as log_file:
            s3_client.upload_fileobj(
                log_file, "lammplighter", f"{output_dir}/{filename}"
            )


@app.post("/execute")
async def run(input_filename: str):
    s3_client.download_file(
        "lammplighter",
        f"resources/inputs/{input_filename}",
        f"api/resources/inputs/{input_filename}",
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    run_id = f"{input_filename}_{timestamp}"
    p = Process(target=lamp_run, args=(input_filename, run_id))
    p.start()

    return {f"Executing {run_id}"}
