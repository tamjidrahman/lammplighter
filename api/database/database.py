import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(".env.local")

DB_ENGINE = os.environ.get("DB_ENGINE")
DB_USER = os.environ.get("DB_USER")
DB_HOSTNAME = os.environ.get("DB_HOSTNAME")
DB_DATABASE = os.environ.get("DB_DATABASE")

DB_URL = f"{DB_ENGINE}://{DB_USER}@{DB_HOSTNAME}/{DB_DATABASE}"


engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
