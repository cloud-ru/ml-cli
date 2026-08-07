"""Shared CLI layer for Jupyter Server and TensorBoard managers."""
import inspect
import json
from functools import update_wrapper
from typing import Any
from typing import Callable
from typing import Type
from typing import TypeVar

import click

import mls.utils.client as client_utils
from mls.utils.settings import DEFAULT_PROFILE
from mls_core.client import CommonPublicApiInterface

T = TypeVar('T', bound=CommonPublicApiInterface)


class GroupedOption(click.Option):
    """Базовая опция с группировкой для help-output notebook-сервисов."""

    GROUP: str = ''
    GROUP_INDEX = 0
    INTEND = 0

    def __init__(self, *args, index=0, **kwargs):
        """Метод включения сортировки внутри класса."""
        super().__init__(*args, **kwargs)
        self.group = self.GROUP
        self.group_index = self.GROUP_INDEX
        self.index = index
        self.intend = self.INTEND


class ProfileOptions(GroupedOption):
    """Опции профиля."""

    GROUP: str = 'Опции профиля'
    GROUP_INDEX = 11


class DebugOptions(GroupedOption):
    """Опции отладки."""

    GROUP: str = 'Опции отладки'
    GROUP_INDEX = 100


def common_cli_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Декоратор для добавления общих клиентских опций notebook-сервисов."""
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
        cls=DebugOptions,
        is_flag=True,
        help='Вывод в консоль отладочной информации',
    )(func)
    return func


def notebook_service_client(client_class: Type[T]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Создаёт Click-декоратор API-клиента для Jupyter Server и TensorBoard."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:

        @common_cli_options
        def init_client(*args: Any, **kwargs: Any) -> Any:
            profile = client_utils.read_profile(kwargs.pop('profile'))
            client = client_class(
                debug=kwargs.pop('debug'),
                **client_utils.create_client_stable_rules(
                    profile,
                    endpoint_url=kwargs.pop('endpoint_url', ''),
                ),
            )
            client.USER_OUTPUT_PREFERENCE = kwargs.pop('output', None) or profile.get('output', 'json')
            calculated_options = dict(region=kwargs.pop('region', '') or profile.get('region', ''))
            signature = inspect.signature(func)
            accepts_region = 'region' in signature.parameters or any(
                param.kind == inspect.Parameter.VAR_KEYWORD
                for param in signature.parameters.values()
            )
            if accepts_region:
                kwargs.update(calculated_options)
            return func(client, *args, **kwargs)

        return update_wrapper(init_client, func)

    return decorator


def parse_optional_json_array(value: str | None) -> list[Any] | None:
    """Парсит JSON-массив из значения опции CLI."""
    if value is None or value == '':
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f'Невалидный JSON: {exc}') from exc
    if not isinstance(parsed, list):
        raise ValueError('Ожидался JSON-массив')
    return parsed


def parse_optional_json_object(value: str | None) -> dict[str, Any] | None:
    """Парсит JSON-объект из значения опции CLI."""
    if value is None or value == '':
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f'Невалидный JSON: {exc}') from exc
    if not isinstance(parsed, dict):
        raise ValueError('Ожидался JSON-объект')
    return parsed


def parse_optional_string_mapping_json_object(value: str | None, field_name: str) -> dict[str, str] | None:
    """Парсит JSON-объект и проверяет, что все ключи и значения являются строками."""
    parsed = parse_optional_json_object(value)
    if parsed is None:
        return None
    if not all(isinstance(key, str) and isinstance(item, str) for key, item in parsed.items()):
        raise ValueError(f'Поле {field_name} должно быть словарём со строковыми ключами и значениями')
    return parsed


def resolve_region(region: str | None, profile_region: str | None) -> str:
    """Возвращает регион из CLI/YAML или профиля пользователя."""
    if region:
        return region
    if profile_region:
        return profile_region
    raise ValueError(
        'Не задан регион. Передайте --region, укажите region в манифесте '
        'или настройте region в профиле.',
    )


def click_parse_optional_json_array(
    _ctx: click.Context,
    _param: click.Parameter,
    value: str | None,
) -> list[Any] | None:
    """Обёртка Click: парсинг JSON-массива."""
    try:
        return parse_optional_json_array(value)
    except ValueError as exc:
        raise click.BadParameter(str(exc)) from exc


def click_parse_optional_json_object(
    _ctx: click.Context,
    _param: click.Parameter,
    value: str | None,
) -> dict[str, Any] | None:
    """Обёртка Click: парсинг JSON-объекта."""
    try:
        return parse_optional_json_object(value)
    except ValueError as exc:
        raise click.BadParameter(str(exc)) from exc


def click_parse_optional_string_mapping_json_object(
    field_name: str,
) -> Callable[[click.Context, click.Parameter, str | None], dict[str, str] | None]:
    """Создаёт Click callback для JSON-объекта со строковыми ключами и значениями."""

    def callback(
        _ctx: click.Context,
        _param: click.Parameter,
        value: str | None,
    ) -> dict[str, str] | None:
        try:
            return parse_optional_string_mapping_json_object(value, field_name)
        except ValueError as exc:
            raise click.BadParameter(str(exc)) from exc

    return callback
