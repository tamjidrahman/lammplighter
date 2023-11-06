import uuid
from typing import List

from pydantic import BaseModel, ConfigDict


class InputConfigBase(BaseModel):
    name: str


class InputConfigCreate(InputConfigBase):
    pass


class InputConfig(InputConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class RunBase(BaseModel):
    commands: List[str]


class RunCreate(RunBase):
    input_id: uuid.UUID
    pass


class Run(RunBase):
    model_config = ConfigDict(from_attributes=True)

    status: str
    id: uuid.UUID


class HealthCheckResponse(BaseModel):
    lammps_version: int


class JoinedRuns(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run: Run
    inputconfig: InputConfig
