import os
os.environ["DISABLE_RATE_LIMIT"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.auth import hash_password
from app.models.user import User
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.category import Category
from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(User(name="Admin", email="admin@gmail.com", password=hash_password("admin123"), role="admin"))
    db.add(User(name="User", email="user@gmail.com", password=hash_password("user123"), role="user"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    resp = client.post("/auth/login", json={"email": "admin@gmail.com", "password": "admin123"})
    return resp.json()["access_token"]


@pytest.fixture
def user_token(client):
    resp = client.post("/auth/login", json={"email": "user@gmail.com", "password": "user123"})
    return resp.json()["access_token"]


@pytest.fixture
def auth(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


class TestHealth:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["app"] == "Helpdesk Lite"


class TestTickets:
    def test_create_ticket(self, client, auth):
        resp = client.post("/tickets/", json={
            "title": "Test ticket",
            "description": "Test description",
            "priority": "high",
        }, headers=auth)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test ticket"
        assert data["id"] is not None

    def test_get_tickets(self, client):
        resp = client.get("/tickets/")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    def test_get_ticket_by_id(self, client, auth):
        resp = client.post("/tickets/", json={"title": "Find me", "priority": "low"}, headers=auth)
        ticket_id = resp.json()["id"]
        resp = client.get(f"/tickets/{ticket_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Find me"

    def test_update_ticket(self, client, auth):
        resp = client.post("/tickets/", json={"title": "Update me", "priority": "low"}, headers=auth)
        ticket_id = resp.json()["id"]
        resp = client.put(f"/tickets/{ticket_id}", json={"title": "Updated", "status": "done"}, headers=auth)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"
        assert resp.json()["status"] == "done"

    def test_delete_ticket(self, client, auth):
        resp = client.post("/tickets/", json={"title": "Delete me", "priority": "low"}, headers=auth)
        ticket_id = resp.json()["id"]
        resp = client.delete(f"/tickets/{ticket_id}", headers=auth)
        assert resp.status_code == 204
        resp = client.get(f"/tickets/{ticket_id}")
        assert resp.status_code == 404

    def test_author_can_update_own_ticket(self, client, auth):
        resp = client.post("/tickets/", json={"title": "My ticket", "priority": "low"}, headers=auth)
        ticket_id = resp.json()["id"]
        resp = client.put(f"/tickets/{ticket_id}", json={"title": "Updated by author"}, headers=auth)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated by author"

    def test_author_can_delete_own_ticket(self, client, user_token):
        auth_user = {"Authorization": f"Bearer {user_token}"}
        resp = client.post("/tickets/", json={"title": "Delete me", "priority": "low"}, headers=auth_user)
        ticket_id = resp.json()["id"]
        resp = client.delete(f"/tickets/{ticket_id}", headers=auth_user)
        assert resp.status_code == 204

    def test_author_cannot_update_others_ticket(self, client, auth, user_token):
        resp = client.post("/tickets/", json={"title": "Admin ticket", "priority": "high"}, headers=auth)
        ticket_id = resp.json()["id"]
        auth_user = {"Authorization": f"Bearer {user_token}"}
        resp = client.put(f"/tickets/{ticket_id}", json={"title": "Hacked!"}, headers=auth_user)
        assert resp.status_code == 403

    def test_author_cannot_delete_others_ticket(self, client, auth, user_token):
        resp = client.post("/tickets/", json={"title": "Admin ticket", "priority": "low"}, headers=auth)
        ticket_id = resp.json()["id"]
        auth_user = {"Authorization": f"Bearer {user_token}"}
        resp = client.delete(f"/tickets/{ticket_id}", headers=auth_user)
        assert resp.status_code == 403

    def test_get_ticket_404(self, client):
        resp = client.get("/tickets/99999")
        assert resp.status_code == 404

    def test_pagination(self, client, auth):
        for i in range(3):
            client.post("/tickets/", json={"title": f"Ticket {i}", "priority": "low"}, headers=auth)
        resp = client.get("/tickets/?skip=0&limit=2")
        data = resp.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1

    def test_filter_by_status(self, client, auth):
        client.post("/tickets/", json={"title": "New ticket", "priority": "low", "status": "new"}, headers=auth)
        resp = client.get("/tickets/?status=new")
        data = resp.json()
        for t in data["items"]:
            assert t["status"] == "new"

    def test_filter_by_priority(self, client, auth):
        client.post("/tickets/", json={"title": "High ticket", "priority": "high"}, headers=auth)
        resp = client.get("/tickets/?priority=high")
        data = resp.json()
        for t in data["items"]:
            assert t["priority"] == "high"

    def test_search(self, client, auth):
        client.post("/tickets/", json={"title": "Find me please", "priority": "low"}, headers=auth)
        resp = client.get("/tickets/?search=Find")
        data = resp.json()
        assert len(data["items"]) > 0

    def test_validation_title_short(self, client, auth):
        resp = client.post("/tickets/", json={"title": "ab", "priority": "low"}, headers=auth)
        assert resp.status_code == 422

    def test_validation_priority_invalid(self, client, auth):
        resp = client.post("/tickets/", json={"title": "Valid title", "priority": "urgent"}, headers=auth)
        assert resp.status_code == 422

    def test_validation_status_invalid(self, client, auth):
        resp = client.post("/tickets/", json={"title": "Valid title", "priority": "low", "status": "unknown"}, headers=auth)
        assert resp.status_code == 422

    def test_validation_deadline_past(self, client, auth):
        resp = client.post("/tickets/", json={
            "title": "Past deadline",
            "priority": "low",
            "deadline": "2020-01-01T00:00:00",
        }, headers=auth)
        assert resp.status_code == 422


class TestCategories:
    def test_categories(self, client):
        resp = client.get("/categories/")
        assert resp.status_code == 200

    def test_create_category(self, client, auth):
        resp = client.post("/categories/", json={"name": "TestCat", "description": "Test"}, headers=auth)
        assert resp.status_code == 201
        assert resp.json()["name"] == "TestCat"

    def test_validation_category_name_short(self, client, auth):
        resp = client.post("/categories/", json={"name": "X"}, headers=auth)
        assert resp.status_code == 422


class TestComments:
    def test_comments_flow(self, client, auth):
        resp = client.post("/tickets/", json={"title": "Comment test", "priority": "low"}, headers=auth)
        ticket_id = resp.json()["id"]
        resp = client.post(f"/tickets/{ticket_id}/comments/", json={"text": "Test comment"}, headers=auth)
        assert resp.status_code == 201
        assert resp.json()["text"] == "Test comment"
        resp = client.get(f"/tickets/{ticket_id}/comments/")
        assert len(resp.json()) == 1

    def test_validation_comment_empty(self, client, auth):
        resp = client.post("/tickets/", json={"title": "Ticket for comment", "priority": "low"}, headers=auth)
        ticket_id = resp.json()["id"]
        resp = client.post(f"/tickets/{ticket_id}/comments/", json={"text": ""}, headers=auth)
        assert resp.status_code == 422


class TestAuth:
    def test_register(self, client, setup_db):
        resp = client.post("/auth/register", json={"name": "NewUser", "email": "newuser@gmail.com", "password": "test123", "role": "user"})
        assert resp.status_code == 200
        assert resp.json()["message"] == "Код подтверждения отправлен на почту"

    def test_login(self, client):
        resp = client.post("/auth/login", json={"email": "admin@gmail.com", "password": "admin123"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_auth_me(self, client):
        resp = client.post("/auth/login", json={"email": "admin@gmail.com", "password": "admin123"})
        token = resp.json()["access_token"]
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "admin@gmail.com"

    def test_auth_invalid(self, client):
        resp = client.post("/auth/login", json={"email": "nonexist@gmail.com", "password": "wrong"})
        assert resp.status_code == 401


class TestRoles:
    def test_x_user_role_header(self, client):
        resp = client.get("/tickets/", headers={"X-User-Role": "guest"})
        assert resp.status_code == 200

    def test_guest_cannot_write(self, client):
        resp = client.post("/tickets/", json={"title": "Guest ticket", "priority": "low"}, headers={"X-User-Role": "guest"})
        assert resp.status_code == 403

    def test_anon_cannot_write(self, client):
        resp = client.post("/tickets/", json={"title": "Anon ticket", "priority": "low"})
        assert resp.status_code == 401

    def test_guest_can_read(self, client):
        resp = client.get("/tickets/", headers={"X-User-Role": "guest"})
        assert resp.status_code == 200


class TestUsers:
    def test_get_users(self, client, auth):
        resp = client.get("/users/", headers=auth)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 2

    def test_validation_name_short(self, client, auth):
        resp = client.post("/users/", json={"name": "A", "email": "a@b.com", "password": "123"}, headers=auth)
        assert resp.status_code == 422

    def test_validation_email_invalid(self, client, auth):
        resp = client.post("/users/", json={"name": "Test", "email": "notanemail", "password": "123"}, headers=auth)
        assert resp.status_code == 422
