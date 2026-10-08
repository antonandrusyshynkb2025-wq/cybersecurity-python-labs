import csv
import datetime
import hashlib
import json
import os
from functools import wraps

# Константи та налаштування
VARIANT = 2
SALT = str(VARIANT).zfill(5)
MIN_LENGTH = 10
DATA_DIR = "labs/lab01/data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
LOG_FILE = os.path.join(DATA_DIR, "log.json")


class ValidationError(Exception):
    """Власний виняток для помилок валідації пароля."""


def generate_hash(password: str, salt: str = SALT) -> str:
    # Генерує SHA3-224 хеш пароля з додаванням солі
    if not password or not salt:
        raise ValueError("Пароль або сіль не можуть бути порожніми.")
    if len(password) < MIN_LENGTH:
        raise ValidationError(f"Пароль має бути не менше {MIN_LENGTH} символів.")

    combined = password + salt
    return hashlib.sha3_224(combined.encode()).hexdigest()


def log_event(func):
    # Декоратор для логування подій у JSON файл
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        log_entry = {
            "event": "login",
            "user": args[0] if args else "unknown",
            "result": "success" if result else "failure",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "args": list(args),
            "kwargs": kwargs,
        }
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            json.dump(log_entry, f)
            f.write("\n")
        return result

    return wrapper


def create_user(username: str, password: str) -> tuple:
    # Створює кортеж (логін, хеш).
    hash_value = generate_hash(password)
    return (username, hash_value)


def create_users(users_list: list):
    # Запис у CSV файл
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for username, password in users_list:
            if not username or not username.strip():
                print("Логін не може бути порожнім.")
                continue

            try:
                writer.writerow(create_user(username, password))
            except (ValidationError, ValueError) as e:
                print(f"Помилка реєстрації {username}: {e}")


@log_event
def login(username: str, password: str) -> bool:
    # Перевіряє автентичність користувача.
    if not username or not password:
        raise ValueError("Логін або пароль не можуть бути порожніми.")

    input_hash = generate_hash(password)
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for u_name, u_hash in reader:
            if u_name == username and u_hash == input_hash:
                return True
    return False


def main():
    # Головна функція виконання логіки.
    users_to_register = [
        ("user1", "securePass123!"),
        ("admin_user", "verySecretKey2026"),
        ("tester01", "testPass1234567"),
        ("", "Test123456"),
        ("user5", ""),
    ]

    try:
        # Реєстрація та читання
        create_users(users_to_register)

        print(f"{'Логін':<15} | {'Хеш пароля'}")
        print("-" * 50)
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                print(f"{row[0]:<15} | {row[1]}")

        # Спроба входу
        print(f"\nСтатус входу: {login('user1', 'securePass123!')}")

    except (
        OSError,
        FileNotFoundError,
        PermissionError,
        ValidationError,
        ValueError,
    ) as e:
        print(f"Системна помилка: {e}")


if __name__ == "__main__":
    main()
