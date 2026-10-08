# Модуль для системи контролю доступу.

# Вхідні дані
USERS = {
    "sysadmin02": {
        "role": "system_admin",
        "clearance": 4,
        "department": "Infrastructure",
        "active": True,
    },
    "analyst234": {
        "role": "security_analyst",
        "clearance": 3,
        "department": "SOC",
        "active": True,
    },
    "developer567": {
        "role": "developer",
        "clearance": 2,
        "department": "Development",
        "active": True,
    },
    "intern890": {"role": "intern", "clearance": 1, "department": "HR", "active": True},
    "external123": {
        "role": "external",
        "clearance": 1,
        "department": "Vendor",
        "active": False,
    },
}

RESOURCES = [
    ("prod_database", 4),
    ("dev_environment", 2),
    ("documentation", 1),
    ("source_code", 3),
    ("server_configs", 4),
    ("test_data", 2),
    ("compliance_docs", 3),
    ("system_logs", 4),
    ("project_files", 2),
    ("public_wiki", 1),
]

SECURITY_LEVELS = ("Open", "Internal", "Restricted", "Top Secret")

BLOCKED_USERS = {"external123", "old_account", "test_user"}


def check_access(username, resource_level):
    # Визначає, чи має користувач доступ до ресурсу за рівнем безпеки.
    if username not in USERS:
        return "DENY (User not found)"

    if username in BLOCKED_USERS:
        return "DENY (User is blocked)"

    if not USERS[username]["active"]:
        return "DENY (Account inactive)"

    user_clearance = USERS[username]["clearance"]

    if user_clearance >= resource_level:
        return "ALLOW"

    return "DENY (Insufficient clearance)"


def main():
    # Головна функція виконання логіки завдання.
    # Виведення ресурсів
    print(f"{'Ресурс':<20} | {'Рівень безпеки'}")
    print("-" * 40)
    for name, level_idx in RESOURCES:
        level_name = SECURITY_LEVELS[level_idx - 1]
        print(f"{name:<20} | {level_name}")

    print("\n" + "=" * 60 + "\n")

    # Виведення результатів перевірки
    all_users = list(USERS.keys()) + ["test_user"]

    for username in all_users:
        for resource_name, resource_level in RESOURCES:
            status = check_access(username, resource_level)
            print(f"user={username:<15} resource={resource_name:<18} -> {status}")


if __name__ == "__main__":
    main()
