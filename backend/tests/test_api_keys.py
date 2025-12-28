import pytest
from httpx import AsyncClient
from app.models import User
from sqlalchemy import select

@pytest.mark.asyncio
async def test_api_key_generation_on_register(client: AsyncClient, db_session):
    # 1. Register a new user
    user_data = {
        "username": "test_key_user",
        "email": "test_key@example.com",
        "password": "testpassword123"
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    
    # 2. Verify API key is present
    api_key = data.get("api_key")
    assert api_key is not None
    assert len(api_key) > 20 # token_urlsafe(32) should be reasonably long
    
    # 3. Verify the key works for authentication
    me_response = await client.get("/auth/me", headers={"X-API-Key": api_key})
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "test_key_user"

@pytest.mark.asyncio
async def test_api_key_regeneration(client: AsyncClient, db_session):
    # 1. Create a user and login to get JWT
    user = User(
        username="regene_user",
        email="regene@example.com",
        hashed_password="hashed_password",
        api_key="initial-key",
        reputation_score=0.0
    )
    db_session.add(user)
    await db_session.commit()
    
    # Login to get token
    from app.core import security
    from datetime import timedelta
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=15)
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 2. Call regeneration endpoint
    response = await client.post("/auth/api-key/regenerate", headers=headers)
    assert response.status_code == 200
    data = response.json()
    new_api_key = data.get("api_key")
    
    assert new_api_key is not None
    assert new_api_key != "initial-key"
    
    # 3. Verify old key fails
    fail_response = await client.get("/auth/me", headers={"X-API-Key": "initial-key"})
    assert fail_response.status_code == 401
    
    # 4. Verify new key works
    success_response = await client.get("/auth/me", headers={"X-API-Key": new_api_key})
    assert success_response.status_code == 200
    assert success_response.json()["id"] == user.id
