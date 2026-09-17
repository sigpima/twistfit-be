from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class RegisterRequest(CamelModel):
    name: str
    identifier: str
    password: str


class LoginRequest(CamelModel):
    identifier: str
    password: str


class UserResponse(CamelModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    role: str


class AccountResponse(CamelModel):
    name: str
    email: str | None
    phone: str | None
    role: str


class UpdateProfileRequest(CamelModel):
    name: str
    phone: str | None = None


class ChangePasswordRequest(CamelModel):
    current_password: str
    new_password: str
