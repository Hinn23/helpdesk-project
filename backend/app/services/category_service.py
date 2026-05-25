from sqlalchemy.orm import Session
from app.repositories.category_repo import CategoryRepository
from app.models.category import Category


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, category_id: int):
        category = self.repo.get_by_id(category_id)
        if not category:
            raise ValueError("Категория не найдена")
        return category

    def create(self, data):
        category = Category(**data.model_dump())
        return self.repo.create(category)

    def update(self, category_id: int, data):
        category = self.repo.get_by_id(category_id)
        if not category:
            raise ValueError("Категория не найдена")
        for key, val in data.model_dump(exclude_unset=True).items():
            setattr(category, key, val)
        return self.repo.update(category)

    def delete(self, category_id: int):
        category = self.repo.get_by_id(category_id)
        if not category:
            raise ValueError("Категория не найдена")
        self.repo.delete(category)
