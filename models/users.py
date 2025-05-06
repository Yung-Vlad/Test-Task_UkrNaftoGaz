from pydantic import BaseModel
from enum import Enum


class UserLoginModel(BaseModel):
    username: str
    password: str


class UserCreateModel(UserLoginModel):
    email: str


class AccessModel(BaseModel):
    user_id: int
    note_id: int


class Permission(str, Enum):
    read = "read"
    read_and_write = "read and write"


class AccessInternalModel(AccessModel):
    permission: int
    key: str | bytes | None
