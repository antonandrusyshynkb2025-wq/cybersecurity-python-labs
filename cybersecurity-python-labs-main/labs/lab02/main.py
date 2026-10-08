from .task1 import User, Admin, UserAccount

def demo():
    # Демонстрація
    print("--- Створення користувача ---")
    u = User("ivan_ua", "ivan@example.com", "user")
    u.set_password("SecurePass123")
    
    account = UserAccount(u)
    
    print("--- Успішний вхід ---")
    account.login("ivan_ua", "SecurePass123", "127.0.0.1")
    print(f"Auth: {account.is_authenticated()}")
    
    print("--- Зміна email ---")
    account.user.email = "new_ivan@example.com"
    print(f"New email: {account.user.email}")
    
    print("--- Адмін права ---")
    admin = Admin("admin_root", "admin@root.com")
    admin.grant_permission("delete_user")
    print(admin)

    print("\n--- Невдалий вхід ---")
    account.login("ivan_ua", "WrongPassword", "192.168.0.1")
    
    print("\n--- Вихід із системи ---")
    account.logout()
    
    print("\n--- Повний аудит ---")
    account.audit.show_all()
    
    print("--- Аудит ---")
    account.audit.show_all()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
        