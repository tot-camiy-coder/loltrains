"""
<| imgs.py |>
Описание:
вспомогательный файл для user.py
Made with ❤️ by @snowlover4ever
"""

import os
import re
from typing import List, Tuple
import random

BASE_PATH = "../media/defaults"

PHOTO_PATTERN = re.compile(r"^p(\d*)\.[a-zA-Z0-9]+$", re.IGNORECASE)
BANNER_PATTERN = re.compile(r"^b(\d*)\.[a-zA-Z0-9]+$", re.IGNORECASE)
PHOTO_DANGER_PATTERN = re.compile(r"^pd(\d*)\.[a-zA-Z0-9]+$", re.IGNORECASE)
BANNER_DANGER_PATTERN = re.compile(r"^bd(\d*)\.[a-zA-Z0-9]+$", re.IGNORECASE)

IMAGE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff', '.tif',
    '.ico', '.svg', '.heic', '.heif', '.avif', '.jfif', '.pjpeg', '.pjp'
}


def _is_image_file(filename: str) -> bool:
    """Проверяет, является ли файл изображением по расширению"""
    return any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)


def _scan_files() -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    Сканирует папку defaults и возвращает:
    (photos, banners, danger_photos, danger_banners)
    """
    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", BASE_PATH.lstrip("/")))
    print(full_path)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"[imgs.py] Папка не найдена: {full_path}")

    photos = []
    banners = []
    danger_photos = []
    danger_banners = []

    for file in os.listdir(full_path):
        if not _is_image_file(file):
            continue  # Пропускаем не-изображения

        filepath = os.path.join(BASE_PATH, file)

        if PHOTO_PATTERN.match(file):
            photos.append(filepath)
        elif BANNER_PATTERN.match(file):
            banners.append(filepath)
        elif PHOTO_DANGER_PATTERN.match(file):
            danger_photos.append(filepath)
        elif BANNER_DANGER_PATTERN.match(file):
            danger_banners.append(filepath)
        else:
            pass

    print(f"[imgs.py] Загружено: {len(photos)} фото, {len(banners)} баннеров, "
          f"{len(danger_photos)} pd, {len(danger_banners)} bd")

    return photos, banners, danger_photos, danger_banners


# Кэшируем при первом вызове
_photos, _banners, _pd, _bd = _scan_files()


def get_random_photos() -> str:
    """
    Возвращает случайную фотку.
    Если есть pd* — шанс выпадения пропорционален их количеству.
    Выпало? → Показываем. Двойной ролл? Уже встроен в шанс.
    """
    total_photos = _photos + _pd 
    if not total_photos:
        BASE_PATH = str(BASE_PATH).replace('..', '/api')
        return BASE_PATH + "/p1.png"

    choice = random.choice(total_photos)
    choice = choice.replace("\\", "/")
    choice = choice.replace("..", "/api")
    
    if choice in _pd:
        print(f"[imgs.py] ☢️ DANGER PHOTO ACTIVATED: {choice}")
    
    return choice


def get_random_banners() -> str:
    """
    То же самое, но для баннеров.
    bd* — шанс на эпик.
    """
    total_banners = _banners + _bd
    if not total_banners:
        return BASE_PATH + "/b1.png"

    choice = random.choice(total_banners)
    choice = choice.replace("\\", "/")
    choice = choice.replace("..", "/api")
    
    if choice in _bd:
        print(f"[imgs.py] ☢️ DANGER BANNER ACTIVATED: {choice}")

    return choice