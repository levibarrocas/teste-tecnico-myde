import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.clients.dto import ClientCreate, ClientRead, ClientUpdate
from app.clients.service import ClientService

router = APIRouter()

@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new client for the current tenant.
    """
    return await ClientService.create_client(db, client_data, current_user)

@router.get("/", response_model=list[ClientRead])
async def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve clients for the current tenant with pagination.
    """
    return await ClientService.get_clients(db, current_user, skip, limit)

@router.get("/{client_id}", response_model=ClientRead)
async def read_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific client by ID.
    """
    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        )
    return await ClientService.get_client_by_id(db, client_uuid, current_user)

@router.put("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing client.
    """
    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        )
    return await ClientService.update_client(db, client_uuid, client_data, current_user)
