import pytest
from httpx import AsyncClient
from tests.conftest import create_test_user


@pytest.mark.asyncio
async def test_follow_notification(client: AsyncClient, db_session):
    # Create User 1 and User 2 directly in DB
    user1, headers1 = await create_test_user(db_session, username="notif_u1", email="notif_u1@e.com")
    user2, headers2 = await create_test_user(db_session, username="notif_u2", email="notif_u2@e.com")

    # User 1 follows User 2
    response = await client.post(
        f"/users/{user2.id}/follow",
        headers=headers1
    )
    assert response.status_code == 200

    # User 2 checks notifications
    response = await client.get(
        "/notifications/",
        headers=headers2
    )
    assert response.status_code == 200
    notifications = response.json()
    assert len(notifications) > 0
    assert notifications[0]["content"] == "notif_u1 followed you"
    assert notifications[0]["type"] == "FOLLOW"

    # Mark as read
    notif_id = notifications[0]["id"]
    response = await client.patch(
        f"/notifications/{notif_id}/read",
        headers=headers2
    )
    assert response.status_code == 200
    assert response.json()["is_read"] == True
