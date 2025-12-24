from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    password_confirm: str

    @field_validator("password")
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        return v

    @field_validator("password_confirm")
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserResponce(BaseModel):
    id: int

