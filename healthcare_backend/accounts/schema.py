from pydantic import BaseModel, EmailStr , ConfigDict
from typing import Optional
from datetime import date

# Output schema
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True) 


# Input schema
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    profile_type_id: Optional[int] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
