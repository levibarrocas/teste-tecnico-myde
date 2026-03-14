import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base

class ProposalStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SIMULATED = "simulated"
    SIMULATION_FAILED = "simulation_failed"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)

    external_protocol: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False)  # simulacao / proposta
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    installments: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Fields returned by the bank (nullable initially)
    interest_rate: Mapped[float] = mapped_column(Numeric(10, 4), nullable=True)
    installment_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=True)
    
    status: Mapped[str] = mapped_column(String, nullable=False, default=ProposalStatus.PENDING)
    bank_response: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
