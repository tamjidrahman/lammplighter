from typing import List

from pydantic import BaseModel, ConfigDict


class RunBase(BaseModel):
    commands: str


class RunCreate(RunBase):
    inputconfig_name: str
    commands: List[str]
    pass


class Run(RunBase):
    model_config = ConfigDict(from_attributes=True)

    status: str
    inputconfig_id: int
    id: str


class InputConfigBase(BaseModel):
    name: str
    s3_path: str


class InputConfigCreate(InputConfigBase):
    pass


class InputConfig(InputConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    runs: list[Run] = []
