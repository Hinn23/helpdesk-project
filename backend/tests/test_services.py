import os
os.environ["DISABLE_RATE_LIMIT"] = "1"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.auth import hash_password
from app.models.user import User
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.category import Category
from app.services.user_service import UserService
from app.services.ticket_service import TicketService
from app.services.category_service import CategoryService
from app.services.comment_service import CommentService
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketRead
from app.schemas.category import CategoryCreate, CategoryRead

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(User(name="Admin", email="admin@gmail.com", password=hash_password("admin123"), role="admin"))
    db.add(User(name="User", email="user@gmail.com", password=hash_password("user123"), role="user"))
    db.add(Category(name="Bug", description="Bugs"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestUserService:
    def test_get_all_users(self):
        db = next(get_db())
        svc = UserService(db)
        users = svc.get_all()
        assert len(users) >= 2

    def test_get_by_id_found(self):
        db = next(get_db())
        svc = UserService(db)
        user = svc.get_by_id(1)
        assert user.name == "Admin"

    def test_get_by_id_not_found(self):
        db = next(get_db())
        svc = UserService(db)
        with pytest.raises(ValueError, match="Пользователь не найден"):
            svc.get_by_id(999)

    def test_create_user(self):
        db = next(get_db())
        svc = UserService(db)
        data = UserCreate(name="New", email="new@gmail.com", password="pass123", role="user")
        user = svc.create(data)
        assert user.name == "New"
        assert user.email == "new@gmail.com"

    def test_create_duplicate_email(self):
        db = next(get_db())
        svc = UserService(db)
        data = UserCreate(name="Another", email="admin@gmail.com", password="pass123", role="user")
        with pytest.raises(ValueError, match="Email already registered"):
            svc.create(data)

    def test_delete_user(self):
        db = next(get_db())
        svc = UserService(db)
        svc.delete(2)
        with pytest.raises(ValueError):
            svc.get_by_id(2)


class TestTicketService:
    def test_create_ticket(self):
        db = next(get_db())
        svc = TicketService(db)
        data = TicketCreate(title="Test ticket", priority="high", description="Desc")
        ticket = svc.create(data, user_name="Admin")
        assert ticket.title == "Test ticket"
        assert ticket.priority == "high"

    def test_get_ticket_by_id_found(self):
        db = next(get_db())
        svc = TicketService(db)
        data = TicketCreate(title="Find me", priority="low")
        created = svc.create(data)
        ticket = svc.get_by_id(created.id)
        assert ticket.title == "Find me"

    def test_get_ticket_by_id_not_found(self):
        db = next(get_db())
        svc = TicketService(db)
        with pytest.raises(ValueError, match="Заявка не найдена"):
            svc.get_by_id(999)

    def test_update_ticket(self):
        db = next(get_db())
        svc = TicketService(db)
        data = TicketCreate(title="Original", priority="low")
        created = svc.create(data)
        update = TicketUpdate(title="Updated", status="done")
        ticket = svc.update(created.id, update, user_name="Admin")
        assert ticket.title == "Updated"
        assert ticket.status == "done"

    def test_delete_ticket(self):
        db = next(get_db())
        svc = TicketService(db)
        data = TicketCreate(title="Delete me", priority="low")
        created = svc.create(data)
        svc.delete(created.id)
        with pytest.raises(ValueError):
            svc.get_by_id(created.id)

    def test_filter_by_status(self):
        db = next(get_db())
        svc = TicketService(db)
        svc.create(TicketCreate(title="Done ticket", priority="low", status="done"), user_name="Admin")
        items, total = svc.get_all_filtered(status="done")
        assert total >= 1
        for t in items:
            assert t.status == "done"

    def test_filter_by_search(self):
        db = next(get_db())
        svc = TicketService(db)
        svc.create(TicketCreate(title="Find this one", priority="low"), user_name="Admin")
        items, total = svc.get_all_filtered(search="Find")
        assert total >= 1


class TestCategoryService:
    def test_create_category(self):
        db = next(get_db())
        svc = CategoryService(db)
        data = CategoryCreate(name="Test", description="Test category")
        cat = svc.create(data)
        assert cat.name == "Test"

    def test_get_all_categories(self):
        db = next(get_db())
        svc = CategoryService(db)
        cats = svc.get_all()
        assert len(cats) >= 1


class TestCommentService:
    def test_create_comment(self):
        db = next(get_db())
        ticket_svc = TicketService(db)
        ticket = ticket_svc.create(TicketCreate(title="Ticket", priority="low"))
        comment_svc = CommentService(db)
        comment = comment_svc.create(ticket.id, "Test comment", 1, "Admin")
        assert comment.text == "Test comment"
        assert comment.author_name == "Admin"

    def test_get_comments_by_ticket(self):
        db = next(get_db())
        ticket_svc = TicketService(db)
        ticket = ticket_svc.create(TicketCreate(title="Ticket", priority="low"))
        comment_svc = CommentService(db)
        comment_svc.create(ticket.id, "Comment 1", 1, "Admin")
        comment_svc.create(ticket.id, "Comment 2", 2, "User")
        comments = comment_svc.get_by_ticket(ticket.id)
        assert len(comments) == 2
