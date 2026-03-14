import pytest
import random
import uuid
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.proposals.models import Proposal

def generate_random_cpf():
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    sum_ = sum(cpf[i] * (10 - i) for i in range(9))
    remainder = sum_ % 11
    digit1 = 0 if remainder < 2 else 11 - remainder
    cpf.append(digit1)
    
    sum_ = sum(cpf[i] * (11 - i) for i in range(10))
    remainder = sum_ % 11
    digit2 = 0 if remainder < 2 else 11 - remainder
    cpf.append(digit2)
    
    return "".join(map(str, cpf))

@pytest.mark.asyncio
async def test_bank_callback_success(client, auth_headers):
    cpf = generate_random_cpf()
    client_res = await client.post("/api/clients/", json={
        "name": "Webhook Client",
        "cpf": cpf,
        "birth_date": "1990-01-01",
        "phone": "5511999999999"
    }, headers=auth_headers)
    assert client_res.status_code == 201
    client_id = client_res.json()["id"]

    sim_res = await client.post("/api/proposals/simulate", json={
        "client_id": client_id,
        "amount": 10000.00,
        "installments": 24
    }, headers=auth_headers)
    assert sim_res.status_code == 201
    proposal_id = sim_res.json()["id"]

    test_protocol = f"PROTO-{random.randint(1000,9999)}"
    
    async with AsyncSessionLocal() as session:
        p_uuid = uuid.UUID(proposal_id)
        result = await session.execute(select(Proposal).where(Proposal.id == p_uuid))
        proposal = result.scalars().first()
        if proposal:
            proposal.external_protocol = test_protocol
            session.add(proposal)
            await session.commit()

    webhook_payload = {
        "protocol": test_protocol,
        "event": "proposal_update",
        "status": "approved",
        "data": {
            "interest_rate": 0.02,
            "installment_value": 500.00,
            "approved_amount": 10000.00
        }
    }
    
    response = await client.post("/api/webhooks/bank-callback", json=webhook_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Callback processed successfully"

    # 4. Verify Update via API
    get_res = await client.get(f"/api/proposals/{proposal_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "approved"

@pytest.mark.asyncio
async def test_bank_callback_idempotency(client, auth_headers):
    # 1. Setup Data (Client + Proposal)
    cpf = generate_random_cpf()
    client_res = await client.post("/api/clients/", json={
        "name": "Idempotency Client",
        "cpf": cpf,
        "birth_date": "1990-01-01",
        "phone": "5511999999999"
    }, headers=auth_headers)
    client_id = client_res.json()["id"]

    sim_res = await client.post("/api/proposals/simulate", json={
        "client_id": client_id,
        "amount": 5000.00,
        "installments": 12
    }, headers=auth_headers)
    proposal_id = sim_res.json()["id"]

    test_protocol = f"PROTO-IDEM-{random.randint(1000,9999)}"
    
    # Manually assign protocol to proposal in DB
    async with AsyncSessionLocal() as session:
        p_uuid = uuid.UUID(proposal_id)
        result = await session.execute(select(Proposal).where(Proposal.id == p_uuid))
        proposal = result.scalars().first()
        if proposal:
            proposal.external_protocol = test_protocol
            session.add(proposal)
            await session.commit()

    webhook_payload = {
        "protocol": test_protocol,
        "event": "proposal_update",
        "status": "approved"
    }
    
    # 2. First Webhook Call
    response1 = await client.post("/api/webhooks/bank-callback", json=webhook_payload)
    assert response1.status_code == 200

    # 3. Second Webhook Call (Simulate Retry)
    # Expect 200 OK because the service handles idempotency by checking current status
    response2 = await client.post("/api/webhooks/bank-callback", json=webhook_payload)
    assert response2.status_code == 200
