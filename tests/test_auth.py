import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    # First registration
    await client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "testpassword"
    })
    
    # Second registration with same email
    response = await client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # Register user first
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "testpassword"
    })
    
    # Login
    response = await client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401