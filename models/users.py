from pydantic import BaseModel


class UserLoginModel(BaseModel):
    username: str
    password: str


class UserCreateModel(UserLoginModel):
    email: str


class PermissionModel(BaseModel):
    user_id: int
    note_id: int

