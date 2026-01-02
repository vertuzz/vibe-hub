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
async def test_create_dream_with_ownership(client: AsyncClient, auth_headers: dict):
    # Test creating a dream as owner
    dream_data = {
        "title": "Owner Dream",
        "prompt_text": "A dream I own",
        "is_owner": True
    }
    response = await client.post("/dreams/", json=dream_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_owner"] == True

    # Test creating a dream as non-owner (submitter)
    dream_data_2 = {
        "title": "Submitter Dream",
        "prompt_text": "A dream I submitted for someone else",
        "is_owner": False
    }
    response = await client.post("/dreams/", json=dream_data_2, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_owner"] == False

@pytest.mark.asyncio
async def test_ownership_claim_lifecycle(client: AsyncClient):
    # Setup: User A creates a dream as non-owner
    headers_a = await get_auth_headers(client, "user_a")
    dream_resp = await client.post("/dreams/", json={
        "title": "Global App",
        "prompt_text": "Someone else's app",
        "is_owner": False
    }, headers=headers_a)
    dream_id = dream_resp.json()["id"]
    
    # User B claims ownership
    headers_b = await get_auth_headers(client, "user_b")
    claim_resp = await client.post(
        f"/dreams/{dream_id}/claim-ownership",
        json={"message": "I am the real dev. Check my site at userb.com"},
        headers=headers_b
    )
    assert claim_resp.status_code == 200
    claim_id = claim_resp.json()["id"]
    assert claim_resp.json()["status"] == "pending"

    # User B tries to claim again (should fail)
    claim_resp_again = await client.post(
        f"/dreams/{dream_id}/claim-ownership",
        json={"message": "Double claim"},
        headers=headers_b
    )
    assert claim_resp_again.status_code == 400

    # User A (creator) views claims
    claims_resp = await client.get(f"/dreams/{dream_id}/ownership-claims", headers=headers_a)
    assert claims_resp.status_code == 200
    assert len(claims_resp.json()) >= 1

    # Resolve claim (Approval)
    # Note: In our current impl, anyone logged in can resolve if we don't have admin check.
    # We should ideally test that the ownership transfers.
    resolve_resp = await client.put(
        f"/ownership-claims/{claim_id}/resolve",
        params={"status": "approved"},
        headers=headers_a
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "approved"

    # Verify dream ownership transferred to User B
    dream_final_resp = await client.get(f"/dreams/{dream_id}")
    dream_data = dream_final_resp.json()
    assert dream_data["is_owner"] == True
    # We need to get User B's ID to verify creator_id
    user_b_resp = await client.get("/auth/me", headers=headers_b)
    user_b_id = user_b_resp.json()["id"]
    assert dream_data["creator_id"] == user_b_id

@pytest.mark.asyncio
async def test_ownership_claim_rejection(client: AsyncClient):
    # Setup: User A creates a dream
    headers_a = await get_auth_headers(client, "user_reject_creator")
    dream_resp = await client.post("/dreams/", json={
        "title": "Rejected App",
        "prompt_text": "Test rejection",
        "is_owner": False
    }, headers=headers_a)
    dream_id = dream_resp.json()["id"]

    # User C claims ownership
    headers_c = await get_auth_headers(client, "user_c")
    claim_resp = await client.post(
        f"/dreams/{dream_id}/claim-ownership",
        json={"message": "I'm a fake"},
        headers=headers_c
    )
    claim_id = claim_resp.json()["id"]

    # User A rejects claim
    resolve_resp = await client.put(
        f"/ownership-claims/{claim_id}/resolve",
        params={"status": "rejected"},
        headers=headers_a
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "rejected"

    # Verify dream ownership NOT transferred
    dream_final_resp = await client.get(f"/dreams/{dream_id}")
    assert dream_final_resp.json()["is_owner"] == False
    assert dream_final_resp.json()["creator_id"] != (await client.get("/auth/me", headers=headers_c)).json()["id"]
