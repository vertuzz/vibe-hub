import pytest
from httpx import AsyncClient
from app.models import AppStatus

@pytest.mark.asyncio
async def test_status_filtering(client: AsyncClient, auth_headers: dict):
    # 1. Create a Concept app
    await client.post("/apps/", json={
        "title": "Concept App",
        "status": "Concept"
    }, headers=auth_headers)
    
    # 2. Create a Live app
    await client.post("/apps/", json={
        "title": "Live App",
        "status": "Live"
    }, headers=auth_headers)
    
    # 3. Filter by Concept
    resp = await client.get("/apps/", params={"status": "Concept"})
    assert resp.status_code == 200
    concepts = [d for d in resp.json() if d["title"] in ["Concept App", "Live App"]]
    assert len(concepts) >= 1
    assert all(d["status"] == "Concept" for d in concepts)
    
    # 4. Filter by Live
    resp = await client.get("/apps/", params={"status": "Live"})
    assert resp.status_code == 200
    lives = [d for d in resp.json() if d["title"] in ["Concept App", "Live App"]]
    assert len(lives) >= 1
    assert all(d["status"] == "Live" for d in lives)

@pytest.mark.asyncio
async def test_manual_status_update(client: AsyncClient, auth_headers: dict):
    # 1. Create app
    resp = await client.post("/apps/", json={
        "title": "Status Test",
        "status": "Concept"
    }, headers=auth_headers)
    app_id = resp.json()["id"]
    
    # 2. Update to WIP
    resp = await client.patch(f"/apps/{app_id}", json={"status": "WIP"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "WIP"
    
    # 3. Update to Live
    resp = await client.patch(f"/apps/{app_id}", json={"status": "Live"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "Live"
