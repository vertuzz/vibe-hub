from fastapi.testclient import TestClient

def test_vibe_lifecycle(client: TestClient, auth_headers: dict):
    # 1. Create tools and tags first (admin-like public for now)
    tool_resp = client.post("/tools/", json={"name": "Cursor"})
    tag_resp = client.post("/tags/", json={"name": "SaaS"})
    tool_id = tool_resp.json()["id"]
    tag_id = tag_resp.json()["id"]
    
    # 2. Create Vibe
    vibe_data = {
        "prompt_text": "A minimal todo app with neon colors",
        "prd_text": "Full PRD details here",
        "status": "Concept",
        "tool_ids": [tool_id],
        "tag_ids": [tag_id]
    }
    response = client.post("/vibes/", json=vibe_data, headers=auth_headers)
    assert response.status_code == 200
    vibe_id = response.json()["id"]
    assert response.json()["prompt_text"] == vibe_data["prompt_text"]
    
    # 3. Fork Vibe
    fork_resp = client.post(f"/vibes/{vibe_id}/fork", headers=auth_headers)
    assert fork_resp.status_code == 200
    assert fork_resp.json()["parent_vibe_id"] == vibe_id
    
    # 4. Social interaction (Comment & Review)
    comment_resp = client.post(f"/vibes/{vibe_id}/comments", json={"content": "Cool vibe!"}, headers=auth_headers)
    assert comment_resp.status_code == 200
    
    review_resp = client.post(f"/vibes/{vibe_id}/reviews", json={"score": 85.5, "comment": "Great prompt"}, headers=auth_headers)
    assert review_resp.status_code == 200
    
    # Check avg score
    avg_resp = client.get(f"/vibes/{vibe_id}/avg-score")
    assert avg_resp.json()["average_score"] == 85.5
    
    # 5. Like
    like_resp = client.post(f"/vibes/{vibe_id}/like", headers=auth_headers)
    assert like_resp.status_code == 200
    
    # 6. Implementation
    impl_data = {"url": "https://neon-todo.vercel.app", "description": "Built in 10 mins"}
    impl_resp = client.post(f"/vibes/{vibe_id}/implementations", json=impl_data, headers=auth_headers)
    assert impl_resp.status_code == 200
    impl_id = impl_resp.json()["id"]
    
    # Mark official
    client.patch(f"/implementations/{impl_id}/official", headers=auth_headers)
    
    # Final check: Feed
    feed_resp = client.get("/vibes/")
    assert len(feed_resp.json()) >= 1
