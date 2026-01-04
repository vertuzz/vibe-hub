"""
Tests for App likes_count, comments_count, and creator fields.
These tests verify the computed fields added to the App response schema.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_app_response_includes_creator(client: AsyncClient, auth_headers: dict):
    """Test that app response includes creator information."""
    # Create an app
    app_resp = await client.post(
        "/apps/",
        json={"title": "Test App", "prompt_text": "A test app"},
        headers=auth_headers
    )
    assert app_resp.status_code == 200
    app = app_resp.json()
    
    # Verify creator is included
    assert "creator" in app
    assert app["creator"] is not None
    assert app["creator"]["username"] == "testuser"
    assert "id" in app["creator"]
    # Ensure sensitive fields are not exposed
    assert "email" not in app["creator"]
    assert "password" not in app["creator"]


@pytest.mark.asyncio
async def test_app_response_includes_zero_counts_on_create(client: AsyncClient, auth_headers: dict):
    """Test that newly created apps have zero counts."""
    app_resp = await client.post(
        "/apps/",
        json={"title": "Fresh App", "prompt_text": "Brand new"},
        headers=auth_headers
    )
    assert app_resp.status_code == 200
    app = app_resp.json()
    
    assert app["likes_count"] == 0
    assert app["comments_count"] == 0


@pytest.mark.asyncio
async def test_app_likes_count_updates(client: AsyncClient, auth_headers: dict):
    """Test that likes_count updates when an app is liked."""
    # Create app
    app_resp = await client.post(
        "/apps/",
        json={"title": "Likeable App", "prompt_text": "Like me!"},
        headers=auth_headers
    )
    app_id = app_resp.json()["id"]
    
    # Verify initial count
    get_resp = await client.get(f"/apps/{app_id}")
    assert get_resp.json()["likes_count"] == 0
    
    # Like the app
    like_resp = await client.post(f"/apps/{app_id}/like", headers=auth_headers)
    assert like_resp.status_code == 200
    
    # Verify count updated
    get_resp = await client.get(f"/apps/{app_id}")
    assert get_resp.json()["likes_count"] == 1
    
    # Unlike the app
    unlike_resp = await client.delete(f"/apps/{app_id}/like", headers=auth_headers)
    assert unlike_resp.status_code == 200
    
    # Verify count decreased
    get_resp = await client.get(f"/apps/{app_id}")
    assert get_resp.json()["likes_count"] == 0


@pytest.mark.asyncio
async def test_app_comments_count_updates(client: AsyncClient, auth_headers: dict):
    """Test that comments_count updates when comments are added."""
    # Create app
    app_resp = await client.post(
        "/apps/",
        json={"title": "Commentable App", "prompt_text": "Comment on me!"},
        headers=auth_headers
    )
    app_id = app_resp.json()["id"]
    
    # Verify initial count
    get_resp = await client.get(f"/apps/{app_id}")
    assert get_resp.json()["comments_count"] == 0
    
    # Add first comment
    await client.post(
        f"/apps/{app_id}/comments",
        json={"content": "First comment"},
        headers=auth_headers
    )
    
    # Verify count is 1
    get_resp = await client.get(f"/apps/{app_id}")
    assert get_resp.json()["comments_count"] == 1
    
    # Add second comment
    await client.post(
        f"/apps/{app_id}/comments",
        json={"content": "Second comment"},
        headers=auth_headers
    )
    
    # Verify count is 2
    get_resp = await client.get(f"/apps/{app_id}")
    assert get_resp.json()["comments_count"] == 2


@pytest.mark.asyncio
async def test_apps_list_includes_counts_and_creator(client: AsyncClient, auth_headers: dict):
    """Test that apps list endpoint includes counts and creator for each app."""
    # Create an app
    app_resp = await client.post(
        "/apps/",
        json={"title": "Listed App", "prompt_text": "In the list"},
        headers=auth_headers
    )
    app_id = app_resp.json()["id"]
    
    # Add a like and comment
    await client.post(f"/apps/{app_id}/like", headers=auth_headers)
    await client.post(
        f"/apps/{app_id}/comments",
        json={"content": "A comment"},
        headers=auth_headers
    )
    
    # Get apps list
    list_resp = await client.get("/apps/")
    assert list_resp.status_code == 200
    apps = list_resp.json()
    
    # Find our app
    our_app = next((d for d in apps if d["id"] == app_id), None)
    assert our_app is not None
    
    # Verify counts and creator
    assert our_app["likes_count"] == 1
    assert our_app["comments_count"] == 1
    assert our_app["creator"] is not None
    assert our_app["creator"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_app_update_preserves_counts(client: AsyncClient, auth_headers: dict):
    """Test that updating an app returns correct counts."""
    # Create app
    app_resp = await client.post(
        "/apps/",
        json={"title": "Updatable App", "prompt_text": "Update me!"},
        headers=auth_headers
    )
    app_id = app_resp.json()["id"]
    
    # Add likes and comments
    await client.post(f"/apps/{app_id}/like", headers=auth_headers)
    await client.post(
        f"/apps/{app_id}/comments",
        json={"content": "Comment before update"},
        headers=auth_headers
    )
    
    # Update the app
    update_resp = await client.patch(
        f"/apps/{app_id}",
        json={"title": "Updated App Title"},
        headers=auth_headers
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    
    # Verify counts are preserved in response
    assert updated["likes_count"] == 1
    assert updated["comments_count"] == 1
    assert updated["title"] == "Updated App Title"
    assert updated["creator"] is not None


@pytest.mark.asyncio
async def test_app_fork_has_zero_counts(client: AsyncClient, auth_headers: dict):
    """Test that forked apps start with zero counts."""
    # Create original app with likes/comments
    app_resp = await client.post(
        "/apps/",
        json={"title": "Original App", "prompt_text": "Fork me!"},
        headers=auth_headers
    )
    app_id = app_resp.json()["id"]
    
    # Add likes and comments to original
    await client.post(f"/apps/{app_id}/like", headers=auth_headers)
    await client.post(
        f"/apps/{app_id}/comments",
        json={"content": "Original comment"},
        headers=auth_headers
    )
    
    # Fork the app
    fork_resp = await client.post(f"/apps/{app_id}/fork", headers=auth_headers)
    assert fork_resp.status_code == 200
    forked = fork_resp.json()
    
    # Verify forked app has zero counts (not inherited)
    assert forked["likes_count"] == 0
    assert forked["comments_count"] == 0
    assert forked["parent_app_id"] == app_id
    assert forked["creator"] is not None


@pytest.mark.asyncio
async def test_app_creator_avatar_included(client: AsyncClient, auth_headers: dict):
    """Test that creator avatar field is included (even if None)."""
    app_resp = await client.post(
        "/apps/",
        json={"title": "Avatar Test", "prompt_text": "Check avatar"},
        headers=auth_headers
    )
    app = app_resp.json()
    
    # Avatar should be in creator object (may be None)
    assert "avatar" in app["creator"]


@pytest.mark.asyncio
async def test_multiple_apps_batch_counts(client: AsyncClient, auth_headers: dict):
    """Test that batch count queries work correctly for multiple apps."""
    app_ids = []
    
    # Create multiple apps
    for i in range(3):
        resp = await client.post(
            "/apps/",
            json={"title": f"App {i}", "prompt_text": f"Content {i}"},
            headers=auth_headers
        )
        app_ids.append(resp.json()["id"])
    
    # Add varying likes to each app
    # App 0: 0 likes, App 1: 1 like, App 2: 1 like
    await client.post(f"/apps/{app_ids[1]}/like", headers=auth_headers)
    
    # We need another user to like app 2 since same user can't like twice
    # For simplicity, just add a comment to app 2 instead
    await client.post(
        f"/apps/{app_ids[2]}/comments",
        json={"content": "Comment on app 2"},
        headers=auth_headers
    )
    
    # Get all apps
    list_resp = await client.get("/apps/")
    apps = list_resp.json()
    
    # Verify counts are correct for each
    app_map = {d["id"]: d for d in apps}
    
    assert app_map[app_ids[0]]["likes_count"] == 0
    assert app_map[app_ids[0]]["comments_count"] == 0
    
    assert app_map[app_ids[1]]["likes_count"] == 1
    assert app_map[app_ids[1]]["comments_count"] == 0
    
    assert app_map[app_ids[2]]["likes_count"] == 0
    assert app_map[app_ids[2]]["comments_count"] == 1
