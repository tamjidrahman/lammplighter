from pydantic import BaseModel


class RunBase(BaseModel):
    commands: str
    status: str


class RunCreate(RunBase):
    pass


class Run(RunBase):
    id: int
    inputconfig_id: int

    class Config:
        orm_mode = True


class InputConfigBase(BaseModel):
    name: str
    s3_path: str


class InputConfigCreate(InputConfigBase):
    pass


class InputConfig(InputConfigBase):
    id: int
    runs: list[Run] = []

    class Config:
        orm_mode = True
