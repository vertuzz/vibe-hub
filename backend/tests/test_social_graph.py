import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_social_graph_and_notifications(client: AsyncClient):
    # 1. Register User A and User B
    await client.post("/auth/register", json={"username": "userA", "email": "a@e.com", "password": "p"})
    await client.post("/auth/register", json={"username": "userB", "email": "b@e.com", "password": "p"})
    
    # Login as User A
    respA = await client.post("/auth/login", data={"username": "userA", "password": "p"})
    tokenA = respA.json()["access_token"]
    headersA = {"Authorization": f"Bearer {tokenA}"}
    
    # Login as User B
    respB = await client.post("/auth/login", data={"username": "userB", "password": "p"})
    tokenB = respB.json()["access_token"]
    headersB = {"Authorization": f"Bearer {tokenB}"}
    respB_me = await client.get("/auth/me", headers=headersB)
    idB = respB_me.json()["id"]
    
    # 2. User A follows User B
    follow_resp = await client.post(f"/users/{idB}/follow", headers=headersA)
    assert follow_resp.status_code == 200
    
    # 3. User B creates an app (optional for this specific test)
    app_resp = await client.post("/apps/", json={"prompt_text": "app"}, headers=headersB)
    app_id = app_resp.json()["id"]
    
    # 4. User A likes User B's app -> should trigger notification
    await client.post(f"/apps/{app_id}/like", headers= headersA)
    
    # 5. User B checks notifications
    notif_resp = await client.get("/notifications/", headers=headersB)
    notifications = notif_resp.json()
    assert len(notifications) >= 2  # Should have both follow and like notifications
    
    # Find the like notification
    like_notif = None
    for notif in notifications:
        if "liked your app" in notif["content"]:
            like_notif = notif
            break
    
    assert like_notif is not None, "Should have a like notification"
    
    # Mark read
    notif_id = like_notif["id"]
    await client.patch(f"/notifications/{notif_id}/read", headers= headersB)
    
    # 6. User A unfollows User B
    unfollow_resp = await client.delete(f"/users/{idB}/follow", headers=headersA)
    assert unfollow_resp.status_code == 200
