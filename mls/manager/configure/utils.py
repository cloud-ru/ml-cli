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

import click

from mls.utils.common import load_saved_config
from mls.utils.execption import ConfigWriteError
from mls.utils.settings import CONFIG_FILE
from mls.utils.settings import CREDENTIALS_FILE
from mls.utils.settings import DEFAULT_PROFILE
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


def configure_profile(profile=None):
    """Конфигурация профиля пользователя через CLI.

    Функция инициализирует процесс настройки профиля, собирает необходимые
    данные от пользователя и сохраняет конфигурацию и учётные данные.

    Аргументы:
        profile (str, optional): Имя профиля для конфигурации. Если не указано, используется профиль по умолчанию.

    Возвращает:
        None
    """
    profile_name = profile or DEFAULT_PROFILE

    config, credentials = prepare_profile(profile_name)
    collect_user_inputs(config, credentials, profile_name)
    try:
        save_profile(config, credentials)
    except Exception as er:
        click.echo(error_format('Профиль не сохранен !'))
        raise ConfigWriteError(er)

    click.echo(success_format(f"Профиль '{profile_name}' успешно сохранен!"))


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
        ('mls_apikey_id', 'MLS API key ID', credentials, mask_secret),
        ('mls_apikey_secret', 'MLS API key secret', credentials, mask_secret),
        ('workspace_id', 'Workspace ID', credentials, mask_secret),
        ('x_api_key', 'Workspace API key', credentials, mask_secret),

        ('region', 'Default region name', config, lambda x: x),
        ('output', 'Default output format [json|text]', config, lambda x: x),
    ]

    for key, prompt, cfg_obj, value_modifier in fields:
        current_value = cfg_obj.get(profile_name, key, fallback='')
        user_value = get_user_input(prompt, value_modifier(current_value), current_value)
        cfg_obj.set(profile_name, key, user_value)


def prepare_profile(profile_name):
    """Подготавливает указанный профиль для записи.

    Функция проверяет наличие секции профиля в файлах конфигурации и создаёт её,
    если она отсутствует.

    Аргументы:
        profile_name (str): Имя профиля, который загружается.

    Возвращает:
        tuple:
            config (ConfigParser): Объект конфигурации с настройками.
            credentials (ConfigParser): Объект конфигурации с учётными данными.
    """
    config, credentials = load_saved_config()
    for section in config, credentials:
        if not section.has_section(profile_name):
            section.add_section(profile_name)
    return config, credentials


def save_profile(config, credentials):
    """Сохраняет конфигурационные данные и учётные данные в файлы профиля.

    Функция создаёт необходимые директории (если они отсутствуют) и записывает
    данные конфигурации и учётных записей в файлы `CONFIG_FILE` и `CREDENTIALS_FILE`.

    Аргументы:
        config (ConfigParser): Объект конфигурации с настройками пользователя.
        credentials (ConfigParser): Объект конфигурации с учётными данными пользователя.

    Возвращает:
        None
    """
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
    with open(CREDENTIALS_FILE, 'w') as cred_file:
        credentials.write(cred_file)
    with open(CONFIG_FILE, 'w') as config_file:
        config.write(config_file)
