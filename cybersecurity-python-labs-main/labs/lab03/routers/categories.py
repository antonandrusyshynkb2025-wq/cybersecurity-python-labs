"""Маршрути для роботи з категоріями."""

from fastapi import APIRouter, HTTPException, status

from labs.lab03 import repository
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=list[CategoryRead],
    summary="Отримати список категорій",
)
def list_categories() -> list[dict]:
    """Повертає список категорій, відсортованих за id у зростаючому порядку."""
    return repository.get_categories()


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити нову категорію",
    responses={409: {"description": "Категорія з такою назвою вже існує"}},
)
def create_category(payload: CategoryCreate) -> dict:
    """Створює нову категорію."""
    try:
        return repository.create_category(name=payload.name)
    except repository.ConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(err)
        ) from err


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити порожню категорію",
    responses={
        404: {"description": "Категорію не знайдено"},
        409: {"description": "Категорія містить пов'язані записи"},
    },
)
def delete_category(category_id: int) -> None:
    """Видаляє категорію, якщо в ній немає записів."""
    try:
        repository.delete_category(category_id=category_id)
    except repository.NotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except repository.ConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(err)
        ) from err
