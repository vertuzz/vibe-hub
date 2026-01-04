import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_delete_app_media_comprehensive(client: AsyncClient, auth_headers: dict):
    # 1. Setup: Create an app
    app_resp = await client.post(
        "/apps/", 
        json={"title": "Media Test App", "prompt_text": "Testing media deletion"}, 
        headers=auth_headers
    )
    assert app_resp.status_code == 200
    app = app_resp.json()
    app_id = app["id"]

    # 2. Add media to the app
    media_url = "https://example.com/test-image.png"
    media_resp = await client.post(
        f"/apps/{app_id}/media", 
        json={"media_url": media_url}, 
        headers=auth_headers
    )
    assert media_resp.status_code == 200
    media = media_resp.json()
    media_id = media["id"]

    # 3. Successful deletion
    delete_resp = await client.delete(
        f"/apps/{app_id}/media/{media_id}", 
        headers=auth_headers
    )
    assert delete_resp.status_code == 204

    # 4. Verify it's gone from the app
    get_resp = await client.get(f"/apps/{app_id}")
    assert get_resp.status_code == 200
    updated_app = get_resp.json()
    assert all(m["id"] != media_id for m in updated_app.get("media", []))

    # 5. Error: Delete non-existent media
    error_resp = await client.delete(
        f"/apps/{app_id}/media/9999", 
        headers=auth_headers
    )
    assert error_resp.status_code == 404

    # 6. Error: Delete media from non-existent app
    error_resp = await client.delete(
        f"/apps/9999/media/{media_id}", 
        headers=auth_headers
    )
    assert error_resp.status_code == 404

    # 7. Error: Unauthorized deletion (not the owner)
    # Register another user
    await client.post(
        "/auth/register", 
        json={"username": "other_user", "email": "other@example.com", "password": "password123"}
    )
    login_resp = await client.post(
        "/auth/login", 
        data={"username": "other_user", "password": "password123"}
    )
    other_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Create new media to delete
    media_resp = await client.post(
        f"/apps/{app_id}/media", 
        json={"media_url": "https://example.com/another.png"}, 
        headers=auth_headers
    )
    new_media_id = media_resp.json()["id"]

    # Try to delete as other_user
    unauth_resp = await client.delete(
        f"/apps/{app_id}/media/{new_media_id}", 
        headers=other_headers
    )
    assert unauth_resp.status_code == 403
