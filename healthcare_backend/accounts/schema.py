from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date
from ninja import Schema
from typing import Literal

# Output schema
class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True) 


# Input schema
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    profile_type_id: int
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None


# Partial update schema
class UserPatch(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None


class GoogleAuthRequest(BaseModel):
    code: str
    error: Optional[str] = None


class GoogleAuthResponse(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: UserOut
    model_config = ConfigDict(from_attributes=True)


# OTP schema
class RequestOtpIn(Schema):
    identifier: str
    channel: Literal["sms","email"] = "sms"


class VerifyOtpIn(Schema):
    identifier: str
    code: str


class TokenOut(Schema):
    refresh: str
    access: str

class CompleteProfileIn(Schema):
    verification_id: str
    first_name: str
    last_name: str
    email: str
    date_of_birth: date
    gender: str
    is_referred: bool = False