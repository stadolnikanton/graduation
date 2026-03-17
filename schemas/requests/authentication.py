from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    password_confirm: str

    @field_validator("password_confirm")
    def password_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v
