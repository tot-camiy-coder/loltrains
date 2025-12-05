"""
<| titles.py |>
Описание:
вспомогательный файл для user.py
который случайно выдаёт звание
Made with ❤️ by @snowlover4ever
"""

import random

started_titles = [
    "Новичок", "Новенький", "Начинающий", "Ученик",
    "Зелёный", "Птенец", "Стажёр", "Первый шаг", "Юниор",
    "Свежая кровь"
]

def get_random_titles() -> str:
    return random.choice(started_titles)