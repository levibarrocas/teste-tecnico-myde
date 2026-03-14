import pytest

@pytest.mark.asyncio
async def test_create_client_invalid_cpf(client, auth_headers):
    # 1. Test Invalid Checksum (Numbers don't match math)
    payload = {
        "name": "Invalid CPF Client",
        "cpf": "12345678900", # Logically invalid
        "birth_date": "1990-01-01",
        "phone": "5511999999999"
    }
    response = await client.post("/api/clients/", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "Invalid CPF" in response.text

    # 2. Test All Digits Equal (Known invalid pattern)
    payload["cpf"] = "11111111111"
    response = await client.post("/api/clients/", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "Invalid CPF" in response.text

    # 3. Test Wrong Length (Short)
    payload["cpf"] = "1234567890" # 10 digits
    response = await client.post("/api/clients/", json=payload, headers=auth_headers)
    assert response.status_code == 422
    
    # 4. Test Non-numeric
    payload["cpf"] = "abcdefghijk"
    response = await client.post("/api/clients/", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "CPF must contain only digits" in response.text