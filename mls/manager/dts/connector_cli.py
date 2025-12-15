"""Описание интерфейса управления коннекторами."""
from dataclasses import asdict

import click

from mls.manager.dts.custom_types import CONNECTOR_FIELDS
from mls.manager.dts.custom_types import ConnectorInput
from mls.manager.dts.custom_types import OptionalOptions
from mls.manager.dts.decorators import arg_connector_ids
from mls.manager.dts.decorators import opt_all_connector_types
from mls.manager.dts.decorators import opt_connector_id
from mls.manager.dts.decorators import opt_connector_id_prompt
from mls.manager.dts.decorators import opt_custom_connector_type
from mls.manager.dts.decorators import opt_json_output_format
from mls.manager.dts.decorators import opt_output_format
from mls.manager.dts.decorators import opt_page_number
from mls.manager.dts.decorators import opt_page_size
from mls.manager.dts.help import ConnectorActivateHelp
from mls.manager.dts.help import ConnectorCreateHelp
from mls.manager.dts.help import ConnectorDeactivateHelp
from mls.manager.dts.help import ConnectorDeleteHelp
from mls.manager.dts.help import ConnectorHelp
from mls.manager.dts.help import ConnectorListHelp
from mls.manager.dts.help import ConnectorSourcesHelp
from mls.manager.dts.help import ConnectorUpdateHelp
from mls.manager.dts.table import DataTransferTableView
from mls.manager.dts.table import display_connectors
from mls.manager.dts.utils import client
from mls.manager.dts.utils import collect_connector_params
from mls.manager.dts.utils import process_json
from mls.manager.dts.utils import validate_connector_exists
from mls.utils.common_types import RussianChoice
from mls.utils.style import success_format
from mls_core.client import DTSApi


@click.group(cls=ConnectorHelp)
def connector():
    """Группа команд (входная точка) для работы с коннекторами.

    Синтаксис: mls connector [command] [args] [options]
    """


@connector.command(cls=ConnectorListHelp, name='list')
@opt_all_connector_types
@arg_connector_ids
@opt_output_format
@click.option(
    '--field',
    'fields',
    cls=OptionalOptions,
    type=RussianChoice(CONNECTOR_FIELDS),
    multiple=True,
    default=None,
    help=f'Выбор параметров коннектора для отображения. {RussianChoice(CONNECTOR_FIELDS).options}',
)
@opt_page_size
@opt_page_number
@client
def list_(
    api: DTSApi,
    connector_type: str,
    connector_ids: str,
    page_size: int,
    page_number: int,
    fields: list,
):
    """Команда просмотра списка коннекторов.

    Синтаксис: mls connector list [args] [options]

    Пример: mls connector list 8ad28362-e7cf-401f-8057-d80e8e3d8069 --field created --field parameters --field system
    """
    connectors_list = api.conn_list(connector_ids, connector_type)
    if api.USER_OUTPUT_PREFERENCE == 'json':
        process_json(connectors_list, page_number, page_size)

    else:
        result = DataTransferTableView(
            connectors_list,
            filters=[],
            sorters=[],
            schema=display_connectors,
            fields=fields or [],
        ).display()
        click.echo(success_format(result))


@connector.command(cls=ConnectorCreateHelp, name='create')
@opt_custom_connector_type
@opt_json_output_format
@click.option(
    '--public',
    is_flag=True,
    help='Публичный коннектор (доступен всем пользователям воркспейса)',
    default=False,
    cls=OptionalOptions,
)
@client
def create(api: DTSApi, connector_type: str, public: bool):
    """Команда создания нового коннектора.

    Синтаксис: mls connector create [options]

    Пример: mls connector create --connector-type s3custom
    """
    u_input = collect_connector_params(connector_type)
    conn = ConnectorInput(**asdict(u_input), source_type=connector_type)
    click.echo(success_format(api.conn_create(conn, public)))


@connector.command(cls=ConnectorUpdateHelp, name='update')
@opt_custom_connector_type
@opt_connector_id_prompt
@opt_output_format
@client
def update(api, connector_id, connector_type):
    """Команда обновления коннектора.

    Синтаксис: mls connector update [options]

    Пример: mls connector update --connector-id 51576044-64c7-41ea-9983-edafab55828b --connector-type s3custom
    """
    if not validate_connector_exists(api, connector_id, connector_type):
        raise click.exceptions.BadParameter('коннектор не найден')

    click.echo('коннектор найден')

    user_input = collect_connector_params(connector_type)
    click.echo(
        success_format(api.conn_update(connector_id, connector_type, user_input)),
    )


@connector.command(cls=ConnectorActivateHelp, name='activate')
@opt_custom_connector_type
@opt_connector_id
@opt_output_format
@client
def activate(api: DTSApi, connector_id: str, connector_type: str):
    """Команда активации коннектора.

    Синтаксис: mls connector activate [options]

    Пример: mls connector activate --connector-type s3custom --connector-id 48173044-64b7-41eb-9993-edafab55828c
    """
    click.echo(success_format(api.conn_activate(connector_id, connector_type)))


@connector.command(cls=ConnectorDeactivateHelp, name='deactivate')
@opt_custom_connector_type
@opt_connector_id
@opt_output_format
@client
def deactivate(api: DTSApi, connector_id: str, connector_type: str):
    """Команда деактивации коннектора.

    Синтаксис: mls connector deactivate [options]

    Пример: mls connector deactivate --connector-type s3custom --connector-id 48173044-64b7-41eb-9993-edafab55828c
    """
    click.echo(success_format(api.conn_deactivate(connector_id, connector_type)))


@connector.command(cls=ConnectorDeleteHelp, name='delete')
@arg_connector_ids
@opt_output_format
@client
def delete(api: DTSApi, connector_ids: list):
    """Команда удаления коннектора.

    Синтаксис: mls connector delete [args]

    Пример: mls connector delete 48173044-64b7-41eb-9993-edafab55828c
    """
    click.echo(success_format(api.conn_delete(connector_ids)))


@connector.command(cls=ConnectorSourcesHelp, name='sources')
@opt_output_format
@client
def sources(api: DTSApi):
    """Команда получения схем возможных типов коннектора.

    Синтаксис: mls connector sources

    Пример: mls connector sources
    """
    click.echo(success_format(api.conn_sources()))
