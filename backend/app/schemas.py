from pydantic import BaseModel, EmailStr
from typing import Optional

class BootstrapAdminRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class BootstrapAdminResponse(BaseModel):
    message: str
    admin_email: str

class TokenResponse(BaseModel):
    bootstrap_token: str
    message: str

class ErrorResponse(BaseModel):
    detail: str