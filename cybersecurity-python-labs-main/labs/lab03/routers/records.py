"""Маршрути для роботи із записами перевірок."""

from typing import Annotated, Literal

from fastapi import APIRouter, Body, HTTPException, Query, status

from labs.lab03 import repository
from labs.lab03.config import MAX_VALUE, MIN_VALUE
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])


@router.get(
    "",
    response_model=list[RecordRead],
    summary="Отримати записи з фільтрами та пагінацією",
)
def list_records(
    category_id: int | None = Query(
        default=None, gt=0, description="Фільтр за ID категорії"
    ),
    status_filter: Literal["new", "in_progress", "done"] | None = Query(
        default=None, alias="status", description="Фільтр за статусом"
    ),
    min_value: float | None = Query(
        default=None,
        ge=MIN_VALUE,
        le=MAX_VALUE,
        description="Мінімальне значення оцінки",
    ),
    q: str | None = Query(
        default=None,
        min_length=1,
        max_length=120,
        description="Буквальний пошук у назві",
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Кількість записів"),
    offset: int = Query(default=0, ge=0, description="Зсув для сторінкового перегляду"),
) -> list[dict]:
    """Повертає список записів за вказаними фільтрами."""
    return repository.get_records(
        category_id=category_id,
        status=status_filter,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{record_id}",
    response_model=RecordRead,
    summary="Отримати окремий запис",
    responses={404: {"description": "Запис не знайдено"}},
)
def get_record(record_id: int) -> dict:
    """Повертає окремий запис за id."""
    try:
        return repository.get_record_by_id(record_id)
    except repository.NotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err


@router.post(
    "",
    response_model=RecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити новий запис",
    responses={
        404: {"description": "Категорію не знайдено"},
        409: {"description": "Дублікат коду запису"},
    },
)
def create_record(payload: RecordCreate) -> dict:
    """Створює один запис."""
    try:
        return repository.create_record(payload.model_dump())
    except repository.NotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except repository.ConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(err)
        ) from err


@router.put(
    "/{record_id}",
    response_model=RecordRead,
    summary="Повна заміна наявного запису",
    responses={
        404: {"description": "Запис або категорію не знайдено"},
        409: {"description": "Код конфліктує з іншим записом"},
    },
)
def replace_record(record_id: int, payload: RecordReplace) -> dict:
    """Повністю оновлює дані запису зі збереженням його id."""
    try:
        return repository.update_record(record_id, payload.model_dump())
    except repository.NotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except repository.ConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(err)
        ) from err


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити запис",
    responses={404: {"description": "Запис не знайдено"}},
)
def delete_record(record_id: int) -> None:
    """Видаляє запис за вказаним id."""
    try:
        repository.delete_record(record_id)
    except repository.NotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err


@router.post(
    "/bulk",
    response_model=list[RecordRead],
    status_code=status.HTTP_201_CREATED,
    summary="Пакетне збереження записів",
    responses={
        404: {"description": "Категорію одного з елементів не знайдено"},
        409: {"description": "Дублікат коду запису"},
    },
)
def create_records_bulk(
    items: Annotated[list[RecordCreate], Body(min_length=1, max_length=100)],
) -> list[dict]:
    """Атомарно створює від 1 до 100 записів."""
    try:
        data = [item.model_dump() for item in items]
        return repository.create_records_bulk(data)
    except repository.NotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except repository.ConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(err)
        ) from err
