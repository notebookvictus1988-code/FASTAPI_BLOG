import pytest
from jose import jwt
from app.settings import settings
from app import schemas

# ─── LOGIN ────────────────────────────────────
def test_login(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# ─── TOKEN TEKSHIRISH ─────────────────────────
def test_login_token_valid(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    token = response.json()["access_token"]

    # Tokenni ochish va tekshirish
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )
    assert payload.get("user_id") == test_user["id"]

# ─── NOTO'G'RI PAROL ──────────────────────────
def test_login_wrong_password(client, test_user):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": "NOTO'G'RI_PAROL"
        }
    )
    assert response.status_code == 403

# ─── MAVJUD BO'LMAGAN USER ────────────────────
def test_login_wrong_email(client):
    response = client.post(
        "/login",
        data={
            "username": "yoq@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 403

# ─── TOKEN SHART ──────────────────────────────
def test_create_post_without_token(client):
    response = client.post(
        "/posts/",
        json={
            "title": "Test post",
            "content": "Kontent"
        }
    )
    assert response.status_code == 401