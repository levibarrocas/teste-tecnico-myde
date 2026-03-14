import pytest
import random
import uuid
from app.database import AsyncSessionLocal
from app.tenants.models import Tenant
from app.users.models import User
from app.core.security import get_password_hash

# Helper to generate valid CPF (reused locally to keep file independent)
def generate_valid_cpf():
    cpf = [random.randint(0, 9) for _ in range(9)]
    # First digit
    sum_ = sum(cpf[i] * (10 - i) for i in range(9))
    remainder = sum_ % 11
    digit1 = 0 if remainder < 2 else 11 - remainder
    cpf.append(digit1)
    # Second digit
    sum_ = sum(cpf[i] * (11 - i) for i in range(10))
    remainder = sum_ % 11
    digit2 = 0 if remainder < 2 else 11 - remainder
    cpf.append(digit2)
    return "".join(map(str, cpf))

@pytest.mark.asyncio
async def test_tenant_data_isolation(client, auth_headers):
    """
    Verify that Tenant B cannot access data created by Tenant A.
    """
    
    # 1. Tenant A (from auth_headers/seed) creates a client
    cpf_a = generate_valid_cpf()
    res_a = await client.post("/api/clients/", json={
        "name": "Client of Tenant A",
        "cpf": cpf_a,
        "birth_date": "2000-01-01",
        "phone": "11999999999"
    }, headers=auth_headers)
    assert res_a.status_code == 201
    client_a_id = res_a.json()["id"]

    # 2. Create a new Tenant B and User B in the database
    async with AsyncSessionLocal() as session:
        unique_suffix = str(uuid.uuid4())[:8]
        tenant_b = Tenant(name=f"Tenant B {unique_suffix}", document=str(random.randint(10**13, 10**14 - 1)))
        session.add(tenant_b)
        await session.commit()
        await session.refresh(tenant_b)

        user_email = f"user_{unique_suffix}@tenantb.com"
        user_b = User(
            tenant_id=tenant_b.id,
            name="User B",
            email=user_email,
            password_hash=get_password_hash("password123"),
            role="admin",
            is_active=True
        )
        session.add(user_b)
        await session.commit()

    # 3. Login as User B
    login_res = await client.post("/auth/login", json={
        "email": user_email,
        "password": "password123"
    })
    assert login_res.status_code == 200
    token_b = login_res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 4. Tenant B tries to list clients (Should NOT see Client A)
    list_res = await client.get("/api/clients/", headers=headers_b)
    assert list_res.status_code == 200
    clients_b = list_res.json()
    
    # Check that client_a_id is NOT in the list returned to Tenant B
    ids_b = [c["id"] for c in clients_b]
    assert client_a_id not in ids_b, "Tenant B should not see Tenant A's client in list"

    # 5. Tenant B tries to access Client A by ID (Should get 404)
    get_res = await client.get(f"/api/clients/{client_a_id}", headers=headers_b)
    assert get_res.status_code == 404, "Tenant B should receive 404 when accessing Tenant A's client"