import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import declarative_base, relationship

from api.database.database import engine

Base = declarative_base()


class InputConfig(Base):
    __tablename__ = "inputconfigs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    s3_path = Column(String)
    runs = relationship("Run", back_populates="input")


class Run(Base):
    __tablename__ = "runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    input_id = Column(UUID, ForeignKey("inputconfigs.id"))
    commands = Column(JSON)
    status = Column(String)

    input = relationship("InputConfig", back_populates="runs")


Base.metadata.create_all(bind=engine)
