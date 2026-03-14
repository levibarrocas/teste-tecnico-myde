import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

def validate_cpf_algorithm(v: str) -> str:
    if not v.isdigit():
        raise ValueError('CPF must contain only digits')
    
    if len(v) != 11:
        raise ValueError('CPF must have 11 digits')
    
    if v == v[0] * len(v):
        raise ValueError('Invalid CPF')

    # Calculate first digit
    sum_ = sum(int(v[i]) * (10 - i) for i in range(9))
    remainder = sum_ % 11
    digit1 = 0 if remainder < 2 else 11 - remainder

    if int(v[9]) != digit1:
        raise ValueError('Invalid CPF')

    # Calculate second digit
    sum_ = sum(int(v[i]) * (11 - i) for i in range(10))
    remainder = sum_ % 11
    digit2 = 0 if remainder < 2 else 11 - remainder

    if int(v[10]) != digit2:
        raise ValueError('Invalid CPF')

    return v

class ClientCreate(BaseModel):
    name: str
    cpf: str = Field(..., min_length=11, max_length=11, description="CPF with 11 digits")
    birth_date: date
    phone: str

    @field_validator('cpf')
    def validate_cpf(cls, v):
        return validate_cpf_algorithm(v)

class ClientUpdate(BaseModel):
    name: str | None = None
    cpf: str | None = Field(None, min_length=11, max_length=11)
    birth_date: date | None = None
    phone: str | None = None

    @field_validator('cpf')
    def validate_cpf(cls, v):
        if v is not None:
            return validate_cpf_algorithm(v)
        return v

class ClientRead(BaseModel):
    id: uuid.UUID
    name: str
    cpf: str
    birth_date: date
    phone: str
    created_at: datetime
    created_by: uuid.UUID
    tenant_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
