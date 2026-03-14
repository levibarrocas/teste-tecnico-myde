import sys
import os
import pytest
import asyncio

# Ensure we can import from the app directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine
from app.core.limiter import limiter

@pytest.fixture
async def client():
    limiter.enabled = False
    # We use the direct app object for testing, avoiding the need to run the server externally
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    limiter.enabled = True

@pytest.fixture
async def auth_headers(client):
    """
    Logs in using the seed credentials and returns the Authorization header
    to be used in other tests.
    """
    response = await client.post("/auth/login", json={
        "email": "admin@acme.com",
        "password": "password123"
    })
    # If seed data isn't there, this will fail. ensure you ran `python seed.py`
    assert response.status_code == 200, "Could not login with seed credentials"
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
async def db_lifecycle():
    yield
    await engine.dispose()
