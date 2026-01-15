"""Модуль CLI для управления очередями MLS."""
import uuid

import click

from .help import InstTypesHelp
from .help import ListHelp
from .help import QueueHelp
from mls.manager.job.decorators import opt_output_format
from mls.utils.client import api_client
from mls.utils.style import success_format
from mls_core import QueueApi


@click.group(cls=QueueHelp)
def queue():
    """Группа команд (входная точка) для работы с очередями.

    Синтаксис: mls queue [command] [args] [options]

    """


@queue.command(cls=ListHelp, name='list')
@click.argument('allocation_id')
@opt_output_format
@api_client(QueueApi)
def list_(api: QueueApi, allocation_id: uuid.UUID):
    """Команда отображения доступных очередей.

    Синтаксис: mls queue list [allocation_id] [options]

    Пример: mls queue list 00000000-0000-4000-8000-000000000000

    """
    click.echo(success_format(api.get_list_queues_by_allocation_id(str(allocation_id))))


@queue.command(cls=InstTypesHelp)
@click.argument('queue_id')
@opt_output_format
@api_client(QueueApi)
def inst_types(api: QueueApi, queue_id: uuid.UUID):
    """Команда отображения доступных инстанс типов в очереди.

    Синтаксис: mls queue inst-types [queue_id] [options]

    Пример: mls queue inst-types 00000000-0000-4000-8000-000000000000

    """
    click.echo(success_format(api.get_instance_types_by_queue_id(queue_id)))
