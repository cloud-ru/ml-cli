"""Вспомогательные утилиты для модуля управления правилами переноса."""
import json
from functools import wraps

import click

from mls.manager.dts.custom_types import Connector
from mls.manager.dts.custom_types import DB_LIKE_CONNECTOR_TYPES
from mls.manager.dts.custom_types import S3_LIKE_CONNECTOR_TYPES
from mls.manager.dts.custom_types import S3Type
from mls.manager.dts.custom_types import SQLType
from mls.utils.client import common_api_client_options
from mls.utils.client import create_configured_client
from mls.utils.common import read_profile
from mls.utils.style import success_format
from mls_core.client import DTSApi


def client(func):
    """Декоратор создающий api client instance на базе ввода пользователя."""
    @wraps(func)
    def init_client(*args, **kwargs):
        """Инициализация клиента PublicApi."""
        profile = read_profile(kwargs.pop('profile', None))
        dts_client = create_configured_client(
            DTSApi,
            profile,
            debug=kwargs.pop('debug', False),
            endpoint_url=kwargs.pop('endpoint_url', ''),
            output=kwargs.pop('output', None),
        )

        return func(dts_client, *args, **kwargs)

    return common_api_client_options(init_client)


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
