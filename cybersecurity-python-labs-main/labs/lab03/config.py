"""Конфігурація та константи предметної області для Варіанта 2."""

VARIANT_NUMBER: int = 2
TITLE: str = "Реєстр вразливостей мережевих сервісів"
DESCRIPTION: str = (
    "Сервіс обліку результатів навчальної перевірки мережевих сервісів. "
    "Категорія визначає групу сервісів (mail, vpn, dns), "
    "value — оцінку небезпеки (score, від 0.0 до 10.0), "
    "status — стан опрацювання знахідки."
)
UNIT: str = "score"
THRESHOLD: float = 6.0

MIN_VALUE: float = 0.0
MAX_VALUE: float = 10.0

ALLOWED_STATUSES = ("new", "in_progress", "done")
