"""
Tests for Dream likes_count, comments_count, and creator fields.
These tests verify the computed fields added to the Dream response schema.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dream_response_includes_creator(client: AsyncClient, auth_headers: dict):
    """Test that dream response includes creator information."""
    # Create a dream
    dream_resp = await client.post(
        "/dreams/",
        json={"title": "Test Dream", "prompt_text": "A test dream"},
        headers=auth_headers
    )
    assert dream_resp.status_code == 200
    dream = dream_resp.json()
    
    # Verify creator is included
    assert "creator" in dream
    assert dream["creator"] is not None
    assert dream["creator"]["username"] == "testuser"
    assert "id" in dream["creator"]
    # Ensure sensitive fields are not exposed
    assert "email" not in dream["creator"]
    assert "password" not in dream["creator"]


@pytest.mark.asyncio
async def test_dream_response_includes_zero_counts_on_create(client: AsyncClient, auth_headers: dict):
    """Test that newly created dreams have zero counts."""
    dream_resp = await client.post(
        "/dreams/",
        json={"title": "Fresh Dream", "prompt_text": "Brand new"},
        headers=auth_headers
    )
    assert dream_resp.status_code == 200
    dream = dream_resp.json()
    
    assert dream["likes_count"] == 0
    assert dream["comments_count"] == 0


@pytest.mark.asyncio
async def test_dream_likes_count_updates(client: AsyncClient, auth_headers: dict):
    """Test that likes_count updates when a dream is liked."""
    # Create dream
    dream_resp = await client.post(
        "/dreams/",
        json={"title": "Likeable Dream", "prompt_text": "Like me!"},
        headers=auth_headers
    )
    dream_id = dream_resp.json()["id"]
    
    # Verify initial count
    get_resp = await client.get(f"/dreams/{dream_id}")
    assert get_resp.json()["likes_count"] == 0
    
    # Like the dream
    like_resp = await client.post(f"/dreams/{dream_id}/like", headers=auth_headers)
    assert like_resp.status_code == 200
    
    # Verify count updated
    get_resp = await client.get(f"/dreams/{dream_id}")
    assert get_resp.json()["likes_count"] == 1
    
    # Unlike the dream
    unlike_resp = await client.delete(f"/dreams/{dream_id}/like", headers=auth_headers)
    assert unlike_resp.status_code == 200
    
    # Verify count decreased
    get_resp = await client.get(f"/dreams/{dream_id}")
    assert get_resp.json()["likes_count"] == 0


@pytest.mark.asyncio
async def test_dream_comments_count_updates(client: AsyncClient, auth_headers: dict):
    """Test that comments_count updates when comments are added."""
    # Create dream
    dream_resp = await client.post(
        "/dreams/",
        json={"title": "Commentable Dream", "prompt_text": "Comment on me!"},
        headers=auth_headers
    )
    dream_id = dream_resp.json()["id"]
    
    # Verify initial count
    get_resp = await client.get(f"/dreams/{dream_id}")
    assert get_resp.json()["comments_count"] == 0
    
    # Add first comment
    await client.post(
        f"/dreams/{dream_id}/comments",
        json={"content": "First comment"},
        headers=auth_headers
    )
    
    # Verify count is 1
    get_resp = await client.get(f"/dreams/{dream_id}")
    assert get_resp.json()["comments_count"] == 1
    
    # Add second comment
    await client.post(
        f"/dreams/{dream_id}/comments",
        json={"content": "Second comment"},
        headers=auth_headers
    )
    
    # Verify count is 2
    get_resp = await client.get(f"/dreams/{dream_id}")
    assert get_resp.json()["comments_count"] == 2


@pytest.mark.asyncio
async def test_dreams_list_includes_counts_and_creator(client: AsyncClient, auth_headers: dict):
    """Test that dreams list endpoint includes counts and creator for each dream."""
    # Create a dream
    dream_resp = await client.post(
        "/dreams/",
        json={"title": "Listed Dream", "prompt_text": "In the list"},
        headers=auth_headers
    )
    dream_id = dream_resp.json()["id"]
    
    # Add a like and comment
    await client.post(f"/dreams/{dream_id}/like", headers=auth_headers)
    await client.post(
        f"/dreams/{dream_id}/comments",
        json={"content": "A comment"},
        headers=auth_headers
    )
    
    # Get dreams list
    list_resp = await client.get("/dreams/")
    assert list_resp.status_code == 200
    dreams = list_resp.json()
    
    # Find our dream
    our_dream = next((d for d in dreams if d["id"] == dream_id), None)
    assert our_dream is not None
    
    # Verify counts and creator
    assert our_dream["likes_count"] == 1
    assert our_dream["comments_count"] == 1
    assert our_dream["creator"] is not None
    assert our_dream["creator"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_dream_update_preserves_counts(client: AsyncClient, auth_headers: dict):
    """Test that updating a dream returns correct counts."""
    # Create dream
    dream_resp = await client.post(
        "/dreams/",
        json={"title": "Updatable Dream", "prompt_text": "Update me!"},
        headers=auth_headers
    )
    dream_id = dream_resp.json()["id"]
    
    # Add likes and comments
    await client.post(f"/dreams/{dream_id}/like", headers=auth_headers)
    await client.post(
        f"/dreams/{dream_id}/comments",
        json={"content": "Comment before update"},
        headers=auth_headers
    )
    
    # Update the dream
    update_resp = await client.patch(
        f"/dreams/{dream_id}",
        json={"title": "Updated Dream Title"},
        headers=auth_headers
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    
    # Verify counts are preserved in response
    assert updated["likes_count"] == 1
    assert updated["comments_count"] == 1
    assert updated["title"] == "Updated Dream Title"
    assert updated["creator"] is not None


@pytest.mark.asyncio
async def test_dream_fork_has_zero_counts(client: AsyncClient, auth_headers: dict):
    """Test that forked dreams start with zero counts."""
    # Create original dream with likes/comments
    dream_resp = await client.post(
        "/dreams/",
        json={"title": "Original Dream", "prompt_text": "Fork me!"},
        headers=auth_headers
    )
    dream_id = dream_resp.json()["id"]
    
    # Add likes and comments to original
    await client.post(f"/dreams/{dream_id}/like", headers=auth_headers)
    await client.post(
        f"/dreams/{dream_id}/comments",
        json={"content": "Original comment"},
        headers=auth_headers
    )
    
    # Fork the dream
    fork_resp = await client.post(f"/dreams/{dream_id}/fork", headers=auth_headers)
    assert fork_resp.status_code == 200
    forked = fork_resp.json()
    
    # Verify forked dream has zero counts (not inherited)
    assert forked["likes_count"] == 0
    assert forked["comments_count"] == 0
    assert forked["parent_dream_id"] == dream_id
    assert forked["creator"] is not None


@pytest.mark.asyncio
async def test_dream_creator_avatar_included(client: AsyncClient, auth_headers: dict):
    """Test that creator avatar field is included (even if None)."""
    dream_resp = await client.post(
        "/dreams/",
        json={"title": "Avatar Test", "prompt_text": "Check avatar"},
        headers=auth_headers
    )
    dream = dream_resp.json()
    
    # Avatar should be in creator object (may be None)
    assert "avatar" in dream["creator"]


@pytest.mark.asyncio
async def test_multiple_dreams_batch_counts(client: AsyncClient, auth_headers: dict):
    """Test that batch count queries work correctly for multiple dreams."""
    dream_ids = []
    
    # Create multiple dreams
    for i in range(3):
        resp = await client.post(
            "/dreams/",
            json={"title": f"Dream {i}", "prompt_text": f"Content {i}"},
            headers=auth_headers
        )
        dream_ids.append(resp.json()["id"])
    
    # Add varying likes to each dream
    # Dream 0: 0 likes, Dream 1: 1 like, Dream 2: 1 like
    await client.post(f"/dreams/{dream_ids[1]}/like", headers=auth_headers)
    
    # We need another user to like dream 2 since same user can't like twice
    # For simplicity, just add a comment to dream 2 instead
    await client.post(
        f"/dreams/{dream_ids[2]}/comments",
        json={"content": "Comment on dream 2"},
        headers=auth_headers
    )
    
    # Get all dreams
    list_resp = await client.get("/dreams/")
    dreams = list_resp.json()
    
    # Verify counts are correct for each
    dream_map = {d["id"]: d for d in dreams}
    
    assert dream_map[dream_ids[0]]["likes_count"] == 0
    assert dream_map[dream_ids[0]]["comments_count"] == 0
    
    assert dream_map[dream_ids[1]]["likes_count"] == 1
    assert dream_map[dream_ids[1]]["comments_count"] == 0
    
    assert dream_map[dream_ids[2]]["likes_count"] == 0
    assert dream_map[dream_ids[2]]["comments_count"] == 1
