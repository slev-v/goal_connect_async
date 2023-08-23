import re

from pydantic import BaseModel, Field, EmailStr, validator
from fastapi import HTTPException


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str


class TokenResponce(BaseModel):
    access_token: str
    token_type: str


class UserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @validator("password")
    def validate_password(cls, password) -> str:
        PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
        if not re.match(PASSWORD_PATTERN, password):
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least: eight symbols, one lower character, one upper character, one digit",
            )

        return password
