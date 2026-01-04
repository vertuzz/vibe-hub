import pytest
from httpx import AsyncClient
import asyncio
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_app_sorting_trending_newest_top_rated(client: AsyncClient, auth_headers: dict):
    # Setup: Create 3 apps with different characteristics
    
    # 1. Newest App (Created now, low engagement)
    resp = await client.post(
        "/apps/", 
        json={"prompt_text": "App 1: Newest"}, 
        headers=auth_headers
    )
    app1_id = resp.json()["id"]
    
    # Wait a bit to ensure time difference if needed, but we'll use engagement for others
    await asyncio.sleep(0.1)
    
    # 2. Top Rated App (Older, but high reviews)
    resp = await client.post(
        "/apps/", 
        json={"prompt_text": "App 2: Top Rated"}, 
        headers=auth_headers
    )
    app2_id = resp.json()["id"]
    
    # Add high score review to App 2
    await client.post(
        f"/apps/{app2_id}/reviews",
        json={"score": 5.0, "comment": "Perfect!"},
        headers=auth_headers
    )
    
    # 3. Trending App (Moderate age, high engagement - likes/comments)
    resp = await client.post(
        "/apps/", 
        json={"prompt_text": "App 3: Trending"}, 
        headers=auth_headers
    )
    app3_id = resp.json()["id"]
    
    # Add engagement to App 3
    # Like
    await client.post(f"/apps/{app3_id}/like", headers=auth_headers)
    # Comment
    await client.post(
        f"/apps/{app3_id}/comments",
        json={"content": "This is trending!"},
        headers=auth_headers
    )
    
    # --- TEST NEWEST ---
    # Should be 3, 2, 1 (since they were created in that order)
    resp = await client.get("/apps/?sort_by=newest")
    assert resp.status_code == 200
    apps = resp.json()
    assert apps[0]["id"] == app3_id
    assert apps[1]["id"] == app2_id
    assert apps[2]["id"] == app1_id
    
    # --- TEST TOP RATED ---
    # Should be 2 (avg 5.0), then 1 and 3 (avg 0.0)
    resp = await client.get("/apps/?sort_by=top_rated")
    assert resp.status_code == 200
    apps = resp.json()
    assert apps[0]["id"] == app2_id
    
    # --- TEST LIKES ---
    # Should be 3 (1 like), then others (0 likes)
    resp = await client.get("/apps/?sort_by=likes")
    assert resp.status_code == 200
    apps = resp.json()
    assert apps[0]["id"] == app3_id
    
    # --- TEST TRENDING (Default) ---
    # App 3 has 1 like + 1 comment (weighted as 2) = 3 engagement points.
    # Since they are all very new, App 3 should easily be top due to highest weighted engagement.
    resp = await client.get("/apps/?sort_by=trending")
    assert resp.status_code == 200
    apps = resp.json()
    assert apps[0]["id"] == app3_id

@pytest.mark.asyncio
async def test_app_sorting_empty_db(client: AsyncClient):
    resp = await client.get("/apps/?sort_by=trending")
    assert resp.status_code == 200
    assert resp.json() == []
    
    resp = await client.get("/apps/?sort_by=top_rated")
    assert resp.status_code == 200
    assert resp.json() == []
