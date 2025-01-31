"""Вспомогательные утилиты для модуля управления задачами.

Этот модуль предоставляет различные вспомогательные функции и утилиты,
используемые в разных частях модуля управления задачами. Включает в себя
функции для обработки данных, валидации входных значений, форматирования
вывода и прочие общие инструменты, необходимые для выполнения задач.
"""
from configparser import NoSectionError
from functools import update_wrapper

import click
import yaml  # type: ignore

from .custom_types import json
from .custom_types import output_choice
from mls.utils.common import load_saved_config
from mls.utils.execption import ConfigReadError
from mls.utils.settings import DEFAULT_PROFILE
from mls.utils.settings import MLSPACE_PUBLIC_API_URL
from mls_core import TrainingJobApi


def common_cli_options(func):
    """Декоратор для добавления общих опций."""
    # Высший приоритет ближе к пользователю консоль
    func = click.option('--region', help='Название кластера')(func)

    # Средний приоритет загрузка из файла
    func = click.option('--profile', default=DEFAULT_PROFILE, help='Название конфигурации пользователя')(func)

    # Опции имеющие умолчания
    func = click.option('--output', type=output_choice, help='Формат вывода в консоль')(func)
    func = click.option('--endpoint_url', default=MLSPACE_PUBLIC_API_URL, help='Базовый адрес API')(func)
    func = click.option('--debug', is_flag=True, help='Вывод в консоль отладочной информации')(func)

    return func


def job_client(func):
    """Декоратор создающий api client instance на базе ввода пользователя."""

    @common_cli_options
    def init_client(*args, **kwargs):
        """Инициализация PublicApi client."""
        profile = read_profile(kwargs.pop('profile'))

        have_defaults = dict(
            debug=kwargs.pop('debug'),
            endpoint_url=kwargs.pop('endpoint_url'),

        )

        stable_rules = dict(
            client_id=profile.get('mls_apikey_id', ''),
            client_secret=profile.get('mls_apikey_secret', ''),
            workspace_id=profile.get('workspace_id'),
            x_api_key=profile.get('x_api_key'),

        )

        calculated_options = dict(region=kwargs.pop('region') or profile.get('region', ''))
        client = TrainingJobApi(**have_defaults, **stable_rules)
        client.USER_OUTPUT_PREFERENCE = kwargs.pop('output', None) or profile.get('output', json)

        return func(client, *args, **kwargs, **calculated_options)

    return update_wrapper(init_client, func)


def read_profile(profile_name):
    """Загружает (только существующий) профиль.

    Функция проверяет наличие секции профиля в файлах конфигурации и создаёт её,
    если она отсутствует.

    Аргументы:
        profile_name (str): Имя профиля, который загружается.

    Возвращает:
        dict : Собранный в словарь профиль
    """
    config, credentials = load_saved_config()
    try:
        return {**dict(config.items(profile_name)), **dict(credentials.items(profile_name))}
    except NoSectionError as err:
        raise ConfigReadError(f'Нет секции с названием {err.section}')


def read_yaml(file_path: str):
    """Читает YAML файл и возвращает содержимое в виде словаря."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise click.ClickException(
            f"Ошибка чтения YAML файла '{file_path}': {e}",
        )
