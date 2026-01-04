import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_access_required_for_tags(client: AsyncClient, auth_headers: dict):
    # Test non-admin cannot create tag
    response = await client.post("/tags/", json={"name": "NewTag"}, headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

@pytest.mark.asyncio
async def test_admin_can_create_tags(client: AsyncClient, admin_headers: dict):
    # Test admin can create tag
    response = await client.post("/tags/", json={"name": "AdminTag"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "AdminTag"

@pytest.mark.asyncio
async def test_admin_access_required_for_tools(client: AsyncClient, auth_headers: dict):
    # Test non-admin cannot create tool
    response = await client.post("/tools/", json={"name": "NewTool"}, headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

@pytest.mark.asyncio
async def test_admin_can_create_tools(client: AsyncClient, admin_headers: dict):
    # Test admin can create tool
    response = await client.post("/tools/", json={"name": "AdminTool"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "AdminTool"

@pytest.mark.asyncio
async def test_admin_can_view_all_pending_claims(client: AsyncClient, admin_headers: dict, auth_headers: dict):
    # 1. Create an app and a claim
    app_resp = await client.post("/apps/", json={
        "title": "Claim App",
        "prompt_text": "Test claim",
        "is_owner": False
    }, headers=auth_headers)
    app_id = app_resp.json()["id"]
    
    await client.post(
        f"/apps/{app_id}/claim-ownership",
        json={"message": "I claim this"},
        headers=auth_headers # reusing auth_headers for simplicity
    )
    
    # 2. Try to view all claims as non-admin
    response = await client.get("/ownership-claims", headers=auth_headers)
    assert response.status_code == 403
    
    # 3. View all claims as admin
    admin_resp = await client.get("/ownership-claims", headers=admin_headers)
    assert admin_resp.status_code == 200
    claims = admin_resp.json()
    assert len(claims) >= 1
    assert any(c["app_id"] == app_id for c in claims)

@pytest.mark.asyncio
async def test_admin_can_resolve_any_claim(client: AsyncClient, admin_headers: dict, auth_headers: dict):
    # 1. Setup claim
    app_resp = await client.post("/apps/", json={
        "title": "Resolve App",
        "prompt_text": "Test resolve",
        "is_owner": False
    }, headers=auth_headers)
    app_id = app_resp.json()["id"]
    
    claim_resp = await client.post(
        f"/apps/{app_id}/claim-ownership",
        json={"message": "I claim this"},
        headers=auth_headers
    )
    claim_id = claim_resp.json()["id"]
    
    # 2. Try to resolve as non-admin
    response = await client.put(
        f"/ownership-claims/{claim_id}/resolve",
        params={"status": "approved"},
        headers=auth_headers
    )
    assert response.status_code == 403
    
    # 3. Resolve as admin
    admin_resp = await client.put(
        f"/ownership-claims/{claim_id}/resolve",
        params={"status": "approved"},
        headers=admin_headers
    )
    assert admin_resp.status_code == 200
    assert admin_resp.json()["status"] == "approved"
