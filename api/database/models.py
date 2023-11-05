from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import declarative_base, relationship

from api.database.database import engine

Base = declarative_base()


class InputConfig(Base):
    __tablename__ = "inputconfigs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    s3_path = Column(String, unique=True)
    runs = relationship("Run", back_populates="input")


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    input_id = Column(Integer, ForeignKey("inputconfigs.id"))
    commands = Column(JSON)
    status = Column(String)

    input = relationship("InputConfig", back_populates="runs")


Base.metadata.create_all(bind=engine)
