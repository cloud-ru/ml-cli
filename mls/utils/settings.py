"""Модуль конфигурации профилей ML Space (MLS).

Данный модуль устанавливает основные пути к директориям и файлам конфигурации,
а также определяет профиль по умолчанию для системы MLS.

Константы:
    PROFILE_DIR (str): Путь к директории профилей пользователя.
    CONFIG_FILE (str): Путь к файлу конфигурации системы MLS.
    CREDENTIALS_FILE (str): Путь к файлу с учётными данными пользователя.
    DEFAULT_PROFILE (str): Имя профиля по умолчанию, определяется через переменную окружения `ML_PROFILE`.
"""
import os

# Путь к директории профилей пользователя в домашней директории.
PROFILE_DIR = os.path.expanduser('~/.mls')

# Путь к файлу конфигурации системы MLS.
CONFIG_FILE = os.path.join(PROFILE_DIR, 'config')

# пароль для шифрования credentials
SECRET_PASSWORD = os.getenv('MLS_PASSWORD', None)

# Путь к файлу с учётными данными пользователя для системы MLS.
CREDENTIALS_FILE = os.path.join(PROFILE_DIR, 'credentials')

# Путь к файлу с зашифрованными учётными данными пользователя для системы MLS.
ENCRYPTED_CREDENTIALS_FILE = os.path.join(PROFILE_DIR, 'credentials.key')

# Имя профиля по умолчанию. Если переменная окружения `ML_PROFILE` не установлена,
# используется значение 'default'.
DEFAULT_PROFILE = os.getenv('MLS_PROFILE_DEFAULT', 'default')

ENDPOINT_URL = 'https://api.ai.cloud.ru/public/v2'

# Расширяемый перечень регионов
# export MLS_REGIONS='AMC, DGX2-MT-001'
REGIONS = os.getenv('MLS_REGIONS', '').replace(' ', '').split(',')
