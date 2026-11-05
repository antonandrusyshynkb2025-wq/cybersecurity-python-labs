"""Головний модуль FastAPI-застосунку з життєвим циклом (Lifespan)."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from labs.lab03.config import DESCRIPTION, THRESHOLD, TITLE, UNIT, VARIANT_NUMBER
from labs.lab03.database import initialize_database
from labs.lab03.routers.categories import router as categories_router
from labs.lab03.routers.records import router as records_router
from labs.lab03.schemas import StudentInfo


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Контекст життєвого циклу: створення таблиць перед запуском."""
    initialize_database()
    yield


app = FastAPI(
    title=f"{TITLE} (Варіант {VARIANT_NUMBER})",
    description=f"{DESCRIPTION}\n\nОдиниця вимірювання: {UNIT}, Поріг: {THRESHOLD}",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories_router)
app.include_router(records_router)


@app.get("/ping", tags=["System"], summary="Перевірка доступності сервісу")
def ping() -> dict[str, str]:
    """Повертає статус працездатності сервісу."""
    return {"status": "ok"}


@app.get(
    "/student", response_model=StudentInfo, tags=["System"], summary="Дані студента"
)
def get_student() -> dict[str, str | int]:
    """Повертає відомості про автора та варіант роботи."""
    try:
        from shared.student import GROUP_NAME, STUDENT_NAME
        from shared.student import VARIANT_NUMBER as V_NUM

        return {
            "student_name": STUDENT_NAME,
            "group_name": GROUP_NAME,
            "variant_number": V_NUM,
        }
    except ImportError:
        return {
            "student_name": "Іванов Іван Іванович",
            "group_name": "КБ-101",
            "variant_number": VARIANT_NUMBER,
        }
