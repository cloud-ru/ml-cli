"""Модуль конфигурации профилей MLS.

Этот модуль предоставляет функции для настройки и управления профилями пользователей
в системе MLS через интерфейс командной строки (CLI). Используются библиотеки `click`
для создания CLI и `configparser` для работы с конфигурационными файлами.

Функции:
    configure_profile(profile=None): Конфигурирует профиль пользователя.
    save_profile(config, credentials): Сохраняет конфигурацию и учётные данные в файлы.
    collect_user_inputs(config, credentials, profile_name): Собирает ввод пользователя для профиля.
    prepare_profile(profile_name): Загружает текущую конфигурацию профиля.
    mask_secret(secret): Маскирует секретные значения для безопасного отображения.
    get_user_input(prompt_text, default_value, no_entry_value): Получает ввод пользователя с предложением.


"""
import os
from getpass import getpass
from io import StringIO

import click

from mls.utils.common import load_saved_config
from mls.utils.execption import ConfigReadError
from mls.utils.execption import ConfigWriteError
from mls.utils.execption import DecryptionError
from mls.utils.execption import EncryptionError
from mls.utils.execption import MissingPassword
from mls.utils.openssl import encrypt as enc
from mls.utils.settings import CONFIG_FILE
from mls.utils.settings import CREDENTIALS_FILE
from mls.utils.settings import DEFAULT_PROFILE
from mls.utils.settings import ENCRYPTED_CREDENTIALS_FILE
from mls.utils.settings import ENDPOINT_URL
from mls.utils.style import error_format
from mls.utils.style import message_format
from mls.utils.style import success_format


def mask_secret(secret):
    """Маскирует секретные значения, отображая только последние символы.

    Функция предназначена для скрытия чувствительных данных (например, API ключей),
    показывая только последний символ для целей безопасности.

    Аргументы:
        secret (str): Исходное секретное значение.

    Возвращает:
        str: Маскированное секретное значение.
    """
    if not secret:
        return ''
    if len(secret) > 12:
        return '...' + '*' * 8 + secret[-1]
    return (len(secret) - 1) * '*' + secret[-1]


def get_user_input(prompt_text, default_value, no_entry_value):
    """Получает ввод пользователя с предложением значения по умолчанию.

    Если пользователь не вводит значение, возвращается `no_entry_value`.

    Аргументы:
        prompt_text (str): Текст запроса для пользователя.
        default_value (str): Значение по умолчанию для отображения.
        no_entry_value (str): Значение, возвращаемое в случае отсутствия ввода.

    Возвращает:
        str: Введённое пользователем значение или `no_entry_value`.
    """
    return input(message_format(f'{prompt_text} [{default_value}]: ')) or no_entry_value


def configure_profile(profile=None, encrypt=False):
    """Конфигурация профиля пользователя через CLI.

    Функция инициализирует процесс настройки профиля, собирает необходимые
    данные от пользователя и сохраняет конфигурацию и учётные данные.

    Аргументы:
        profile (str, optional): Имя профиля для конфигурации. Если не указано, используется профиль по умолчанию.
        encrypt (bool, optional): Если задан, учётные данные шифруются.
    Возвращает:
        None
    """
    profile_name = profile or DEFAULT_PROFILE
    password = None

    if encrypt:
        if os.path.exists(ENCRYPTED_CREDENTIALS_FILE):
            password = get_decrypt_password()
        else:
            password = get_encrypt_password()

    config, credentials = prepare_profile(profile_name, password)
    collect_user_inputs(config, credentials, profile_name)

    try:
        save_profile(config, credentials, password)
    except EncryptionError as er:
        raise er
    except Exception as er:
        click.echo(error_format('Профиль не сохранен !'))
        raise ConfigWriteError(er) from er

    click.echo(success_format(f"Профиль '{profile_name}' успешно сохранен!"))


def get_decrypt_password():
    """Запрашивает у пользователя пароль для расшифровки существующего файла с учётными данными."""
    password = getpass(message_format('Введите пароль для расшифровки данных: '))
    if password:
        return password

    click.echo(error_format('Пароль не может быть пустым'))

    return get_decrypt_password()


def get_encrypt_password():
    """Запрашивает у пользователя новый пароль с подтверждением для шифрования учётных данных."""
    password = getpass(message_format('Задайте пароль шифрования данных: '))
    if not password:
        raise MissingPassword

    confirm_password = getpass(message_format('Подтвердите пароль: '))
    if password == confirm_password:
        return password

    click.echo(error_format('Пароли не совпадают'))

    return get_encrypt_password()


def collect_user_inputs(config, credentials, profile_name):
    """Собирает ввод пользователя для настройки профиля.

    Функция запрашивает у пользователя необходимые параметры для профиля,
    такие как API ключи и настройки региона, и обновляет объекты `config` и `credentials`.

    Аргументы:
        config (ConfigParser): Объект конфигурации для хранения настроек.
        credentials (ConfigParser): Объект конфигурации для хранения учётных данных.
        profile_name (str): Имя профиля, который настраивается.

    Возвращает:
        None
    """
    fields = [
        ('key_id', 'Key ID', credentials, mask_secret, lambda x: x),
        ('key_secret', 'Key Secret', credentials, mask_secret, lambda x: x),
        ('x_workspace_id', 'x-workspace-id (ID воркспейса)', credentials, mask_secret, lambda x: x),
        ('x_api_key', 'x_api_key (API key воркспейса)', credentials, mask_secret, lambda x: x),

        (
            'region',
            'Название региона по умолчанию[A100-MT,SR003,SR004,SR005,SR006,SR008]', config, lambda x: x, lambda x: x,
        ),

        ('output', 'Формат вывода по умолчанию [json|text]', config, lambda x: x, lambda x: x),
        ('endpoint_url', 'https://адрес_api', config, lambda x: x or ENDPOINT_URL, lambda x: x or ENDPOINT_URL),
    ]
    for key, prompt, cfg_obj, value_modifier, store_modifier in fields:
        current_value = cfg_obj.get(profile_name, key, fallback='')
        user_value = get_user_input(prompt, value_modifier(current_value), store_modifier(current_value))
        cfg_obj.set(profile_name, key, user_value)


def prepare_profile(profile_name, password=None):
    """Подготавливает указанный профиль для записи.

    Функция проверяет наличие секции профиля в файлах конфигурации и создаёт её,
    если она отсутствует.

    Аргументы:
        profile_name (str): Имя профиля, который загружается.

    Возвращает:
        tuple:
            config (ConfigParser): Объект конфигурации с настройками.
            credentials (ConfigParser): Объект конфигурации с учётными данными.
            password: (str): Пароль для расшифровки файла с учётными данными пользователя.
    """
    try:
        config, credentials = load_saved_config(password)
    except DecryptionError as er:
        raise er
    except Exception as er:
        click.echo(error_format('Профиль не загружен !'))
        raise ConfigReadError(er) from er

    for section in config, credentials:
        if not section.has_section(profile_name):
            section.add_section(profile_name)
    return config, credentials


def save_profile(config, credentials, password=None):
    """Сохраняет конфигурационные данные и учётные данные в файлы профиля.

    Функция создаёт необходимые директории (если они отсутствуют) и записывает
    данные конфигурации и учётных записей в файлы `CONFIG_FILE` и `CREDENTIALS_FILE`.

    Аргументы:
        config (ConfigParser): Объект конфигурации с настройками пользователя.
        credentials (ConfigParser): Объект конфигурации с учётными данными пользователя.
        password (str): Пароль шифрования, если задан данные credentials шифруются перед записью.

    Возвращает:
        None
    """
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)

    with open(CONFIG_FILE, 'w', encoding='utf-8') as config_file:
        config.write(config_file)

    fp = StringIO()
    credentials.write(fp)

    if password:
        with open(ENCRYPTED_CREDENTIALS_FILE, 'wb') as cred_file:
            cred_file.write(enc(fp.getvalue(), password))
    else:
        with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as cred_file:
            cred_file.write(fp.getvalue())
