import pytest
from httpx import AsyncClient
from app.models import User, Dream, DreamStatus
from sqlalchemy import select

@pytest.mark.asyncio
async def test_update_dream_success(client: AsyncClient, db_session, auth_headers: dict):
    # 1. Get the current user from auth_headers context or just assume it's the one in conftest
    # Typically auth_headers uses a test user. Let's create a dream for that user.
    # In conftest.py, auth_headers usually corresponds to a user.
    
    # Let's create a dream owned by the authenticated user
    from app.routers.auth import get_current_user
    # We need the user ID. 
    result = await db_session.execute(select(User).filter(User.username == "testuser"))
    user = result.scalars().first()
    
    dream = Dream(
        creator_id=user.id,
        title="Original Title",
        prompt_text="Original Prompt",
        slug="original-title"
    )
    db_session.add(dream)
    await db_session.commit()
    
    update_data = {
        "title": "Updated Title",
        "prd_text": "Updated PRD"
    }
    
    response = await client.patch(
        f"/dreams/{dream.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["prd_text"] == "Updated PRD"

@pytest.mark.asyncio
async def test_update_dream_unauthorized(client: AsyncClient, db_session, auth_headers: dict):
    # Create another user
    other_user = User(
        username="other_user",
        email="other@example.com",
        hashed_password="hashed_password",
        reputation_score=0.0
    )
    db_session.add(other_user)
    await db_session.commit()
    
    dream = Dream(
        creator_id=other_user.id,
        title="Other User Dream",
        slug="other-user-dream"
    )
    db_session.add(dream)
    await db_session.commit()
    
    response = await client.patch(
        f"/dreams/{dream.id}",
        json={"title": "Hacked Title"},
        headers=auth_headers
    )
    
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_dream_success(client: AsyncClient, db_session, auth_headers: dict):
    result = await db_session.execute(select(User).filter(User.username == "testuser"))
    user = result.scalars().first()
    
    dream = Dream(
        creator_id=user.id,
        title="To be deleted",
        slug="to-be-deleted"
    )
    db_session.add(dream)
    await db_session.commit()
    
    response = await client.delete(
        f"/dreams/{dream.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's gone
    result = await db_session.execute(select(Dream).filter(Dream.id == dream.id))
    assert result.scalars().first() is None

@pytest.mark.asyncio
async def test_delete_dream_unauthorized(client: AsyncClient, db_session, auth_headers: dict):
    other_user = User(
        username="another_user",
        email="another@example.com",
        hashed_password="password",
        reputation_score=0.0
    )
    db_session.add(other_user)
    await db_session.commit()
    
    dream = Dream(
        creator_id=other_user.id,
        title="Not yours",
        slug="not-yours"
    )
    db_session.add(dream)
    await db_session.commit()
    
    response = await client.delete(
        f"/dreams/{dream.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 403
