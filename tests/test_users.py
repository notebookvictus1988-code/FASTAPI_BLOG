import pytest
from jose import jwt
from app.settings import settings


# ─── 1. FOYDALANUVCHI YARATISH ───────────────────
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


# ─── 2. TAKRORIY EMAIL ───────────────────────────
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


# ─── 3. NOTO'G'RI MA'LUMOT ───────────────────────
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


# ─── 4. FOYDALANUVCHINI OLISH (ID bo'yicha) ─────
def test_get_user(client, test_user):
    response = client.get(f"/users/{test_user['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]


# ─── 5. MAVJUD BO'LMAGAN USER ────────────────────
def test_get_user_not_found(client):
    response = client.get("/users/99999")
    assert response.status_code == 404


# ─── 6. ME ENDPOINT TESTLARI (Yangi qo'shildi) ────
def test_get_current_user(authorized_client, test_user):
    response = authorized_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]


def test_get_current_user_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == 401


# ─── 7. PAROL O'ZGARTIRISH TESTI (Yangi qo'shildi) ─
def test_change_password(authorized_client, test_user):
    response = authorized_client.put(
        "/users/me/password",
        json={
            "old_password": test_user["password"],
            "new_password": "yangi_parol_123"
        }
    )
    assert response.status_code == 200


# ─── 8. LOGIN TESTI (Yangi qo'shildi) ─────────────
@pytest.mark.parametrize("email, password, status_code", [
    ("test@example.com", "password123", 200),      # To'g'ri login
    ("test@example.com", "NOTO'G'RI", 403),        # Noto'g'ri parol
    ("yoq@example.com", "password123", 403),       # Email bazada yo'q
    ("test@example.com", "", 422),                 # Bo'sh parol (validation error)
])
def test_login_cases(client, test_user, email, password, status_code):
    response = client.post(
        "/login",
        data={"username": email, "password": password}
    )
    assert response.status_code == status_code