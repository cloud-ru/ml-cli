"""Вспомогательные утилиты для модуля управления правилами переноса."""
import json
from functools import update_wrapper

import click

from mls.manager.dts.custom_types import Connector
from mls.manager.dts.custom_types import DB_LIKE_CONNECTOR_TYPES
from mls.manager.dts.custom_types import S3_LIKE_CONNECTOR_TYPES
from mls.manager.dts.custom_types import S3Type
from mls.manager.dts.custom_types import SQLType
from mls.manager.job.custom_types import JobDebugOptions
from mls.manager.job.custom_types import ProfileOptions
from mls.utils.common import read_profile
from mls.utils.settings import DEFAULT_PROFILE
from mls.utils.style import success_format
from mls_core.client import DTSApi


def common_cli_options(func):
    """Декоратор для добавления общих опций."""
    func = click.option(
        '-P',
        '--profile',
        cls=ProfileOptions,
        index=4,
        default=DEFAULT_PROFILE,
        help='Определение параметров региона, формата вывода по имени профиля',
    )(func)

    func = click.option(
        '-E', '--endpoint_url', cls=ProfileOptions, index=2, help='Базовый адрес API',
    )(func)
    func = click.option(
        '-D',
        '--debug',
        cls=JobDebugOptions,
        is_flag=True,
        help='Вывод в консоль отладочной информации',
    )(func)
    return func


def client(func):
    """Декоратор создающий api client instance на базе ввода пользователя."""
    @common_cli_options
    def _init(*args, **kwargs):
        """Инициализация клиента PublicApi."""
        profile = read_profile(kwargs.pop('profile'))

        have_defaults = dict(
            debug=kwargs.pop('debug'),
        )
        stable_rules = dict(
            client_id=profile.get('key_id', ''),
            client_secret=profile.get('key_secret', ''),
            x_workspace_id=profile.get('x_workspace_id'),
            x_api_key=profile.get('x_api_key'),
            endpoint_url=kwargs.pop('endpoint_url', '') or profile.get('endpoint_url'),
        )
        dts_client = DTSApi(**have_defaults, **stable_rules)
        dts_client.USER_OUTPUT_PREFERENCE = kwargs.pop('output', None) or profile.get(
            'output', 'json',
        )

        return func(dts_client, *args, **kwargs)

    return update_wrapper(_init, func)


def collect_connector_params(connector_type: str) -> Connector:
    """Функция сбора параметров коннектора."""
    params: S3Type | SQLType | None = None
    if connector_type in S3_LIKE_CONNECTOR_TYPES:
        params = S3Type(
            endpoint=click.prompt('Endpoint'),
            bucket=click.prompt('S3 Bucket'),
            access_key_id=click.prompt('S3 Access Key', hide_input=True),
            security_key=click.prompt('S3 Secret Key', hide_input=True),
        )

    elif connector_type in DB_LIKE_CONNECTOR_TYPES:
        params = SQLType(
            user=click.prompt('user'),
            password=click.prompt('password', hide_input=True),
            database=click.prompt('database'),
            host=click.prompt('host'),
            port=click.prompt('port', type=click.IntRange(0, 65535)),
        )

    return Connector(name=click.prompt('Имя коннектора'), parameters=params)


def validate_connector_exists(api, connector_id, connector_type):
    """Проверяет наличие коннектора."""
    try:
        conn_list = api.conn_list(connector_ids=[connector_id], typ=connector_type)
        if isinstance(conn_list, str):
            conn_list = json.loads(conn_list)

    except Exception as e:
        raise click.exceptions.UsageError(
            f'Не удалось проверить доступность коннектора с ID: {connector_id}',
        ) from e

    if isinstance(conn_list, list) and len(conn_list) == 1:
        return conn_list[0].get('connector_id') == connector_id

    return False


def paginate(data, page, per_page):
    """Отображает одну страницу данных."""
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    try:
        click.echo(
            success_format(
                json.dumps(data[start_idx:end_idx], indent=4, ensure_ascii=False),
            ),
        )

        if end_idx < len(data):
            return

    except Exception as e:
        raise click.ClickException(message=str(e))


def process_json(data: str, page_number: int, page_size: int):
    """Обработка и вывод данных в формате JSON."""
    if page_size and page_number:
        data = json.loads(data)
        click.echo(paginate(data=data, page=page_number, per_page=page_size))
    else:
        click.echo(success_format(data))


def validate_ints(ctx, param, value, min_val, max_val):
    """Проверка вхождения значения в обозначенные границы."""
    _ = ctx, param
    if value is None:
        return None

    if not min_val <= value <= max_val:
        raise click.BadParameter(
            f'Число должно быть в пределах от {min_val} до {max_val}',
        )

    return value
