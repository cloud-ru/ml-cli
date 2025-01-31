"""Описание общих функций."""
from configparser import ConfigParser

import click

from .settings import CONFIG_FILE
from .settings import CREDENTIALS_FILE
from .style import error_format


def load_saved_config():
    """Загружает в память пользовательские настройки файлов (профиля) config, credentials.

    Возвращает:
        tuple:
            config (ConfigParser): Объект конфигурации с настройками.
            credentials (ConfigParser): Объект конфигурации с учётными данными.
    """
    config, credentials = ConfigParser(), ConfigParser()
    config.read(CONFIG_FILE)
    credentials.read(CREDENTIALS_FILE)
    return config, credentials


def handle_click_exception(error: click.ClickException, ctx: click.Context):
    """Обработка исключений Click и вывод соответствующих сообщений об ошибках."""
    message = error.format_message()

    # Замена стандартных сообщений на пользовательские
    message_mappings = {
        'Got unexpected extra arguments': 'Получены не поддерживаемы аргументы',
        'Got unexpected extra argument': 'Получен не поддерживаемый аргумент',
        'No such command': 'Нет такой команды',
        'does not take a value': 'не принимает значений',
        'Invalid value for': 'Не верное значение для',
        'is not one of': 'не входит в перечень',
        'is not': 'не является',
        'Option': 'Опция',
        'requires': 'требует',
        'arguments': 'аргументов',
        'argument': 'аргумента',
        'does not exist': 'указанного пути не существует',
    }

    for original, custom in message_mappings.items():
        message = message.replace(original, custom)

    if isinstance(error, click.MissingParameter):
        param_name = error.param.name if error.param else ''
        message = f'Ошибка: отсутствует параметр: {param_name}'
    elif isinstance(error, click.NoSuchOption):
        option_name = error.option_name or ''
        message = f'Ошибка: отсутствует опция: {option_name}'
    elif isinstance(error, click.BadParameter):
        message = message
    elif isinstance(error, click.UsageError):
        message = message

    if ctx:
        click.echo(f'{ctx.get_help()}')
    click.echo(error_format(message))
