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
async def test_comment_voting(client: AsyncClient, auth_headers: dict):
    # Setup: Create a dream and a comment
    dream_resp = await client.post(
        "/dreams/", 
        json={"prompt_text": "Test Dream for Comment Voting"}, 
        headers=auth_headers
    )
    dream_id = dream_resp.json()["id"]
    
    comment_resp = await client.post(
        f"/dreams/{dream_id}/comments", 
        json={"content": "Test Comment"}, 
        headers=auth_headers
    )
    comment_id = comment_resp.json()["id"]
    assert comment_resp.json()["score"] == 0

    # 1. Upvote
    resp = await client.post(f"/comments/{comment_id}/vote?value=1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["score"] == 1

    # Verify score
    dream_comments = await client.get(f"/dreams/{dream_id}/comments", headers=auth_headers)
    comment = next(c for c in dream_comments.json() if c["id"] == comment_id)
    assert comment["score"] == 1
    assert comment["user_vote"] == 1

    # 2. Downvote (flip vote)
    resp = await client.post(f"/comments/{comment_id}/vote?value=-1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["score"] == -1

    # Verify score
    dream_comments = await client.get(f"/dreams/{dream_id}/comments", headers=auth_headers)
    comment = next(c for c in dream_comments.json() if c["id"] == comment_id)
    assert comment["score"] == -1
    assert comment["user_vote"] == -1

    # 3. Remove vote (value=0)
    resp = await client.post(f"/comments/{comment_id}/vote?value=0", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["score"] == 0

    # Verify score
    dream_comments = await client.get(f"/dreams/{dream_id}/comments", headers=auth_headers)
    comment = next(c for c in dream_comments.json() if c["id"] == comment_id)
    assert comment["score"] == 0
    assert comment["user_vote"] == 0
