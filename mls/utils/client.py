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


def create_client_stable_rules(profile: dict[str, Any], endpoint_url: str = '') -> dict[str, Any]:
    """Собирает общие параметры авторизации и endpoint для API-клиента."""
    return {
        'client_id': profile.get('key_id', ''),
        'client_secret': profile.get('key_secret', ''),
        'x_workspace_id': profile.get('x_workspace_id'),
        'x_api_key': profile.get('x_api_key'),
        'endpoint_url': endpoint_url or profile.get('endpoint_url', ''),
    }


def create_configured_client(
    client_class: Type[T],
    profile: dict[str, Any],
    debug: bool = False,
    endpoint_url: str = '',
    output: str | None = None,
) -> T:
    """Создает API-клиент из профиля и CLI-опций."""
    client: T = create_client_instance(
        client_class,
        debug=debug,
        **create_client_stable_rules(profile, endpoint_url=endpoint_url),
    )
    client.USER_OUTPUT_PREFERENCE = output or profile.get('output', 'json')
    return client


def common_api_client_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Добавляет общие CLI-опции API-клиента."""
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

    return func


def api_client(client_class: Type[T]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор создающий api client instance на базе ввода пользователя."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def init_client(*args: Any, **kwargs: Any) -> Any:
            """Инициализация PublicApi client."""
            profile = read_profile(kwargs.pop('profile', None))
            client = create_configured_client(
                client_class,
                profile,
                debug=kwargs.pop('debug', False),
                endpoint_url=kwargs.pop('endpoint_url', ''),
                output=kwargs.pop('output', None),
            )

            return func(client, *args, **kwargs)

        return common_api_client_options(init_client)

    return decorator
