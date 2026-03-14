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
async def test_create_client(client, auth_headers):
    payload = {
        "name": "Test Client",
        "cpf": generate_random_cpf(),
        "birth_date": "1990-01-01",
        "phone": "5511999999999"
    }
    response = await client.post("/api/clients/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    return data["id"]

@pytest.mark.asyncio
async def test_list_clients(client, auth_headers):
    response = await client.get("/api/clients/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_client(client, auth_headers):
    # First create a client to update
    cpf = generate_random_cpf()
    create_res = await client.post("/api/clients/", json={
        "name": "To Update",
        "cpf": cpf,
        "birth_date": "1990-01-01",
        "phone": "5511999999999"
    }, headers=auth_headers)
    client_id = create_res.json()["id"]

    # Now update it
    update_res = await client.put(f"/api/clients/{client_id}", json={
        "name": "Updated Name"
    }, headers=auth_headers)
    
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Updated Name"
    assert update_res.json()["cpf"] == cpf # Should remain unchanged
