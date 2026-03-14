import uuid
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.proposals.models import ProposalStatus

class SimulationRequest(BaseModel):
    client_id: uuid.UUID
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    installments: int = Field(..., gt=0)

class ProposalRead(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    tenant_id: uuid.UUID
    external_protocol: str | None = None
    type: str
    amount: Decimal
    installments: int
    interest_rate: Decimal | None = None
    installment_value: Decimal | None = None
    status: ProposalStatus
    bank_response: dict | None = None
    created_at: datetime
    created_by: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
