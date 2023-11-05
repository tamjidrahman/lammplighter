from pydantic import BaseModel, ConfigDict


class RunBase(BaseModel):
    commands: str
    status: str


class RunCreate(RunBase):
    pass


class Run(RunBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inputconfig_id: int


class InputConfigBase(BaseModel):
    name: str
    s3_path: str


class InputConfigCreate(InputConfigBase):
    pass


class InputConfig(InputConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    runs: list[Run] = []
