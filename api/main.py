import json
from contextlib import asynccontextmanager
from datetime import datetime
from multiprocessing import Process
from typing import List, Optional

import boto3
from fastapi import Depends, FastAPI, Query, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from api.database.crud import create_inputconfig, get_input_by_name
from api.database.database import SessionLocal
from api.database.schemas import InputConfigCreate
from api.squeue import lammps, loop

s3_client = boto3.client("s3", region_name="us-east-2")
sqs = boto3.client("sqs", region_name="us-east-2")
QUEUE_URL = (
    "https://sqs.us-east-2.amazonaws.com/217089594100/lammplighterQueue"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run asynchronous lammp process
    queue_process = Process(target=loop)
    queue_process.start()
    yield
    # Close asynchronous lammp process
    queue_process.terminate()


app = FastAPI(lifespan=lifespan)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
async def get_outputs(run_id: str, file_type: Optional[str] = None):
    files = s3_client.list_objects_v2(
        Bucket="lammplighter", Prefix=f"outputs/{run_id}/"
    ).get("Contents")

    filenames = (
        [file.get("Key").split("/")[-1] for file in files] if files else []
    )

    if not file_type:
        return {"outputs/": filenames}

    if f"{run_id}.{file_type}" in filenames:
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
    return {"No such file"}


@app.post("/resources/inputs/")
def post_input(files: List[UploadFile], db: Session = Depends(get_db)):
    filenames = [file.filename for file in files]
    for file in files:
        if get_input_by_name(db, file.filename):
            return {f"Input {file.filename} already exists"}

        s3_path = f"resources/inputs/{file.filename}"
        input_config_create_model = InputConfigCreate(
            name=file.filename, s3_path=s3_path
        )
        create_inputconfig(db, input_config_create_model)
        s3_client.upload_fileobj(
            file.file, "lammplighter", f"resources/inputs/{file.filename}"
        )

    return {f"Uploaded: {filenames}"}


@app.post("/execute")
async def run(input_filename: str, dump_commands: List[str] = Query(None)):
    # s3_client.download_file(
    #     "lammplighter",
    #     f"resources/inputs/{input_filename}",
    #     f"api/resources/inputs/{input_filename}",
    # )
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    run_id = f"{input_filename}_{timestamp}"

    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        DelaySeconds=10,
        MessageAttributes={
            "FileName": {
                "DataType": "String",
                "StringValue": f"{input_filename}",
            },
            "RunID": {"DataType": "String", "StringValue": f"{run_id}"},
        },
        MessageBody=(json.dumps(dump_commands)),
    )
    return response["MessageId"]
