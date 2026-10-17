import pytest
from app import schemas

# ─── BARCHA POSTLAR ───────────────────────────
def test_get_all_posts(client, test_posts):
    response = client.get("/posts/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(test_posts)

# ─── BITTA POST ───────────────────────────────
def test_get_post(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_posts[0].id
    assert data["title"] == test_posts[0].title

# ─── MAVJUD BO'LMAGAN POST ────────────────────
def test_get_post_not_found(client):
    response = client.get("/posts/99999")
    assert response.status_code == 404

# ─── POST YARATISH (token bilan) ──────────────
def test_create_post(authorized_client):
    response = authorized_client.post(
        "/posts/",
        json={
            "title": "Yangi post",
            "content": "Yangi kontent",
            "published": True
        }
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Yangi post"
    assert data["content"] == "Yangi kontent"
    assert data["published"] == True
    assert "id" in data
    assert "owner_id" in data

# ─── POST YARATISH (token YO'Q) ───────────────
def test_create_post_unauthorized(client):
    response = client.post(
        "/posts/",
        json={
            "title": "Post",
            "content": "Kontent"
        }
    )
    assert response.status_code == 401

# ─── DEFAULT PUBLISHED = TRUE ─────────────────
def test_create_post_default_published(authorized_client):
    response = authorized_client.post(
        "/posts/",
        json={
            "title": "Post",
            "content": "Kontent"
            # published yuborilmagan!
        }
    )
    assert response.status_code == 201
    assert response.json()["published"] == True

# ─── POST YANGILASH ───────────────────────────
def test_update_post(authorized_client, test_posts):
    response = authorized_client.put(
        f"/posts/{test_posts[0].id}",
        json={
            "title": "Yangilangan sarlavha",
            "content": "Yangilangan kontent",
            "published": True
        }
    )
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Yangilangan sarlavha"
    assert data["content"] == "Yangilangan kontent"

# ─── BOSHQANING POSTINI YANGILASH ─────────────
def test_update_other_user_post(authorized_client, db):
    from app import models
    from app.utils.hashing import hash_password

    # Ikkinchi user yaratish
    other_user = models.User(
        username="other",
        email="other@example.com",
        password=hash_password("password123")
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    # Ikkinchi userning posti
    other_post = models.Post(
        title="Boshqaning posti",
        content="Kontent",
        owner_id=other_user.id
    )
    db.add(other_post)
    db.commit()
    db.refresh(other_post)

    # Birinchi user boshqaning postini yangilashga urinadi
    response = authorized_client.put(
        f"/posts/{other_post.id}",
        json={
            "title": "O'g'irlashga urindim",
            "content": "Kontent",
            "published": True
        }
    )
    assert response.status_code == 403

# ─── POST O'CHIRISH ───────────────────────────
def test_delete_post(authorized_client, test_posts):
    response = authorized_client.delete(
        f"/posts/{test_posts[0].id}"
    )
    assert response.status_code == 204

# ─── O'CHIRILGAN POSTNI TEKSHIRISH ────────────
def test_delete_post_check(authorized_client, test_posts):
    # Сначала сохраняем ID в обычную переменную Python, чтобы SQLAlchemy не делала лишний запрос
    post_id = test_posts[0].id
    
    # Удаляем пост
    authorized_client.delete(f"/posts/{post_id}")
    
    # Пытаемся получить удаленный пост по сохраненному ID
    response = authorized_client.get(f"/posts/{post_id}")
    assert response.status_code == 404

# ─── MAVJUD BO'LMAGAN POSTNI O'CHIRISH ────────
def test_delete_post_not_found(authorized_client):
    response = authorized_client.delete("/posts/99999")
    assert response.status_code == 404

# ─── BOSHQANING POSTINI O'CHIRISH ─────────────
def test_delete_other_user_post(authorized_client, db):
    from app import models
    from app.utils.hashing import hash_password

    other_user = models.User(
        username="other2",
        email="other2@example.com",
        password=hash_password("password123")
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    other_post = models.Post(
        title="Boshqaning posti",
        content="Kontent",
        owner_id=other_user.id
    )
    db.add(other_post)
    db.commit()
    db.refresh(other_post)

    response = authorized_client.delete(
        f"/posts/{other_post.id}"
    )
    assert response.status_code == 403

# ─── PAGINATION ───────────────────────────────
def test_get_posts_pagination(client, test_posts):
    response = client.get("/posts/?limit=2&skip=0")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response2 = client.get("/posts/?limit=2&skip=2")
    assert response2.status_code == 200
    assert len(response2.json()) == 1

# ─── QIDIRUV ──────────────────────────────────
def test_get_posts_search(client, test_posts):
    response = client.get("/posts/?search=Birinchi")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Birinchi post"



# Bo'sh title bilan post:
def test_create_post_empty_title(authorized_client):
    response = authorized_client.post(
        "/posts/",
        json={"title": "", "content": "Kontent"}
    )
    # 422 kelishi kerak

# Juda uzun title:
def test_create_post_long_title(authorized_client):
    response = authorized_client.post(
        "/posts/",
        json={"title": "A" * 1000, "content": "Kontent"}
    )
    # 422 kelishi kerak (255 ta belgi limit)  