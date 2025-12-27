from fastapi.testclient import TestClient

def test_register_and_login(client: TestClient):
    # Register
    user_data = {"username": "newuser", "email": "new@example.com", "password": "securepassword"}
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    
    # Login
    login_response = client.post("/auth/login", data={"username": "newuser", "password": "securepassword"})
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    
    # Get Me
    token = login_response.json()["access_token"]
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "newuser"

def test_login_invalid_password(client: TestClient):
    # Register first
    client.post("/auth/register", json={"username": "failuser", "email": "fail@example.com", "password": "correct"})
    
    # Login fail
    response = client.post("/auth/login", data={"username": "failuser", "password": "wrong"})
    assert response.status_code == 401
