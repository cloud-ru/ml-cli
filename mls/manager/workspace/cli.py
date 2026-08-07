"""Модуль CLI для просмотра workspaces MLS."""
import click

from .help import Workspace
from .help import WorkspaceHelp
from mls.manager.decorators import opt_output_format
from mls.utils.client import api_client
from mls.utils.style import success_format
from mls_core import WorkspaceApi


@click.group(cls=Workspace, name='ws')
def ws():
    """Группа команд (входная точка) для работы с Workspace.

    Синтаксис: mls ws [command] [args] [options]

    """


@ws.command(cls=WorkspaceHelp, name='list')
@click.option('--customer-id', default=None, help='Фильтр воркспейсов по ID пользователя')
@opt_output_format
@api_client(WorkspaceApi)
def list_(api: WorkspaceApi, customer_id: str | None):
    """Команда для отображения доступных воркспейсов.

    Синтаксис: mls ws list [options]

    Пример: mls ws list --customer-id 00000000-0000-0000-0000-000000000000

    """
    click.echo(success_format(api.get_workspaces(customer_id=customer_id)))
