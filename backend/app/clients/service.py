import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.clients.models import Client
from app.clients.dto import ClientCreate, ClientUpdate
from app.users.models import User

class ClientService:
    @staticmethod
    async def create_client(db: AsyncSession, client_data: ClientCreate, current_user: User) -> Client:
        # 1. Check if client with same CPF exists for this tenant
        result = await db.execute(
            select(Client).where(
                Client.tenant_id == current_user.tenant_id,
                Client.cpf == client_data.cpf
            )
        )
        existing_client = result.scalars().first()
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Client with this CPF already exists for this tenant"
            )

        # 2. Create new client
        new_client = Client(
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            **client_data.model_dump()
        )
        
        db.add(new_client)
        await db.commit()
        await db.refresh(new_client)
        
        return new_client

    @staticmethod
    async def get_clients(db: AsyncSession, current_user: User, skip: int = 0, limit: int = 100) -> list[Client]:
        result = await db.execute(
            select(Client)
            .where(Client.tenant_id == current_user.tenant_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_client_by_id(db: AsyncSession, client_id: uuid.UUID, current_user: User) -> Client:
        result = await db.execute(
            select(Client).where(
                Client.id == client_id,
                Client.tenant_id == current_user.tenant_id
            )
        )
        client = result.scalars().first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        return client

    @staticmethod
    async def update_client(db: AsyncSession, client_id: uuid.UUID, client_data: ClientUpdate, current_user: User) -> Client:
        client = await ClientService.get_client_by_id(db, client_id, current_user)

        # Check CPF uniqueness if updating CPF
        if client_data.cpf is not None and client_data.cpf != client.cpf:
            result = await db.execute(
                select(Client).where(
                    Client.tenant_id == current_user.tenant_id,
                    Client.cpf == client_data.cpf
                )
            )
            if result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Client with this CPF already exists for this tenant"
                )

        for key, value in client_data.model_dump(exclude_unset=True).items():
            setattr(client, key, value)

        await db.commit()
        await db.refresh(client)
        return client
