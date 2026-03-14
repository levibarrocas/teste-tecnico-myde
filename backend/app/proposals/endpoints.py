import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.proposals.dto import SimulationRequest, ProposalRead
from app.proposals.service import ProposalService

router = APIRouter()

@router.post("/simulate", response_model=ProposalRead, status_code=status.HTTP_201_CREATED)
async def create_simulation(
    request: SimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a credit simulation.
    """
    return await ProposalService.create_simulation(db, request, current_user)

@router.post("/{proposal_id}/submit", response_model=ProposalRead)
async def submit_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a simulated proposal to the bank.
    """
    try:
        proposal_uuid = uuid.UUID(proposal_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    return await ProposalService.submit_proposal(db, proposal_uuid, current_user)

@router.get("/", response_model=list[ProposalRead])
async def read_proposals(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve proposals for the current tenant with pagination and optional status filter.
    """
    return await ProposalService.get_proposals(db, current_user, skip, limit, status)

@router.get("/{proposal_id}", response_model=ProposalRead)
async def read_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific proposal by ID.
    """
    try:
        proposal_uuid = uuid.UUID(proposal_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    return await ProposalService.get_proposal_by_id(db, proposal_uuid, current_user)
