import os

import boto3
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_ENGINE = os.environ.get("DB_ENGINE")
DB_USER = os.environ.get("DB_USER")
DB_HOSTNAME = os.environ.get("DB_HOSTNAME")
DB_DATABASE = os.environ.get("DB_DATABASE")
DB_PORT = os.environ.get("DB_PORT")

if "rds" in DB_HOSTNAME:
    session = boto3.Session()
    client = session.client("rds")
    password = client.generate_db_auth_token(
        DBHostname=DB_HOSTNAME,
        Port=DB_PORT,
        DBUsername=DB_USER,
        Region="us-east-2",
    )
else:
    password = ""

url_object = URL.create(
    DB_ENGINE,
    username=DB_USER,
    password=password,
    host=DB_HOSTNAME,
    database=DB_DATABASE,
)


engine = create_engine(url_object)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
