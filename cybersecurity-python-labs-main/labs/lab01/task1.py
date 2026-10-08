import os
import random
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


def get_password_strength(password, criteria, forbidden):
    # Оцінює надійність пароля згідно з критеріями
    length = len(password)
    has_digit = any(char.isdigit() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_special = any(not char.isalnum() for char in password)

    # Заборонений пароль
    if password in forbidden or length < criteria["min_length"]:
        return "Заборонений"

    # Кількість виконаних основних критеріїв безпеки
    met_criteria_count = sum([has_digit, has_upper, has_special])

    # Дуже сильний пароль (min_length + 4, всі критерії, повна унікальність)
    if (
        met_criteria_count == 3
        and length >= (criteria["min_length"] + 4)
        and passwords.count(password) == 1
    ):
        return "Дуже сильний"

    # Сильний пароль (всі критерії, довжина менша за min_length + 4)
    if met_criteria_count == 3 and length < (criteria["min_length"] + 4):
        return "Сильний"

    # Середній пароль (відповідає мін. довжині та деяким критеріям)
    if length >= criteria["min_length"] and met_criteria_count > 0:
        return "Середній"

    # Слабкий пароль(виконує хоча б один критерій)
    if has_digit or has_upper or has_lower or has_special:
        return "Слабкий"

    return "Слабкий"


# Вихідні дані
passwords = [
    "Hello123!",
    "simple",
    "CompL3x@Pass",
    "password",
    "Str0ng#2023",
    "weak",
    "MySecur3!",
    "12345",
    "Advanced@1",
    "basic",
    "TestPass2024",
]

criteria = {
    "min_length": 10,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

forbidden_passwords = {"password", "simple", "weak", "basic", "12345", "hello"}

# Генерація дублікатів
random_indices = random.sample(range(len(passwords)), 3)
for idx in random_indices:
    passwords.append(passwords[idx])

# Вивід результатів
print(f"{'Пароль':<20} | {'Оцінка надійності':<15}")
print("-" * 40)

for pwd in passwords:
    strength = get_password_strength(pwd, criteria, forbidden_passwords)
    print(f"{pwd:<20} | {strength:<15}")
