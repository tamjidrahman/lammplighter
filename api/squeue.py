import os
import time
from typing import List

import boto3
from sqlalchemy import UUID, Column

from api.database.crud import create_run, update_run_status
from api.database.database import SessionLocal
from api.database.schemas import RunCreate

QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/217089594100/lammplighterQueue"

sqs = boto3.client("sqs", region_name="us-east-2")
s3_client = boto3.client("s3", region_name="us-east-2")
db = SessionLocal()

if os.getenv("LAMMPS_INSTALLED") != "0":
    import lammps
else:
    import api.test.lammps_mock as lammps

__lammps_version__ = lammps.__version__


def receive_message() -> dict | None:
    """Pull message from SQS if possible, else return None"""

    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        AttributeNames=["All"],
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=0,
    )

    if "Messages" in response:
        message = response["Messages"][0]
        receipt_handle = message["ReceiptHandle"]

        # Delete received message from queue
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)

        return message
    return None


def lamp_run(input_filename: str, run_id: Column[UUID], dump_commands: List[str]):
    lmp = lammps.lammps()

    output_dir = f"outputs/{run_id}"
    os.makedirs(output_dir, exist_ok=True)

    log_filename = f"{output_dir}/{run_id}.log"
    lmp.command(f"log {log_filename}")
    for i, cmd in enumerate(dump_commands):
        lmp.command(f"dump {i} {cmd} {output_dir}/{run_id}.{i}.dump")

    lmp.file(f"api/resources/inputs/{input_filename}")

    for filename in os.listdir(output_dir):
        with open(f"{output_dir}/{filename}", "rb") as log_file:
            s3_client.upload_fileobj(
                log_file, "lammplighter", f"{output_dir}/{filename}"
            )


def read_and_execute():
    message: dict | None = None
    while not message:
        time.sleep(1)
        message = receive_message()

    run: RunCreate = RunCreate.model_validate_json(message["Body"])
    db_run = create_run(db, run)

    if not db_run:
        return

    os.makedirs("api/resources/inputs", exist_ok=True)
    s3_client.download_file(
        "lammplighter",
        f"resources/inputs/{run.inputconfig_name}",
        f"api/resources/inputs/{run.inputconfig_name}",
    )

    update_run_status(db, db_run.id, "IN PROGRESS")
    lamp_run(run.inputconfig_name, db_run.id, run.commands)
    update_run_status(db, db_run.id, "COMPLETE")


def loop():
    while True:
        read_and_execute()
