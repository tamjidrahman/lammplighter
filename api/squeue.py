import json
import logging
import os
import time
from datetime import datetime
from typing import List, Optional

import boto3

logging.basicConfig(
    filename="queue_log.log", encoding="utf-8", level=logging.DEBUG
)


QUEUE_URL = (
    "https://sqs.us-east-2.amazonaws.com/217089594100/lammplighterQueue"
)

sqs = boto3.client("sqs", region_name="us-east-2")
s3_client = boto3.client("s3", region_name="us-east-2")


if os.getenv("LAMMPS_INSTALLED") != "0":
    import lammps
else:
    import api.test.lammps_mock as lammps


def receive_message() -> Optional[str]:
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


def lamp_run(input_filename: str, run_id: str, dump_commands: List[str]):
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
    message = None
    while not message:
        time.sleep(1)
        message = receive_message()

    logging.info(f"found file {message}")

    body = message["Body"]

    input_filename = message["MessageAttributes"]["FileName"]["StringValue"]
    dump_commands = json.loads(body)

    os.makedirs("api/resources/inputs", exist_ok=True)
    s3_client.download_file(
        "lammplighter",
        f"resources/inputs/{input_filename}",
        f"api/resources/inputs/{input_filename}",
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    run_id = f"{input_filename}_{timestamp}"
    lamp_run(input_filename, run_id, dump_commands)

    return {f"Executing {run_id}"}


def loop():
    while True:
        read_and_execute()
