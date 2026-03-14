import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.proposals.models import Proposal, ProposalStatus
from app.proposals.dto import SimulationRequest
from app.users.models import User
from app.clients.service import ClientService
from app.core.sqs import enqueue_proposal

class ProposalService:
    @staticmethod
    async def create_simulation(db: AsyncSession, request: SimulationRequest, current_user: User) -> Proposal:
        # 1. Validate if Client exists and belongs to the tenant
        # We reuse the existing service to handle the check + 404 error
        client = await ClientService.get_client_by_id(db, request.client_id, current_user)

        # 2. Create the Proposal record
        new_proposal = Proposal(
            tenant_id=current_user.tenant_id,
            client_id=client.id,
            type="simulacao",
            amount=request.amount,
            installments=request.installments,
            status=ProposalStatus.PENDING,
            created_by=current_user.id
        )
        
        db.add(new_proposal)
        await db.commit()
        await db.refresh(new_proposal)
        
        # Enqueue this proposal to SQS for async processing
        await enqueue_proposal(str(new_proposal.id))
        
        return new_proposal

    @staticmethod
    async def get_proposal_by_id(db: AsyncSession, proposal_id: uuid.UUID, current_user: User) -> Proposal:
        result = await db.execute(
            select(Proposal).where(
                Proposal.id == proposal_id,
                Proposal.tenant_id == current_user.tenant_id
            )
        )
        proposal = result.scalars().first()
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proposal not found"
            )
        return proposal

    @staticmethod
    async def submit_proposal(db: AsyncSession, proposal_id: uuid.UUID, current_user: User) -> Proposal:
        proposal = await ProposalService.get_proposal_by_id(db, proposal_id, current_user)

        # In a real scenario, check if proposal.status == ProposalStatus.SIMULATED
        proposal.status = ProposalStatus.PROCESSING
        proposal.type = "proposta"
        db.add(proposal)
        await db.commit()
        await db.refresh(proposal)
        
        # Enqueue submission job to SQS
        await enqueue_proposal(str(proposal.id))
        
        return proposal

    @staticmethod
    async def get_proposals(db: AsyncSession, current_user: User, skip: int = 0, limit: int = 100, status_filter: str = None) -> list[Proposal]:
        query = select(Proposal).where(Proposal.tenant_id == current_user.tenant_id)
        
        if status_filter:
            query = query.where(Proposal.status == status_filter)
            
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
