from pydantic import BaseModel, Field, ConfigDict


class WithToken(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)


class CreateDataSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    name: str = Field(min_length=1)


class UpdateDataSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    data_source_id: int = Field(gt=0)


class DeleteDataSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    data_source_id: int = Field(gt=0)


class GetDataSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    data_source_id: int = Field(gt=0)


class RenameDataSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    data_source_id: int = Field(gt=0)
    name: str = Field(min_length=1)