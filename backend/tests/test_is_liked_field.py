import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_apps_is_liked_field(client: AsyncClient, auth_headers: dict):
    # Setup: Create an app
    app_resp = await client.post(
        "/apps/", 
        json={"prompt_text": "Test App for is_liked check"}, 
        headers=auth_headers
    )
    assert app_resp.status_code == 200
    app_id = app_resp.json()["id"]

    # 1. Verify initial status (is_liked=False)
    # Check List endpoint
    list_resp = await client.get("/apps/", headers=auth_headers)
    assert list_resp.status_code == 200
    apps = list_resp.json()
    our_app = next(d for d in apps if d["id"] == app_id)
    assert our_app["is_liked"] is False

    # Check Detail endpoint
    detail_resp = await client.get(f"/apps/{app_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["is_liked"] is False

    # 2. Like the app
    like_resp = await client.post(f"/apps/{app_id}/like", headers=auth_headers)
    assert like_resp.status_code == 200

    # 3. Verify updated status (is_liked=True)
    # Check List endpoint
    list_resp_2 = await client.get("/apps/", headers=auth_headers)
    assert list_resp_2.status_code == 200
    apps_2 = list_resp_2.json()
    our_app_2 = next(d for d in apps_2 if d["id"] == app_id)
    assert our_app_2["is_liked"] is True

    # Check Detail endpoint
    detail_resp_2 = await client.get(f"/apps/{app_id}", headers=auth_headers)
    assert detail_resp_2.status_code == 200
    assert detail_resp_2.json()["is_liked"] is True

    # 4. Unlike the app
    unlike_resp = await client.delete(f"/apps/{app_id}/like", headers=auth_headers)
    assert unlike_resp.status_code == 200

    # 5. Verify reverted status (is_liked=False)
    detail_resp_3 = await client.get(f"/apps/{app_id}", headers=auth_headers)
    assert detail_resp_3.status_code == 200
    assert detail_resp_3.json()["is_liked"] is False
