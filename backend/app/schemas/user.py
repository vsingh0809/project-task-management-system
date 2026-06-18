import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]+$")


class UserCreate(BaseModel):
    """
    Schema for user registration.
    """

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip().lower()

        if not USERNAME_REGEX.fullmatch(value):
            raise ValueError(
                "Username may contain only letters, numbers, and underscores"
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one numeric digit")
        if not any(not c.isalnum() for c in value):
            raise ValueError("Password must contain at least one special character")

        return value


class UserLogin(BaseModel):
    """
    Schema for user login.
    """

    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.lower()


class UserResponse(BaseModel):
    """
    Safe user response schema.
    """

    id: str
    email: EmailStr
    username: str
    full_name: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """
    JWT token response schema.
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse