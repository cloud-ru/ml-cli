"""Модуль утилит клиента для MLS CLI."""
from functools import wraps
from typing import Any
from typing import Callable
from typing import Type
from typing import TypeVar

import click

from mls.manager.job.custom_types import JobDebugOptions
from mls.manager.job.custom_types import ProfileOptions
from mls.utils.common import read_profile
from mls.utils.settings import DEFAULT_PROFILE
from mls_core.client import CommonPublicApiInterface

T = TypeVar('T', bound=CommonPublicApiInterface)


def create_client_instance(client_class: Type[T], **kwargs) -> T:
    """Фабричная функция для создания экземпляра клиента."""
    return client_class(**kwargs)


def api_client(client_class: Type[T]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор создающий api client instance на базе ввода пользователя."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func = click.option(
            '-P',
            '--profile',
            cls=ProfileOptions,
            index=4,
            default=DEFAULT_PROFILE,
            help='Определение параметров региона, формата вывода по имени профиля',
        )(func)

        func = click.option(
            '-E',
            '--endpoint_url',
            cls=ProfileOptions,
            index=2,
            help='Базовый адрес API',
        )(func)

        func = click.option(
            '-D',
            '--debug',
            cls=JobDebugOptions,
            is_flag=True,
            help='Вывод в консоль отладочной информации',
        )(func)

        @wraps(func)
        def init_client(*args: Any, **kwargs: Any) -> Any:
            """Инициализация PublicApi client."""
            profile = read_profile(kwargs.pop('profile', None))

            have_defaults = dict(
                debug=kwargs.pop('debug', False),
            )
            stable_rules = dict(
                client_id=profile.get('key_id', ''),
                client_secret=profile.get('key_secret', ''),
                x_workspace_id=profile.get('x_workspace_id'),
                x_api_key=profile.get('x_api_key'),
                endpoint_url=kwargs.pop('endpoint_url', '') or profile.get('endpoint_url', ''),
            )
            client: T = create_client_instance(client_class, **have_defaults, **stable_rules)
            client.USER_OUTPUT_PREFERENCE = kwargs.pop('output', None) or profile.get('output', 'json')

            return func(client, *args, **kwargs)

        return init_client

    return decorator
