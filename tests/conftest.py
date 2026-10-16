import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models

# ─── TEST DATABASE (SQLite — xotirada) ────────
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"
# "sqlite://" = xotirada, fayl yaratmaydi

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ─── FIXTURE: Database ────────────────────────
@pytest.fixture()
def db():
    # Jadvallarni yaratish
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Har test keyin jadvallarni tozalash
        Base.metadata.drop_all(bind=engine)

# ─── FIXTURE: TestClient ──────────────────────
@pytest.fixture()
def client(db):
    # get_db ni test DB bilan almashtirish
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# ─── FIXTURE: Test User ───────────────────────
@pytest.fixture()
def test_user(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    new_user = response.json()
    new_user["password"] = "password123"  # Testda kerak
    return new_user

# ─── FIXTURE: Token ───────────────────────────
@pytest.fixture()
def token(test_user, client):
    response = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

# ─── FIXTURE: Authorized Client ───────────────
@pytest.fixture()
def authorized_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

# ─── FIXTURE: Test Posts ──────────────────────
@pytest.fixture()
def test_posts(test_user, db):
    posts_data = [
        {
            "title": "Birinchi post",
            "content": "Birinchi kontent",
            "published": True,
            "owner_id": test_user["id"]
        },
        {
            "title": "Ikkinchi post",
            "content": "Ikkinchi kontent",
            "published": True,
            "owner_id": test_user["id"]
        },
        {
            "title": "Uchinchi post",
            "content": "Uchinchi kontent",
            "published": False,
            "owner_id": test_user["id"]
        },
    ]

    posts = [models.Post(**p) for p in posts_data]
    db.add_all(posts)
    db.commit()

    return db.query(models.Post).all()