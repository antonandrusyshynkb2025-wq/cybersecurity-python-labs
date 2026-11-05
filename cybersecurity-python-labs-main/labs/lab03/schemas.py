"""Pydantic-моделі для валідації запитів та відповідей API."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyStrCategory = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=40),
]
NonEmptyStrCode = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=40),
]
NonEmptyStrTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=120),
]


class CategoryBase(BaseModel):
    """Базова схема категорії."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )
    name: NonEmptyStrCategory = Field(
        ...,
        description="Унікальна назва категорії (наприклад, mail, vpn, dns)",
    )


class CategoryCreate(CategoryBase):
    """Схема створення категорії."""


class CategoryRead(CategoryBase):
    """Схема відображення категорії."""

    id: int = Field(..., gt=0)


class RecordCreate(BaseModel):
    """Схема створення нового запису."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )
    code: NonEmptyStrCode = Field(
        ...,
        description="Унікальний ідентифікатор запису (наприклад, V02-01)",
    )
    title: NonEmptyStrTitle = Field(
        ...,
        description="Опис або назва перевірки",
    )
    category_id: int = Field(
        ...,
        gt=0,
        description="Ідентифікатор наявної категорії",
    )
    value: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        allow_inf_nan=False,
        description="Оцінка небезпеки в межах [0.0; 10.0]",
    )
    status: Literal["new", "in_progress", "done"] = Field(
        ...,
        description="Статус опрацювання знахідки",
    )


class RecordReplace(RecordCreate):
    """Схема повної заміни запису (PUT)."""


class RecordRead(RecordCreate):
    """Схема читання запису з розширеними даними."""

    id: int = Field(..., gt=0)
    category_name: str = Field(..., description="Назва категорії з таблиці categories")


class StudentInfo(BaseModel):
    """Інформація про автора роботи."""

    student_name: str
    group_name: str
    variant_number: int
