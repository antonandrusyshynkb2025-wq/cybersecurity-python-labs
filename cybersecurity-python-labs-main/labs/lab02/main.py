import sys
from datetime import datetime, timedelta, timezone

from .task1 import Admin, User, UserAccount


def demo():
    print("=== 1. Створення користувача та хешування пароля ===")
    u1 = User("ivan_ua", "ivan@example.com", "user")
    u1.set_password("SecurePass123")
    account1 = UserAccount(u1)
    print(account1.user)

    print("\n=== 2. Успішний вхід ===")
    account1.login("ivan_ua", "SecurePass123", "127.0.0.1")
    print(f"Авторизований: {account1.is_authenticated()}")

    print("\n=== 3. Зміна email із валідацією ===")
    account1.user.email = "new_ivan@example.com"
    print(f"Новий валідний email: {account1.user.email}")
    try:
        account1.user.email = "bad_email@"
    except ValueError as e:
        print(f"Перехоплено помилку валідації: {e}")

    print("\n=== 4. Права адміністратора (наслідування) ===")
    admin = Admin("admin_root", "admin@root.com")
    admin.grant_permission("delete_user")
    print(admin)
    print(f"Чи має право 'delete_user': {admin.has_permission('delete_user')}")

    print("\n=== 5. Завершення сеансу за таймаутом ===")
    print(f"Статус до таймауту: {account1.is_authenticated()}")
    if account1.session:
        account1.session.last_activity = datetime.now(timezone.utc) - timedelta(
            seconds=901
        )
    print(f"Статус після таймауту (>900 с): {account1.is_authenticated()}")

    print("\n=== 6. Невдалий вхід ===")
    account1.login("ivan_ua", "WrongPassword", "192.168.0.1")
    print(f"Авторизований після невдалого входу: {account1.is_authenticated()}")

    print("\n=== 7. Вихід із системи (Logout) ===")
    account1.login("ivan_ua", "SecurePass123", "127.0.0.1")
    account1.logout()
    print(f"Авторизований після logout: {account1.is_authenticated()}")

    print("\n=== 8. Додавання та перевірка нового користувача ===")
    # Створюємо 2-го користувача та передаємо спільний AuditLog
    u2 = User("olena_sec", "olena@security.ua", "analyst")
    u2.set_password("AuditSecret2026")
    account2 = UserAccount(u2, audit=account1.audit)

    account2.login("olena_sec", "AuditSecret2026", "10.0.0.45")
    print(f"Авторизовано ({account2.user.username}): {account2.is_authenticated()}")
    account2.logout()

    u3 = User("Tester2", "test@security.ua", "analyst")
    u3.set_password("AuditSecret2026")
    account2 = UserAccount(u2, audit=account1.audit)

    account2.login("Tester2", "AuditSecret2045", "10.0.0.45")
    print(f"Авторизовано ({account2.user.username}): {account2.is_authenticated()}")
    account2.logout()

    print("\n=== 9. Журнал AuditLog для всіх користувачів ===")
    account1.audit.show_all()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        print("Для запуску демонстрації виконайте:")
        print("python -m labs.lab02.main demo")
