from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.services.category_service import CategoryService
from app.auth import get_optional_user, get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db), _=Depends(get_optional_user)):
    return CategoryService(db).get_all()


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db), _=Depends(get_optional_user)):
    try:
        return CategoryService(db).get_by_id(category_id)
    except ValueError:
        raise HTTPException(404, f"Категория #{category_id}? Первый раз слышим")


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return CategoryService(db).create(data)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return CategoryService(db).update(category_id, data)
    except ValueError:
        raise HTTPException(404, f"Не нашлось категории #{category_id} для редактирования")


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        CategoryService(db).delete(category_id)
    except ValueError:
        raise HTTPException(404, f"Категория #{category_id} и так удалена. Или её не было?")
