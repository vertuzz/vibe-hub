"""Tests for Open Graph meta tags endpoint."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_app_og_existing(client: AsyncClient, auth_headers):
    """Test OG endpoint returns proper meta tags for existing app."""
    # Create an app first
    app_data = {
        "title": "Test OG App",
        "prompt_text": "A test app for OG meta tags testing",
        "status": "Live"
    }
    create_response = await client.post("/apps/", json=app_data, headers=auth_headers)
    assert create_response.status_code == 200
    app = create_response.json()
    
    response = await client.get(f"/og/apps/{app['slug']}")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    content = response.text
    # Check for OG meta tags
    assert 'property="og:title"' in content
    assert 'property="og:description"' in content
    assert 'property="og:image"' in content
    assert 'property="og:url"' in content
    assert app["title"] in content
    assert f"/apps/{app['slug']}" in content


@pytest.mark.asyncio
async def test_get_app_og_by_id(client: AsyncClient, auth_headers):
    """Test OG endpoint works with app ID."""
    # Create an app first
    app_data = {
        "title": "Test OG App By ID",
        "prompt_text": "A test app",
        "status": "Live"
    }
    create_response = await client.post("/apps/", json=app_data, headers=auth_headers)
    app = create_response.json()
    
    response = await client.get(f"/og/apps/{app['id']}")
    assert response.status_code == 200
    assert app["title"] in response.text


@pytest.mark.asyncio
async def test_get_app_og_not_found(client: AsyncClient):
    """Test OG endpoint handles non-existent app gracefully."""
    response = await client.get("/og/apps/non-existent-app-slug-12345")
    assert response.status_code == 200  # Still returns 200 with generic tags
    assert "App Not Found" in response.text


@pytest.mark.asyncio
async def test_get_user_og_existing(client: AsyncClient, auth_user_and_headers):
    """Test OG endpoint returns proper meta tags for existing user."""
    user, _ = auth_user_and_headers
    response = await client.get(f"/og/users/{user.username}")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    content = response.text
    assert 'property="og:title"' in content
    assert user.username in content


@pytest.mark.asyncio
async def test_get_user_og_not_found(client: AsyncClient):
    """Test OG endpoint handles non-existent user gracefully."""
    response = await client.get("/og/users/nonexistent_user_12345")
    assert response.status_code == 200  # Still returns 200 with generic tags
    assert "User Not Found" in response.text


@pytest.mark.asyncio
async def test_og_escapes_html(client: AsyncClient, auth_headers):
    """Test that OG endpoint properly escapes HTML to prevent XSS."""
    # Create app with potentially dangerous content
    app_data = {
        "title": '<script>alert("xss")</script>',
        "prompt_text": '"><img src=x onerror=alert(1)>',
        "status": "Live"
    }
    create_response = await client.post("/apps/", json=app_data, headers=auth_headers)
    app = create_response.json()
    
    response = await client.get(f"/og/apps/{app['slug']}")
    content = response.text
    
    # Ensure content is escaped - the malicious title should NOT appear unescaped
    # Look for the escaped version in the title meta tag
    assert '&lt;script&gt;alert' in content
    # The original XSS payload should be escaped
    assert '<script>alert("xss")</script>' not in content
