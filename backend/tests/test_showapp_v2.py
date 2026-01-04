import pytest
from httpx import AsyncClient
from app.models import User, AppStatus
from sqlalchemy import select

@pytest.mark.asyncio
async def test_api_key_auth_and_app_v2_fields(client: AsyncClient, db_session):
    # 1. Create a user with an API key
    user = User(
        username="agent_user",
        email="agent@example.com",
        api_key="secret-agent-key",
        reputation_score=0.0
    )
    db_session.add(user)
    await db_session.commit()
    
    # 2. Try to create an app using X-API-Key header
    app_data = {
        "prompt_text": "A futuristic city built on clouds",
        "prd_text": "Full specs for cloud city",
        "status": "Live",
        "app_url": "https://cloud-city.vercel.app",
        "is_agent_submitted": True,
        "tool_ids": [],
        "tag_ids": []
    }
    
    response = await client.post(
        "/apps/",
        json=app_data,
        headers={"X-API-Key": "secret-agent-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["app_url"] == "https://cloud-city.vercel.app"
    assert data["is_agent_submitted"] is True
    assert data["creator_id"] == user.id

@pytest.mark.asyncio
async def test_api_key_auth_failure(client: AsyncClient):
    response = await client.post(
        "/apps/",
        json={"prompt_text": "test"},
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401
@pytest.mark.asyncio
async def test_app_with_title_and_no_prompt(client: AsyncClient, auth_headers: dict):
    app_data = {
        "title": "My App Title",
        "prompt_text": None,
        "status": "Concept"
    }
    response = await client.post(
        "/apps/",
        json=app_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My App Title"
    assert data["prompt_text"] is None
