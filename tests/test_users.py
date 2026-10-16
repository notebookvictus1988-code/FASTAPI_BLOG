import pytest
from jose import jwt
from app.settings import settings

# ─── FOYDALANUVCHI YARATISH ───────────────────
def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "username": "ali",
            "email": "ali@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "ali@example.com"
    assert data["username"] == "ali"
    assert "password" not in data    # Parol ko'rinmasin!
    assert "id" in data
    assert "created_at" in data

# ─── TAKRORIY EMAIL ───────────────────────────
def test_create_user_duplicate_email(client):
    # Birinchi user
    client.post(
        "/users/",
        json={
            "username": "ali",
            "email": "ali@example.com",
            "password": "password123"
        }
    )

    # Xuddi shu email bilan yana
    response = client.post(
        "/users/",
        json={
            "username": "vali",
            "email": "ali@example.com",   # Takror!
            "password": "password456"
        }
    )
    assert response.status_code == 400
    assert "allaqachon" in response.json()["detail"]

# ─── NOTO'G'RI MA'LUMOT ───────────────────────
def test_create_user_invalid_email(client):
    response = client.post(
        "/users/",
        json={
            "username": "ali",
            "email": "bu-email-emas",    # Noto'g'ri email
            "password": "password123"
        }
    )
    assert response.status_code == 422   # Validation error

# ─── FOYDALANUVCHINI OLISH ────────────────────
def test_get_user(client, test_user):
    response = client.get(f"/users/{test_user['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]

# ─── MAVJUD BO'LMAGAN USER ────────────────────
def test_get_user_not_found(client):
    response = client.get("/users/99999")
    assert response.status_code == 404