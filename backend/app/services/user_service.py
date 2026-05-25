from sqlalchemy.orm import Session
from app.repositories.user_repo import UserRepository
from app.models.user import User


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip, limit)

    def get_by_id(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        return user

    def create(self, data):
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")
        user = User(**data.model_dump())
        return self.repo.create(user)

    def update(self, user_id: int, data):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        update_data = data.model_dump(exclude_unset=True)
        new_email = update_data.get("email")
        new_name = update_data.get("name")
        if new_email is not None:
            existing = self.repo.get_by_email(new_email)
            if existing and existing.id != user_id:
                raise ValueError("Этот email уже занят")
        if new_name is not None:
            existing = self.repo.get_by_name(new_name)
            if existing and existing.id != user_id:
                raise ValueError("Это имя уже занято")
        for key, val in update_data.items():
            setattr(user, key, val)
        return self.repo.update(user)

    def delete(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        self.repo.delete(user)
