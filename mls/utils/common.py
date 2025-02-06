"""Описание общих функций."""
from configparser import ConfigParser

import click
from click import Command
from click import Group

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


def suggest_autocomplete(input_str, commands_dict):
    """Функция предположений о значении ввода пользователя."""
    suggestions = []
    # Поиск совпадений в ключах словаря
    for command in commands_dict:
        if command.startswith(input_str):
            # Добавление найденных подкоманд/параметров
            full = input_str.split(' ')
            last = full[-1]
            prev = ' '.join(full[:-1])
            items = commands_dict.get(prev, [])
            sss = [*filter(lambda x: x.startswith(last), items)]
            suggestions.extend(sss)

    return list(set(suggestions))


def create_autocomplete(start_point, command_or_group, mapping):
    """Рекурсивная функция наполняющая автозаполнения."""
    if isinstance(command_or_group, Group):
        mapping[start_point] = [str(command) for command in command_or_group.commands]
        for command_name, command_obj in command_or_group.commands.items():
            next_point = f'{start_point} {command_name}'.strip()
            create_autocomplete(next_point, command_obj, mapping)

    elif isinstance(command_or_group, Command):
        mapping[start_point] = [param.opts[0] for param in command_or_group.params if param.opts]
