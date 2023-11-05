import json
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
DB_ENGINE = os.environ.get("DB_ENGINE", "")
DB_USER = os.environ.get("DB_USER")
DB_HOSTNAME = os.environ.get("DB_HOSTNAME")
DB_PASSWORD = ""
DB_DATABASE = os.environ.get("DB_DATABASE")
DB_PORT = os.environ.get("DB_PORT")
DB_SECRET_NAME = os.environ.get("DB_SECRET_NAME")
DB_SECRET_REGION = os.environ.get("DB_SECRET_REGION")


def get_aws_db_secret():
    secret_name = DB_SECRET_NAME
    region_name = DB_SECRET_REGION

    # Create a Secrets Manager client
    session = boto3.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response["SecretString"]
    return secret


if DB_SECRET_NAME:
    secret = json.loads(get_aws_db_secret())
    DB_ENGINE = secret["engine"]
    DB_USER = secret["username"]
    DB_HOSTNAME = secret["host"]
    DB_PASSWORD = secret["password"]
    DB_PORT = secret["port"]

url_object = URL.create(
    drivername="postgresql" if DB_ENGINE == "postgres" else DB_ENGINE,
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOSTNAME,
    database=DB_DATABASE,
)


engine = create_engine(url_object)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
