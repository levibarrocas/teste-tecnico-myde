import uuid
from pydantic import BaseModel, ConfigDict

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRead(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    tenant_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
