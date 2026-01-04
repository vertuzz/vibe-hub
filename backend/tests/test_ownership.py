import pytest
from httpx import AsyncClient
from tests.conftest import create_test_user


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
async def test_ownership_claim_lifecycle(client: AsyncClient, db_session, admin_headers: dict):
    # Setup: User A creates an app as non-owner
    user_a, headers_a = await create_test_user(db_session, username="user_a", email="user_a@example.com")
    app_resp = await client.post("/apps/", json={
        "title": "Global App",
        "prompt_text": "Someone else's app",
        "is_owner": False
    }, headers=headers_a)
    app_id = app_resp.json()["id"]
    
    # User B claims ownership
    user_b, headers_b = await create_test_user(db_session, username="user_b", email="user_b@example.com")
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
    assert app_data["creator_id"] == user_b.id


@pytest.mark.asyncio
async def test_ownership_claim_rejection(client: AsyncClient, db_session, admin_headers: dict):
    # Setup: User A creates an app
    user_a, headers_a = await create_test_user(db_session, username="user_reject_creator", email="urc@example.com")
    app_resp = await client.post("/apps/", json={
        "title": "Rejected App",
        "prompt_text": "Test rejection",
        "is_owner": False
    }, headers=headers_a)
    app_id = app_resp.json()["id"]

    # User C claims ownership
    user_c, headers_c = await create_test_user(db_session, username="user_c", email="user_c@example.com")
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
    assert app_final_resp.json()["creator_id"] != user_c.id
