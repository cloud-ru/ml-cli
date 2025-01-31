"""Описание интерфейса сохранения профиля."""
import click

from .help import ConfigureHelp
from .utils import configure_profile


@click.command(cls=ConfigureHelp)
@click.option('--profile', default=None,  help='Имя профиля')
def configure(profile):
    """Команда конфигурации профиля пользователя.

    Позволяет настраивать профили конфигурации для системы MLS.

    Если профиль не указан, используется профиль по умолчанию.

    Пример: mls configure --profile [name]
    """
    configure_profile(profile)
