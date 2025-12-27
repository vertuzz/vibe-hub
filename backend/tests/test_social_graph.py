from fastapi.testclient import TestClient

def test_social_graph_and_notifications(client: TestClient):
    # 1. Register User A and User B
    client.post("/auth/register", json={"username": "userA", "email": "a@e.com", "password": "p"})
    client.post("/auth/register", json={"username": "userB", "email": "b@e.com", "password": "p"})
    
    # Login as User A
    respA = client.post("/auth/login", data={"username": "userA", "password": "p"})
    tokenA = respA.json()["access_token"]
    headersA = {"Authorization": f"Bearer {tokenA}"}
    
    # Login as User B
    respB = client.post("/auth/login", data={"username": "userB", "password": "p"})
    tokenB = respB.json()["access_token"]
    headersB = {"Authorization": f"Bearer {tokenB}"}
    idB = client.get("/auth/me", headers=headersB).json()["id"]
    
    # 2. User A follows User B
    follow_resp = client.post(f"/users/{idB}/follow", headers=headersA)
    assert follow_resp.status_code == 200
    
    # 3. User B creates a vibe (optional for this specific test)
    vibe_resp = client.post("/vibes/", json={"prompt_text": "vibe"}, headers=headersB)
    vibe_id = vibe_resp.json()["id"]
    
    # 4. User A likes User B's vibe -> should trigger notification
    client.post(f"/vibes/{vibe_id}/like", headers=headersA)
    
    # 5. User B checks notifications
    notif_resp = client.get("/notifications/", headers=headersB)
    assert len(notif_resp.json()) >= 1
    assert "liked your vibe" in notif_resp.json()[0]["content"]
    
    # Mark read
    notif_id = notif_resp.json()[0]["id"]
    client.patch(f"/notifications/{notif_id}/read", headers=headersB)
    
    # 6. User A unfollows User B
    unfollow_resp = client.delete(f"/users/{idB}/follow", headers=headersA)
    assert unfollow_resp.status_code == 200
