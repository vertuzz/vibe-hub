import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_dream_like_unlike(client: AsyncClient, auth_headers: dict):
    # Setup: Create a dream
    dream_resp = await client.post(
        "/dreams/", 
        json={"prompt_text": "Test Dream for Liking"}, 
        headers=auth_headers
    )
    dream_id = dream_resp.json()["id"]

    # 1. Like
    resp = await client.post(f"/dreams/{dream_id}/like", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Liked"

    # 2. Like again (failure)
    resp = await client.post(f"/dreams/{dream_id}/like", headers=auth_headers)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Already liked"

    # 3. Unlike
    resp = await client.delete(f"/dreams/{dream_id}/like", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Unliked"

    # 4. Unlike again (failure)
    resp = await client.delete(f"/dreams/{dream_id}/like", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Like not found"

@pytest.mark.asyncio
async def test_comment_like_unlike(client: AsyncClient, auth_headers: dict):
    # Setup: Create a dream and a comment
    dream_resp = await client.post(
        "/dreams/", 
        json={"prompt_text": "Test Dream for Comment Like"}, 
        headers=auth_headers
    )
    dream_id = dream_resp.json()["id"]
    
    comment_resp = await client.post(
        f"/dreams/{dream_id}/comments", 
        json={"content": "Test Comment"}, 
        headers=auth_headers
    )
    comment_id = comment_resp.json()["id"]
    assert comment_resp.json()["likes_count"] == 0

    # 1. Like comment
    resp = await client.post(f"/comments/{comment_id}/like", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Liked"

    # Verify counter cache
    dream_comments = await client.get(f"/dreams/{dream_id}/comments")
    comment = next(c for c in dream_comments.json() if c["id"] == comment_id)
    assert comment["likes_count"] == 1

    # 2. Like again (failure)
    resp = await client.post(f"/comments/{comment_id}/like", headers=auth_headers)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Already liked"

    # 3. Unlike comment
    resp = await client.delete(f"/comments/{comment_id}/like", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Unliked"

    # Verify counter cache
    dream_comments = await client.get(f"/dreams/{dream_id}/comments")
    comment = next(c for c in dream_comments.json() if c["id"] == comment_id)
    assert comment["likes_count"] == 0

    # 4. Unlike again (failure)
    resp = await client.delete(f"/comments/{comment_id}/like", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Like not found"
