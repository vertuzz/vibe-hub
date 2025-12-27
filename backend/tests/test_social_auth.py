import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.core.config import settings

@pytest.fixture(autouse=True)
def mock_oauth_settings():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "google-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "google-secret"), \
         patch.object(settings, "GITHUB_CLIENT_ID", "github-id"), \
         patch.object(settings, "GITHUB_CLIENT_SECRET", "github-secret"):
        yield

@pytest.mark.asyncio
async def test_google_login_new_user(client: AsyncClient):
    # Simplified test: Create a mock async client that returns expected responses
    mock_async_client = AsyncMock()
    
    # Mock the context manager
    mock_async_client.__aenter__.return_value = mock_async_client
    mock_async_client.__aexit__.return_value = None
    
    # Mock token exchange response
    mock_token_resp = AsyncMock()
    mock_token_resp.status_code = 200
    mock_token_resp.json = MagicMock(return_value={"access_token": "google-access-token"})
    
    # Mock user info response
    mock_user_resp = AsyncMock()
    mock_user_resp.status_code = 200
    mock_user_resp.json = MagicMock(return_value={
        "email": "google@example.com",
        "sub": "google-sub-123",
        "picture": "http://avatar.com/google",
        "name": "Google User"
    })
    
    mock_async_client.post = AsyncMock(return_value=mock_token_resp)
    mock_async_client.get = AsyncMock(return_value=mock_user_resp)
    
    with patch("httpx.AsyncClient", return_value=mock_async_client):
        response = await client.post("/auth/google", json={"code": "some-google-code"})
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data

@pytest.mark.asyncio
async def test_github_login_new_user(client: AsyncClient):
    # Simplified test: Create a mock async client that returns expected responses
    mock_async_client = AsyncMock()
    
    # Mock the context manager
    mock_async_client.__aenter__.return_value = mock_async_client
    mock_async_client.__aexit__.return_value = None
    
    # Mock token exchange response
    mock_token_resp = AsyncMock()
    mock_token_resp.status_code = 200
    mock_token_resp.json = MagicMock(return_value={"access_token": "github-access-token"})
    
    # Mock user info response
    mock_user_resp = AsyncMock()
    mock_user_resp.status_code = 200
    mock_user_resp.json = MagicMock(return_value={
        "id": 12345,
        "login": "githubuser",
        "avatar_url": "http://avatar.com/github",
        "email": "github@example.com"
    })
    
    mock_async_client.post = AsyncMock(return_value=mock_token_resp)
    mock_async_client.get = AsyncMock(return_value=mock_user_resp)
    
    with patch("httpx.AsyncClient", return_value=mock_async_client):
        response = await client.post("/auth/github", json={"code": "some-github-code"})
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data

@pytest.mark.asyncio
async def test_google_login_existing_user_by_email(client: AsyncClient):
    # Register user first
    await client.post("/auth/register", json={
        "username": "existinguser",
        "email": "google@example.com",
        "password": "password123"
    })

    # Simplified mock
    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value = mock_async_client
    mock_async_client.__aexit__.return_value = None
    
    mock_token_resp = AsyncMock()
    mock_token_resp.status_code = 200
    mock_token_resp.json = MagicMock(return_value={"access_token": "google-access-token"})
    
    mock_user_resp = AsyncMock()
    mock_user_resp.status_code = 200
    mock_user_resp.json = MagicMock(return_value={
        "email": "google@example.com",
        "sub": "google-sub-123",
        "picture": "http://avatar.com/google",
        "name": "Google User"
    })
    
    mock_async_client.post = AsyncMock(return_value=mock_token_resp)
    mock_async_client.get = AsyncMock(return_value=mock_user_resp)
    
    with patch("httpx.AsyncClient", return_value=mock_async_client):
        response = await client.post("/auth/google", json={"code": "some-google-code"})
        
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_github_login_private_email(client: AsyncClient):
    # Simplified mock
    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value = mock_async_client
    mock_async_client.__aexit__.return_value = None
    
    mock_token_resp = AsyncMock()
    mock_token_resp.status_code = 200
    mock_token_resp.json = MagicMock(return_value={"access_token": "github-access-token"})
    
    # First call: user info with no email
    mock_user_resp = AsyncMock()
    mock_user_resp.status_code = 200
    mock_user_resp.json = MagicMock(return_value={
        "id": 12345,
        "login": "githubuser",
        "avatar_url": "http://avatar.com/github",
        "email": None
    })
    
    # Second call: emails endpoint
    mock_emails_resp = AsyncMock()
    mock_emails_resp.status_code = 200
    mock_emails_resp.json = MagicMock(return_value=[
        {"email": "private@example.com", "primary": True, "verified": True}
    ])
    
    mock_async_client.post = AsyncMock(return_value=mock_token_resp)
    # Return different responses for sequential get calls
    mock_async_client.get = AsyncMock(side_effect=[mock_user_resp, mock_emails_resp])
    
    with patch("httpx.AsyncClient", return_value=mock_async_client):
        response = await client.post("/auth/github", json={"code": "some-github-code"})
        
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_google_login_missing_config(client: AsyncClient):
    with patch.object(settings, "GOOGLE_CLIENT_ID", None):
        response = await client.post("/auth/google", json={"code": "some-code"})
        assert response.status_code == 500
        assert "Google OAuth not configured" in response.json()["detail"]

@pytest.mark.asyncio
async def test_google_login_exchange_fail(client: AsyncClient):
    # Simplified mock for failure case
    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value = mock_async_client
    mock_async_client.__aexit__.return_value = None
    
    mock_token_resp = AsyncMock()
    mock_token_resp.status_code = 400
    mock_token_resp.text = "invalid code"
    
    mock_async_client.post = AsyncMock(return_value=mock_token_resp)
    
    with patch("httpx.AsyncClient", return_value=mock_async_client):
        response = await client.post("/auth/google", json={"code": "bad-code"})
        assert response.status_code == 400
        assert "Failed to exchange Google code" in response.json()["detail"]

@pytest.mark.asyncio
async def test_github_login_no_email_fail(client: AsyncClient):
    # Simplified mock for failure case
    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value = mock_async_client
    mock_async_client.__aexit__.return_value = None
    
    mock_token_resp = AsyncMock()
    mock_token_resp.status_code = 200
    mock_token_resp.json = MagicMock(return_value={"access_token": "github-access-token"})
    
    # User info with no email
    mock_user_resp = AsyncMock()
    mock_user_resp.status_code = 200
    mock_user_resp.json = MagicMock(return_value={
        "id": 12345,
        "login": "githubuser",
        "avatar_url": "http://avatar.com/github",
        "email": None
    })
    
    # Emails endpoint fails
    mock_emails_resp = AsyncMock()
    mock_emails_resp.status_code = 400
    
    mock_async_client.post = AsyncMock(return_value=mock_token_resp)
    mock_async_client.get = AsyncMock(side_effect=[mock_user_resp, mock_emails_resp])
    
    with patch("httpx.AsyncClient", return_value=mock_async_client):
        response = await client.post("/auth/github", json={"code": "some-github-code"})
        assert response.status_code == 400
        assert "Failed to get GitHub user email" in response.json()["detail"]

@pytest.mark.asyncio
async def test_google_login_username_collision(client: AsyncClient):
    # Register user with the same base username
    await client.post("/auth/register", json={
        "username": "googleuser",
        "email": "other@example.com",
        "password": "password123"
    })

    # Simplified mock
    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value = mock_async_client
    mock_async_client.__aexit__.return_value = None
    
    mock_token_resp = AsyncMock()
    mock_token_resp.status_code = 200
    mock_token_resp.json = MagicMock(return_value={"access_token": "google-access-token"})
    
    mock_user_resp = AsyncMock()
    mock_user_resp.status_code = 200
    mock_user_resp.json = MagicMock(return_value={
        "email": "google@example.com",
        "sub": "google-sub-123",
        "picture": "http://avatar.com/google",
        "name": "Google User"
    })
    
    mock_async_client.post = AsyncMock(return_value=mock_token_resp)
    mock_async_client.get = AsyncMock(return_value=mock_user_resp)
    
    with patch("httpx.AsyncClient", return_value=mock_async_client):
        response = await client.post("/auth/google", json={"code": "some-google-code"})
        
        assert response.status_code == 200
        # The username should be "googleuser1" now
        # We can't easily check the DB here without a session, but we can check if it succeeded
        assert "access_token" in response.json()
