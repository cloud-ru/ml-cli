"""Модуль конфигурации профилей ML Space (MLS).

Данный модуль устанавливает основные пути к директориям и файлам конфигурации,
а также определяет профиль по умолчанию для системы MLS.

Константы:
    PROFILE_DIR (str): Путь к директории профилей пользователя.
    CONFIG_FILE (str): Путь к файлу конфигурации системы MLS.
    CREDENTIALS_FILE (str): Путь к файлу с учётными данными пользователя.
    DEFAULT_PROFILE (str): Имя профиля по умолчанию, определяется через переменную окружения `MLS_PROFILE`.
    MLSPACE_PUBLIC_API_URL TODO
"""
import os

# Путь к директории профилей пользователя в домашней директории.
PROFILE_DIR = os.path.expanduser('~/.mls')

# Путь к файлу конфигурации системы MLS.
CONFIG_FILE = os.path.join(PROFILE_DIR, 'config')

# Путь к файлу с учётными данными пользователя для системы MLS.
CREDENTIALS_FILE = os.path.join(PROFILE_DIR, 'credentials')

# Имя профиля по умолчанию. Если переменная окружения `MLS_PROFILE` не установлена,
# используется значение 'default'.
DEFAULT_PROFILE = os.getenv('MLS_PROFILE', 'default')

MLSPACE_PUBLIC_API_URL = 'https://api.ai.cloud.ru/public/v2'
