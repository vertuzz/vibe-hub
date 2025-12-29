import pytest
from httpx import AsyncClient
import asyncio
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_dream_sorting_trending_newest_top_rated(client: AsyncClient, auth_headers: dict):
    # Setup: Create 3 dreams with different characteristics
    
    # 1. Newest Dream (Created now, low engagement)
    resp = await client.post(
        "/dreams/", 
        json={"prompt_text": "Dream 1: Newest"}, 
        headers=auth_headers
    )
    dream1_id = resp.json()["id"]
    
    # Wait a bit to ensure time difference if needed, but we'll use engagement for others
    await asyncio.sleep(0.1)
    
    # 2. Top Rated Dream (Older, but high reviews)
    resp = await client.post(
        "/dreams/", 
        json={"prompt_text": "Dream 2: Top Rated"}, 
        headers=auth_headers
    )
    dream2_id = resp.json()["id"]
    
    # Add high score review to Dream 2
    await client.post(
        f"/dreams/{dream2_id}/reviews",
        json={"score": 5.0, "comment": "Perfect!"},
        headers=auth_headers
    )
    
    # 3. Trending Dream (Moderate age, high engagement - likes/comments)
    resp = await client.post(
        "/dreams/", 
        json={"prompt_text": "Dream 3: Trending"}, 
        headers=auth_headers
    )
    dream3_id = resp.json()["id"]
    
    # Add engagement to Dream 3
    # Like
    await client.post(f"/dreams/{dream3_id}/like", headers=auth_headers)
    # Comment
    await client.post(
        f"/dreams/{dream3_id}/comments",
        json={"content": "This is trending!"},
        headers=auth_headers
    )
    
    # --- TEST NEWEST ---
    # Should be 3, 2, 1 (since they were created in that order)
    resp = await client.get("/dreams/?sort_by=newest")
    assert resp.status_code == 200
    dreams = resp.json()
    assert dreams[0]["id"] == dream3_id
    assert dreams[1]["id"] == dream2_id
    assert dreams[2]["id"] == dream1_id
    
    # --- TEST TOP RATED ---
    # Should be 2 (avg 5.0), then 1 and 3 (avg 0.0)
    resp = await client.get("/dreams/?sort_by=top_rated")
    assert resp.status_code == 200
    dreams = resp.json()
    assert dreams[0]["id"] == dream2_id
    
    # --- TEST LIKES ---
    # Should be 3 (1 like), then others (0 likes)
    resp = await client.get("/dreams/?sort_by=likes")
    assert resp.status_code == 200
    dreams = resp.json()
    assert dreams[0]["id"] == dream3_id
    
    # --- TEST TRENDING (Default) ---
    # Dream 3 has 1 like + 1 comment (weighted as 2) = 3 engagement points.
    # Since they are all very new, Dream 3 should easily be top due to highest weighted engagement.
    resp = await client.get("/dreams/?sort_by=trending")
    assert resp.status_code == 200
    dreams = resp.json()
    assert dreams[0]["id"] == dream3_id

@pytest.mark.asyncio
async def test_dream_sorting_empty_db(client: AsyncClient):
    resp = await client.get("/dreams/?sort_by=trending")
    assert resp.status_code == 200
    assert resp.json() == []
    
    resp = await client.get("/dreams/?sort_by=top_rated")
    assert resp.status_code == 200
    assert resp.json() == []
