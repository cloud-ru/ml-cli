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
import click
import requests
import urllib3

from mls.manager.configure.cli import configure
from mls.manager.job.cli import job
from mls.utils.cli_entrypoint_help import MLSHelp
from mls.utils.common import handle_click_exception
from mls.utils.execption import ConfigReadError
from mls.utils.execption import ConfigWriteError
from mls.utils.style import error_format
from mls.utils.style import text_format


@click.group(cls=MLSHelp)
def cli():
    """Основная точка входа для команд MLS."""


cli.add_command(job)
cli.add_command(configure)


def activate_autocomplete_function():
    """Функция содержащая инструкцию включения mls <TAB> auto complete."""
    click.echo("""TODO""")


def entry_point():
    """Входная точка ядл поддержки работы в рамках вызова через mls.cli(в режиме cli приложения)."""
    try:
        cli(standalone_mode=False)
    except ConfigReadError as error:
        click.echo(error_format(str(error)))
    except ConfigWriteError as error:
        click.echo(error_format(str(error)))
    except click.ClickException as error:
        ctx = getattr(error, 'ctx', None)
        handle_click_exception(error, ctx)
    except click.exceptions.Abort:
        click.echo(text_format('Оборвано CTRL+Z'))
    except urllib3.exceptions.MaxRetryError as error:
        click.echo(error_format(f'Достигнут предел по количеству обращений к {error.url}'))
    except urllib3.exceptions.NameResolutionError as error:
        click.echo(error_format(f'Ошибка разрешения ip адреса при обращении к домену {error.conn.host}'))
    except requests.exceptions.ConnectionError:
        click.echo(error_format('Не удалось установить соединение за указанное время'))


if __name__ == '__main__':
    entry_point()
