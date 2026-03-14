import asyncio
import sys
import os
from sqlalchemy import select

# Ensure we can import from the app directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.tenants.models import Tenant
from app.users.models import User
from app.core.security import get_password_hash

async def seed_data():
    async with AsyncSessionLocal() as session:
        print("Starting seed process...")

        # 1. Create a Test Tenant
        # We check if it exists first to avoid duplicates if you run this twice
        result = await session.execute(select(Tenant).where(Tenant.name == "Acme Corp"))
        tenant = result.scalars().first()

        if not tenant:
            tenant = Tenant(name="Acme Corp", document="12345678000199")
            session.add(tenant)
            await session.commit()
            await session.refresh(tenant)
            print(f"Created Tenant: {tenant.name} (ID: {tenant.id})")
        else:
            print(f"Tenant already exists: {tenant.name}")

        # 2. Create a Test User
        result = await session.execute(select(User).where(User.email == "admin@acme.com"))
        user = result.scalars().first()

        if not user:
            user = User(
                tenant_id=tenant.id,
                name="Alice Admin",
                email="admin@acme.com",
                password_hash=get_password_hash("password123"), # The password you will use to login
                role="admin",
                is_active=True
            )
            session.add(user)
            await session.commit()
            print(f"Created User: {user.email}")
        else:
            print(f"User already exists: {user.email}")

if __name__ == "__main__":
    asyncio.run(seed_data())