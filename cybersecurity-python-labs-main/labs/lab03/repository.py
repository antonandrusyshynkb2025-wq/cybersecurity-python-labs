"""Шар доступу до даних (Repository) з чистими параметризованими SQL-запитами."""

from contextlib import closing
from typing import Any

from labs.lab03.database import get_connection


class NotFoundError(Exception):
    """Запис або категорія не знайдена."""


class ConflictError(Exception):
    """Порушення унікальності або зв'язності даних."""


def get_categories() -> list[dict[str, Any]]:
    """Повернути список усіх категорій, відсортованих за id."""
    with closing(get_connection()) as conn:
        cursor = conn.execute("SELECT id, name FROM categories ORDER BY id ASC;")
        return [dict(row) for row in cursor.fetchall()]


def get_category_by_id(category_id: int) -> dict[str, Any] | None:
    """Отримати категорію за id."""
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            "SELECT id, name FROM categories WHERE id = ?;",
            (category_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def create_category(name: str) -> dict[str, Any]:
    """Створити нову категорію."""
    with closing(get_connection()) as conn:
        try:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO categories (name) VALUES (?);",
                    (name,),
                )
                category_id = cursor.lastrowid
            return {"id": category_id, "name": name}
        except conn.IntegrityError as err:
            raise ConflictError("Категорія з такою назвою вже існує") from err


def delete_category(category_id: int) -> None:
    """Видалити порожню категорію."""
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            "SELECT id FROM categories WHERE id = ?;",
            (category_id,),
        )
        if not cursor.fetchone():
            raise NotFoundError(f"Категорію з id={category_id} не знайдено")

        record_check = conn.execute(
            "SELECT 1 FROM records WHERE category_id = ? LIMIT 1;",
            (category_id,),
        ).fetchone()
        if record_check:
            raise ConflictError("Неможливо видалити непорожню категорію")

        try:
            with conn:
                conn.execute(
                    "DELETE FROM categories WHERE id = ?;",
                    (category_id,),
                )
        except conn.IntegrityError as err:
            raise ConflictError("Помилка цілісності при видаленні категорії") from err


def get_records(
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Отримати список записів із фільтрами та пагінацією."""
    query = """
        SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name AS category_name
        FROM records r
        JOIN categories c ON r.category_id = c.id
        WHERE 1=1
    """
    params: list[Any] = []

    if category_id is not None:
        query += " AND r.category_id = ?"
        params.append(category_id)

    if status is not None:
        query += " AND r.status = ?"
        params.append(status)

    if min_value is not None:
        query += " AND r.value >= ?"
        params.append(min_value)

    if q is not None:
        query += " AND instr(r.title, ?) > 0"
        params.append(q)

    query += " ORDER BY r.id ASC LIMIT ? OFFSET ?;"
    params.extend([limit, offset])

    with closing(get_connection()) as conn:
        cursor = conn.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]


def get_record_by_id(record_id: int) -> dict[str, Any]:
    """Отримати один запис за його id."""
    query = """
        SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name AS category_name
        FROM records r
        JOIN categories c ON r.category_id = c.id
        WHERE r.id = ?;
    """
    with closing(get_connection()) as conn:
        row = conn.execute(query, (record_id,)).fetchone()
        if not row:
            raise NotFoundError(f"Запис з id={record_id} не знайдено")
        return dict(row)


def create_record(data: dict[str, Any]) -> dict[str, Any]:
    """Створити один запис."""
    with closing(get_connection()) as conn:
        cat = conn.execute(
            "SELECT name FROM categories WHERE id = ?;",
            (data["category_id"],),
        ).fetchone()
        if not cat:
            raise NotFoundError(f"Категорію з id={data['category_id']} не знайдено")

        try:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        data["code"],
                        data["title"],
                        data["category_id"],
                        data["value"],
                        data["status"],
                    ),
                )
                record_id = cursor.lastrowid
            return {
                "id": record_id,
                "code": data["code"],
                "title": data["title"],
                "category_id": data["category_id"],
                "value": data["value"],
                "status": data["status"],
                "category_name": cat["name"],
            }
        except conn.IntegrityError as err:
            raise ConflictError(f"Запис із кодом '{data['code']}' вже існує") from err


def update_record(record_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """Повністю оновити запис за record_id."""
    with closing(get_connection()) as conn:
        existing = conn.execute(
            "SELECT id FROM records WHERE id = ?;",
            (record_id,),
        ).fetchone()
        if not existing:
            raise NotFoundError(f"Запис з id={record_id} не знайдено")

        cat = conn.execute(
            "SELECT name FROM categories WHERE id = ?;",
            (data["category_id"],),
        ).fetchone()
        if not cat:
            raise NotFoundError(f"Категорію з id={data['category_id']} не знайдено")

        try:
            with conn:
                conn.execute(
                    """
                    UPDATE records
                    SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                    WHERE id = ?;
                    """,
                    (
                        data["code"],
                        data["title"],
                        data["category_id"],
                        data["value"],
                        data["status"],
                        record_id,
                    ),
                )
            return {
                "id": record_id,
                "code": data["code"],
                "title": data["title"],
                "category_id": data["category_id"],
                "value": data["value"],
                "status": data["status"],
                "category_name": cat["name"],
            }
        except conn.IntegrityError as err:
            raise ConflictError(
                f"Код '{data['code']}' вже використовується іншим записом"
            ) from err


def delete_record(record_id: int) -> None:
    """Видалити запис."""
    with closing(get_connection()) as conn, conn:
        cursor = conn.execute(
            "DELETE FROM records WHERE id = ?;",
            (record_id,),
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Запис з id={record_id} не знайдено")


def create_records_bulk(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Атомарно створити список записів в одній транзакції."""
    if not items:
        return []

    codes = [item["code"] for item in items]
    if len(codes) != len(set(codes)):
        raise ConflictError("Дублікат code всередині переданого пакета")

    with closing(get_connection()) as conn:
        for item in items:
            cat = conn.execute(
                "SELECT 1 FROM categories WHERE id = ?;",
                (item["category_id"],),
            ).fetchone()
            if not cat:
                raise NotFoundError(f"Категорію з id={item['category_id']} не знайдено")

        created_records: list[dict[str, Any]] = []
        try:
            with conn:
                for item in items:
                    cursor = conn.execute(
                        """
                        INSERT INTO records (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?);
                        """,
                        (
                            item["code"],
                            item["title"],
                            item["category_id"],
                            item["value"],
                            item["status"],
                        ),
                    )
                    record_id = cursor.lastrowid
                    cat_name = conn.execute(
                        "SELECT name FROM categories WHERE id = ?;",
                        (item["category_id"],),
                    ).fetchone()["name"]

                    created_records.append(
                        {
                            "id": record_id,
                            "code": item["code"],
                            "title": item["title"],
                            "category_id": item["category_id"],
                            "value": item["value"],
                            "status": item["status"],
                            "category_name": cat_name,
                        }
                    )
            return created_records
        except conn.IntegrityError as err:
            raise ConflictError(
                "Помилка цілісності даних або дублікат коду в базі"
            ) from err
