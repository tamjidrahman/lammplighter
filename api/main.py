from contextlib import asynccontextmanager
from multiprocessing import Process
from typing import List, Optional

import boto3
from fastapi import Depends, FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.database.crud import create_inputconfig, get_input_by_name
from api.database.crud import get_inputs as db_get_inputs
from api.database.crud import get_runs as db_get_runs
from api.database.database import SessionLocal
from api.database.schemas import (
    HealthCheckResponse,
    InputConfigCreate,
    JoinedRuns,
    RunCreate,
)
from api.squeue import __lammps_version__, loop

s3_client = boto3.client("s3", region_name="us-east-2")
sqs = boto3.client("sqs", region_name="us-east-2")
QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/217089594100/lammplighterQueue"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run asynchronous lammp process
    queue_process = Process(target=loop)
    queue_process.start()
    yield
    # Close asynchronous lammp process
    queue_process.terminate()


app = FastAPI(lifespan=lifespan)

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/healthcheck")
async def healthcheck(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1")).first()
    return HealthCheckResponse(lammps_version=__lammps_version__)


@app.get("/")
async def main():
    files = s3_client.list_objects_v2(
        Bucket="lammplighter", Prefix="resources/inputs/"
    ).get("Contents")

    filenames = [file.get("Key").split("/")[-1] for file in files]

    input_configs_html = f"""
    <ul>
    {''.join([f"<li>{filename}</li>" for filename in filenames if filename])}
    </ul>
    """

    content = """
    <body>
    <form
        action="/resources/inputs/"
        enctype="multipart/form-data"
        method="post"
    >
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content="<h1>Hi Laura <3 </h1>" + input_configs_html + content)


@app.get("/resources/inputs/")
async def get_inputs(db: Session = Depends(get_db)):
    return db_get_inputs(db)


@app.get("/outputs")
async def get_outputs(run_id: str, file_type: Optional[str] = None):
    files = s3_client.list_objects_v2(
        Bucket="lammplighter", Prefix=f"outputs/{run_id}/"
    ).get("Contents")

    filenames = [file.get("Key").split("/")[-1] for file in files] if files else []

    if not file_type:
        return {
            s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": "lammplighter",
                    "Key": f"outputs/{run_id}/{run_id}.zip",
                },
                ExpiresIn=60,
            )
        }

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


@app.get("/runs")
async def get_runs(db: Session = Depends(get_db)):
    return [JoinedRuns(run=jr[0], inputconfig=jr[1]) for jr in db_get_runs(db)]


@app.post("/resources/inputs/")
def post_input(files: List[UploadFile], db: Session = Depends(get_db)):
    filenames = [file.filename for file in files]
    for file in files:
        if file.filename is None:
            continue
        if get_input_by_name(db, file.filename):
            return {f"Input {file.filename} already exists"}

        db_inputconfig = create_inputconfig(db, InputConfigCreate(name=file.filename))

        s3_client.upload_fileobj(
            file.file, "lammplighter", f"resources/inputs/{db_inputconfig.id}"
        )

    return {f"Uploaded: {filenames}"}


@app.post("/execute")
async def run(run: RunCreate):
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        DelaySeconds=10,
        MessageBody=(run.model_dump_json()),
    )
    return "OK"
