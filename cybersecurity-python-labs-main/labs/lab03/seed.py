"""Початкове заповнення бази навчальними даними з JSON."""

import json
import logging
from contextlib import closing
from pathlib import Path

from labs.lab03.database import get_connection, initialize_database

logger = logging.getLogger(__name__)
SEED_FILE = Path(__file__).resolve().parent / "data" / "seed.json"


def seed_database() -> None:
    """Заповнити базу початковими категоріями та записами."""
    initialize_database()

    if not SEED_FILE.exists():
        print(f"Файл {SEED_FILE} не знайдено.")
        return

    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    categories = data.get("categories", [])
    records = data.get("records", [])

    with closing(get_connection()) as conn:
        cat_count = conn.execute("SELECT COUNT(*) AS c FROM categories;").fetchone()[
            "c"
        ]
        rec_count = conn.execute("SELECT COUNT(*) AS c FROM records;").fetchone()["c"]

        if cat_count > 0 or rec_count > 0:
            print("База даних вже містить інформацію. Початкове заповнення пропущено.")
            return

        try:
            with conn:
                for cat in categories:
                    conn.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?);",
                        (cat["id"], cat["name"]),
                    )
                for rec in records:
                    conn.execute(
                        """
                        INSERT INTO records (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?);
                        """,
                        (
                            rec["code"],
                            rec["title"],
                            rec["category_id"],
                            rec["value"],
                            rec["status"],
                        ),
                    )
            print(
                f"Успішно додано: {len(categories)} категорій та {len(records)} записів."
            )
        except conn.Error as err:
            logger.error("Помилка під час початкового заповнення: %s", err)
            print("Помилка: зміни скасовано.")
            raise


if __name__ == "__main__":
    seed_database()
