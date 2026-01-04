import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_liked_by_user_id_filter(client: AsyncClient, auth_headers: dict):
    # 1. Create an app
    app_resp = await client.post(
        "/apps/", 
        json={"title": "App to be Liked", "prompt_text": "Filter test"}, 
        headers=auth_headers
    )
    assert app_resp.status_code == 200
    app_id = app_resp.json()["id"]

    # 2. Like the app
    like_resp = await client.post(f"/apps/{app_id}/like", headers=auth_headers)
    assert like_resp.status_code == 200

    # 3. Get user info to get the ID
    user_resp = await client.get("/auth/me", headers=auth_headers)
    assert user_resp.status_code == 200
    user_id = user_resp.json()["id"]

    # 4. Filter by liked_by_user_id
    filter_resp = await client.get(f"/apps/?liked_by_user_id={user_id}", headers=auth_headers)
    assert filter_resp.status_code == 200
    apps = filter_resp.json()
    assert len(apps) >= 1
    assert any(d["id"] == app_id for d in apps)

    # 5. Filter by a different user ID (should not return this app)
    filter_resp_other = await client.get("/apps/?liked_by_user_id=99999", headers=auth_headers)
    assert filter_resp_other.status_code == 200
    apps_other = filter_resp_other.json()
    assert not any(d["id"] == app_id for d in apps_other)
