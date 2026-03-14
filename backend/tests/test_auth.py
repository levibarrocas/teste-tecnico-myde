import pytest
from app.core.limiter import limiter

@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post("/auth/login", json={
        "email": "admin@acme.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_get_current_user(client, auth_headers):
    response = await client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "admin@acme.com"

@pytest.mark.asyncio
async def test_login_rate_limit(client):
    limiter.enabled = True
    # Attempt login multiple times to trigger rate limit (5/minute)
    limit_reached = False
    for _ in range(10):
        response = await client.post("/auth/login", json={
            "email": "admin@acme.com",
            "password": "password123"
        })
        if response.status_code == 429:
            limit_reached = True
            break
    
    assert limit_reached, "Rate limit of 5/minute was not triggered"
