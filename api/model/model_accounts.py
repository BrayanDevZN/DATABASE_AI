from pydantic import BaseModel, ConfigDict


class ValidEmail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str


class CreateUser(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str
    name: str
    age: int
    gender: str
    code: int


class Login(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str


class Env_CodePass(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str | None = None
    email: str | None = None


class UpdateAuthPass(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: int
    token: str | None = None
    email:str | None = None
    password: str


class Pass(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    password: str


class UpName(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    name: str

class ValidToken(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str
