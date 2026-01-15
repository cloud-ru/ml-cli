"""Описание общих функций."""
from configparser import ConfigParser
from configparser import NoSectionError

import click
from click import Command
from click import Group

from .execption import ConfigReadError
from .openssl import decrypt
from .settings import CONFIG_FILE
from .settings import CREDENTIALS_FILE
from .settings import ENCRYPTED_CREDENTIALS_FILE
from .settings import SECRET_PASSWORD
from .style import error_format


def load_saved_config(password=None):
    """Загружает в память пользовательские настройки файлов (профиля) config, credentials.

    Возвращает:
        tuple:
            config (ConfigParser): Объект конфигурации с настройками.
            credentials (ConfigParser): Объект конфигурации с учётными данными.
            password (str): Пароль для расшифровки файла с учётными данными.
    """
    config, credentials = ConfigParser(), ConfigParser()
    config.read(CONFIG_FILE)

    try:
        if password:
            with open(ENCRYPTED_CREDENTIALS_FILE, 'rb') as cred_file:
                credentials_data = decrypt(cred_file.read(), password)
        else:
            with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as cred_file:
                credentials_data = cred_file.read()
    except FileNotFoundError:
        credentials_data = ''

    credentials.read_string(credentials_data)

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
        'Invalid value for': 'Неверное значение для',
        'is not one of': 'не входит в перечень',
        'is not': 'не является',
        'Option': 'Опция',
        'requires': 'требует',
        'an argument': 'аргумента',
        'an arguments': 'аргументов',
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
            suggest = [*filter(lambda x, start=last: x.startswith(start), items)]
            suggestions.extend(suggest)

    return list(set(suggestions))


def create_autocomplete(start_point, command_or_group, mapping):
    """Рекурсивная функция наполняющая автозаполнения."""
    if isinstance(command_or_group, Group):
        mapping[start_point] = [str(command) for command in command_or_group.commands]
        for command_name, command_obj in command_or_group.commands.items():
            next_point = f'{start_point} {command_name}'.strip()
            create_autocomplete(next_point, command_obj, mapping)

    elif isinstance(command_or_group, Command):
        mapping[start_point] = [
            '--' + param.name for param in command_or_group.params if param.opts and isinstance(param, click.core.Option)
        ]


def read_profile(profile_name):
    """Загружает (только существующий) профиль.

    Функция проверяет наличие секции профиля в файлах конфигурации и создаёт её,
    если она отсутствует.

    Аргументы:
        profile_name (str): Имя профиля, который загружается.

    Возвращает:
        dict : Собранный в словарь профиль.
    """
    config, credentials = load_saved_config(SECRET_PASSWORD)
    try:
        return {**dict(config.items(profile_name)), **dict(credentials.items(profile_name))}
    except NoSectionError as err:
        error_message = (
            f'Профиль конфигурации с именем {err.section} используется по умолчанию, если конфигурация еще не задана.\n'
            'Настройте конфигурацию профиля, выполнив команду:\n'
            'mls configure\n'
            'Или export MLS_PROFILE_DEFAULT=<Ваш профиль по умолчанию>'
        )
        raise ConfigReadError(error_message) from err
