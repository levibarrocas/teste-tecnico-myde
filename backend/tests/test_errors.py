import pytest
import uuid
import random

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
async def test_auth_failures(client):
    # 1. Wrong Password
    res = await client.post("/auth/login", json={
        "email": "admin@acme.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401
    assert "Incorrect email or password" in res.json()["detail"]
    
    # 2. User not found
    res = await client.post("/auth/login", json={
        "email": "ghost@acme.com",
        "password": "password123"
    })
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_client_logic_errors(client, auth_headers):
    # 1. Client Not Found (404)
    random_id = str(uuid.uuid4())
    res = await client.get(f"/api/clients/{random_id}", headers=auth_headers)
    assert res.status_code == 404
    assert "Client not found" in res.json()["detail"]

    # 2. Duplicate CPF (409 Conflict)
    cpf = generate_valid_cpf()
    payload = {
        "name": "Original Client",
        "cpf": cpf,
        "birth_date": "1990-01-01",
        "phone": "123456789"
    }
    # First create - Success
    await client.post("/api/clients/", json=payload, headers=auth_headers)
    
    # Second create - Fail
    res_conflict = await client.post("/api/clients/", json=payload, headers=auth_headers)
    assert res_conflict.status_code == 409
    assert "Client with this CPF already exists" in res_conflict.json()["detail"]

@pytest.mark.asyncio
async def test_proposal_logic_errors(client, auth_headers):
    # 1. Proposal Not Found
    random_id = str(uuid.uuid4())
    res = await client.get(f"/api/proposals/{random_id}", headers=auth_headers)
    assert res.status_code == 404

    # 2. Simulate for non-existent client
    # The service checks for client existence before creating proposal
    res = await client.post("/api/proposals/simulate", json={
        "client_id": random_id,
        "amount": 1000.00,
        "installments": 12
    }, headers=auth_headers)
    assert res.status_code == 404
    assert "Client not found" in res.json()["detail"]