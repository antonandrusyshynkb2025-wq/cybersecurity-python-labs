import random


def get_password_strength(password, criteria, forbidden, all_passwords):
    length = len(password)
    has_digit = any(char.isdigit() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_special = any(not char.isalnum() for char in password)

    if password in forbidden or length < criteria["min_length"]:
        return "Заборонений"

    met_criteria_count = sum([has_digit, has_upper, has_special])

    if (
        met_criteria_count == 3
        and length >= (criteria["min_length"] + 4)
        and all_passwords.count(password) == 1
    ):
        return "Дуже сильний"

    if met_criteria_count == 3 and length < (criteria["min_length"] + 4):
        return "Сильний"

    if length >= criteria["min_length"] and met_criteria_count > 0:
        return "Середній"

    if has_digit or has_upper or has_lower or has_special:
        return "Слабкий"

    return "Слабкий"


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
    "!Test23@g2a1l.com",
]
criteria = {
    "min_length": 10,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}
forbidden_passwords = {"password", "simple", "weak", "basic", "12345", "hello"}

random_indices = random.sample(range(len(passwords)), 3)
for idx in random_indices:
    passwords.append(passwords[idx])

print(f"{'Пароль':<20} | {'Оцінка надійності':<15}")
print("-" * 40)

for pwd in passwords:
    strength = get_password_strength(pwd, criteria, forbidden_passwords, passwords)
    print(f"{pwd:<20} | {strength:<15}")
