"""Описание интерфейса сохранения профиля."""
import click

from .help import ConfigureHelp
from .utils import configure_profile


@click.command(cls=ConfigureHelp)
@click.option('-P', '--profile', default=None,  help='Имя профиля')
@click.option('-E', '--encrypt', is_flag=True, default=False,  help='Шифрование профиля')
def configure(profile, encrypt):
    """Команда настройки конфигурации профиля пользователя.

    Если профиль не указан, используется профиль по умолчанию ('default').

    Синтаксис:
        mls configure --profile [name]
        mls configure --profile [name] --encrypt
    """
    configure_profile(profile, encrypt)
