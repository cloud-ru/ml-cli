"""Описание интерфейса сохранения профиля."""
import click

from .custom_types import ConfigureAdditionalOptions
from .help import ConfigureHelp
from .utils import configure_profile


@click.command(cls=ConfigureHelp)
@click.option('-P', '--profile', cls=ConfigureAdditionalOptions, default=None,  help='Имя профиля')
@click.option('-E', '--encrypt', cls=ConfigureAdditionalOptions, is_flag=True, default=False,  help='Шифрование профиля')
def configure(profile, encrypt):
    """Команда настройки конфигурации профиля пользователя. Если профиль не указан, используется профиль по умолчанию default.

    Синтаксис:
        mls configure [options]

    Пример:
        mls configure --profile name --encrypt
    """
    configure_profile(profile, encrypt)
