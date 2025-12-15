"""Модуль интерфейса командной строки MLS.

Данный модуль предоставляет основную точку входа для CLI-интерфейса системы MLS.
Использует кастомизированные классы `MLSHelp` и `ConfigureHelp` для форматирования
вывода справочной информации.

Команды:
    cli: Основная группа команд MLS.
    configure: Подгруппа команд для конфигурации профилей пользователя.

Примеры:
    Основная справка:
        $ python cli.py --help

    Справка по команде configure:
        $ python cli.py configure --help

    Конфигурация профиля:
        $ python cli.py configure --profile dev
"""
import sys
from typing import Any
from typing import Dict
from typing import Optional

import click
import requests
import urllib3
from requests.exceptions import MissingSchema  # type: ignore

from mls import __version__ as version
from mls.manager.allocation.cli import allocation
from mls.manager.configure.cli import configure
from mls.manager.dts.connector_cli import connector
from mls.manager.dts.transfer_cli import transfer
from mls.manager.job.cli import job
from mls.manager.queue.cli import queue
from mls.utils.cli_entrypoint_help import MLSHelp
from mls.utils.common import create_autocomplete
from mls.utils.common import handle_click_exception
from mls.utils.common import suggest_autocomplete
from mls.utils.execption import ConfigReadError
from mls.utils.execption import ConfigWriteError
from mls.utils.execption import DecryptionError
from mls.utils.execption import EncryptionError
from mls.utils.execption import MissingPassword
from mls.utils.style import error_format
from mls.utils.style import text_format
from mls_core.exceptions import AuthorizationError
from mls_core.exceptions import InvalidAuthorizationToken


@click.group(cls=MLSHelp)
@click.version_option(version, '-v', '--version', message='Версия Distributed Train CLI %(version)s')
def cli():
    """Основная точка входа для команд MLS.

    Совет:
        Настройте профиль в первую очередь. Выполните mls configure для настройки профиля по умолчанию.
    """


cli.add_command(job)
cli.add_command(configure)
cli.add_command(connector)
cli.add_command(transfer)
cli.add_command(allocation)
cli.add_command(queue)


def auto_complete_function(mapping: Optional[Dict[Any, Any]] = None):
    """Функция наполнения mls авто заполнителями."""
    if mapping is None:
        mapping = {}
    create_autocomplete('mls', cli, mapping)
    max_depth = 3

    args = sys.argv
    cleaned_arg = ' '.join([arg.strip() for arg in args if arg.strip()][1:][:max_depth])
    help_options = mapping.get(cleaned_arg, [])

    if help_options:
        sys.stdout.write('\n\u00A0\n')
        sys.stdout.write('\n'.join(help_options))
    else:
        sys.stdout.write('\n'.join(suggest_autocomplete(cleaned_arg, mapping)))


def autocomplete():
    """Входная точка для запуска autocomplete.

    Используется как complete entrypoint.

    _mls_completion() {
        autocomplete "${COMP_WORDS[@]}"
    }
    complete -F _mls_completion mls
    """
    try:
        auto_complete_function()
    except Exception:
        pass


def entry_point():
    """Входная точка для поддержки работы в рамках вызова через mls.cli (в режиме cli-приложения)."""
    try:
        cli(standalone_mode=False)
    except ConfigReadError as error:
        click.echo(error_format(str(error)))
        sys.exit(1)
    except ConfigWriteError as error:
        click.echo(error_format(str(error)))
        sys.exit(1)
    except click.ClickException as error:
        ctx = getattr(error, 'ctx', None)
        handle_click_exception(error, ctx)
        sys.exit(1)
    except click.exceptions.Abort:
        click.echo(text_format('Выполнение прервано пользователем'))
        sys.exit(1)
    except urllib3.exceptions.MaxRetryError as error:
        click.echo(error_format(f'Достигнут предел по количеству запросов к {error.url}'))
        sys.exit(1)
    except urllib3.exceptions.NameResolutionError as error:
        click.echo(error_format(f'Не удалось сопоставить IP-адрес с {error.conn.host}'))
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        click.echo(error_format('Не удалось установить соединение, проверьте настройки сети'))
        sys.exit(1)
    except AuthorizationError:
        click.echo(error_format('Попытка выполнить запрос неавторизованным пользователем'))
        sys.exit(1)
    except InvalidAuthorizationToken:
        click.echo(error_format('Неизвестная ошибка авторизации'))
        sys.exit(1)
    except DecryptionError:
        click.echo(error_format('Невозможно расшифровать учётные данные'))
        sys.exit(1)
    except EncryptionError:
        click.echo(error_format('Невозможно зашифровать учётные данные'))
        sys.exit(1)
    except BrokenPipeError as error:
        click.echo(error_format(error))
        sys.exit(1)
    except MissingSchema as error:
        click.echo(error_format(f'Не указан endpoint_url. {error.args}'))
        sys.exit(1)
    except requests.exceptions.InvalidURL as error:
        click.echo(error_format(f'Указан не валидный endpoint_url. {error.args[0]}'))
        sys.exit(1)
    except MissingPassword:
        click.echo(error_format('Пароль не может быть пустым'))
        sys.exit(1)
    except requests.exceptions.ChunkedEncodingError:
        click.echo(error_format('Сервер объявил chunked кодировку, но отправил не валидный chunk'))
        sys.exit(1)
    except Exception as er:
        click.echo(error_format(f'{er}'))
        sys.exit(2)


if __name__ == '__main__':
    # autocomplete() для debug
    entry_point()
