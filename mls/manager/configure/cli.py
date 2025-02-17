"""Описание интерфейса сохранения профиля."""
import click

from .help import ConfigureHelp
from .utils import configure_profile


@click.command(cls=ConfigureHelp)
@click.option('--profile', default=None,  help='Имя профиля')
def configure(profile):
    """Команда настройки конфигурации профиля пользователя.

    Если профиль не указан, используется профиль по умолчанию ('default').
    Документация по настройкам профиля:
        https://cloud.ru/docs/aicloud/mlspace/concepts/guides/guides__profile/profile__develop-func.html.

    Синтаксис: mls configure --profile [name]
    """
    configure_profile(profile)
