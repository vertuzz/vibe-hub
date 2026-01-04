import pytest
from httpx import AsyncClient

async def get_auth_headers(client: AsyncClient, username: str):
    await client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "password123"
    })
    response = await client.post("/auth/login", data={
        "username": username,
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_create_app_with_ownership(client: AsyncClient, auth_headers: dict):
    # Test creating an app as owner
    app_data = {
        "title": "Owner App",
        "prompt_text": "An app I own",
        "is_owner": True
    }
    response = await client.post("/apps/", json=app_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_owner"] == True

    # Test creating an app as non-owner (submitter)
    app_data_2 = {
        "title": "Submitter App",
        "prompt_text": "An app I submitted for someone else",
        "is_owner": False
    }
    response = await client.post("/apps/", json=app_data_2, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_owner"] == False

@pytest.mark.asyncio
async def test_ownership_claim_lifecycle(client: AsyncClient, admin_headers: dict):
    # Setup: User A creates an app as non-owner
    headers_a = await get_auth_headers(client, "user_a")
    app_resp = await client.post("/apps/", json={
        "title": "Global App",
        "prompt_text": "Someone else's app",
        "is_owner": False
    }, headers=headers_a)
    app_id = app_resp.json()["id"]
    
    # User B claims ownership
    headers_b = await get_auth_headers(client, "user_b")
    claim_resp = await client.post(
        f"/apps/{app_id}/claim-ownership",
        json={"message": "I am the real dev. Check my site at userb.com"},
        headers=headers_b
    )
    assert claim_resp.status_code == 200
    claim_id = claim_resp.json()["id"]
    assert claim_resp.json()["status"] == "pending"

    # User B tries to claim again (should fail)
    claim_resp_again = await client.post(
        f"/apps/{app_id}/claim-ownership",
        json={"message": "Double claim"},
        headers=headers_b
    )
    assert claim_resp_again.status_code == 400

    # User A (creator) views claims
    claims_resp = await client.get(f"/apps/{app_id}/ownership-claims", headers=headers_a)
    assert claims_resp.status_code == 200
    assert len(claims_resp.json()) >= 1

    # Resolve claim (Approval) - only admin can do this now
    resolve_resp = await client.put(
        f"/ownership-claims/{claim_id}/resolve",
        params={"status": "approved"},
        headers=admin_headers
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "approved"

    # Verify app ownership transferred to User B
    app_final_resp = await client.get(f"/apps/{app_id}")
    app_data = app_final_resp.json()
    assert app_data["is_owner"] == True
    # We need to get User B's ID to verify creator_id
    user_b_resp = await client.get("/auth/me", headers=headers_b)
    user_b_id = user_b_resp.json()["id"]
    assert app_data["creator_id"] == user_b_id

@pytest.mark.asyncio
async def test_ownership_claim_rejection(client: AsyncClient, admin_headers: dict):
    # Setup: User A creates an app
    headers_a = await get_auth_headers(client, "user_reject_creator")
    app_resp = await client.post("/apps/", json={
        "title": "Rejected App",
        "prompt_text": "Test rejection",
        "is_owner": False
    }, headers=headers_a)
    app_id = app_resp.json()["id"]

    # User C claims ownership
    headers_c = await get_auth_headers(client, "user_c")
    claim_resp = await client.post(
        f"/apps/{app_id}/claim-ownership",
        json={"message": "I'm a fake"},
        headers=headers_c
    )
    claim_id = claim_resp.json()["id"]

    # Admin rejects claim
    resolve_resp = await client.put(
        f"/ownership-claims/{claim_id}/resolve",
        params={"status": "rejected"},
        headers=admin_headers
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "rejected"

    # Verify app ownership NOT transferred
    app_final_resp = await client.get(f"/apps/{app_id}")
    assert app_final_resp.json()["is_owner"] == False
    assert app_final_resp.json()["creator_id"] != (await client.get("/auth/me", headers=headers_c)).json()["id"]
