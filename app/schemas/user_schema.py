from pydantic import BaseModel, Field
from typing import Optional

class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    age: int = Field(..., ge=18, description="La edad debe ser 18 o mayor")
    had_pregnancy: bool
