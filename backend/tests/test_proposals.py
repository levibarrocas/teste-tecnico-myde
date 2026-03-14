import pytest
import random

def generate_random_cpf():
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
async def test_simulation_flow(client, auth_headers):
    cpf = generate_random_cpf()
    client_res = await client.post("/api/clients/", json={
        "name": "Proposal Client",
        "cpf": cpf,
        "birth_date": "1980-01-01",
        "phone": "123456789"
    }, headers=auth_headers)
    client_id = client_res.json()["id"]

    sim_payload = {
        "client_id": client_id,
        "amount": 10000.00,
        "installments": 24
    }
    sim_res = await client.post("/api/proposals/simulate", json=sim_payload, headers=auth_headers)
    
    assert sim_res.status_code == 201
    proposal = sim_res.json()
    assert proposal["status"] == "pending"
    assert float(proposal["amount"]) == 10000.00
    
    proposal_id = proposal["id"]

    # 3. Submit Proposal
    submit_res = await client.post(
        f"/api/proposals/{proposal_id}/submit", 
        headers=auth_headers
    )
    
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == "processing"

@pytest.mark.asyncio
async def test_list_proposals(client, auth_headers):
    cpf = generate_random_cpf()
    client_res = await client.post("/api/clients/", json={
        "name": "List Prop Client",
        "cpf": cpf,
        "birth_date": "1980-01-01",
        "phone": "123456789"
    }, headers=auth_headers)
    client_id = client_res.json()["id"]

    await client.post("/api/proposals/simulate", json={
        "client_id": client_id,
        "amount": 5000.00,
        "installments": 10
    }, headers=auth_headers)

    response = await client.get("/api/proposals/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_get_proposal_by_id(client, auth_headers):
    cpf = generate_random_cpf()
    client_res = await client.post("/api/clients/", json={
        "name": "Get Prop Client",
        "cpf": cpf,
        "birth_date": "1980-01-01",
        "phone": "123456789"
    }, headers=auth_headers)
    client_id = client_res.json()["id"]

    sim_res = await client.post("/api/proposals/simulate", json={
        "client_id": client_id,
        "amount": 3000.00,
        "installments": 5
    }, headers=auth_headers)
    proposal_id = sim_res.json()["id"]

    response = await client.get(f"/api/proposals/{proposal_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == proposal_id
    assert float(data["amount"]) == 3000.00
