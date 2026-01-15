"""Модуль CLI для управления аллокациями MLS."""
import uuid

import click

from .help import AllocationHelp
from .help import InstTypesHelp
from .help import ListHelp
from mls.manager.job.decorators import opt_output_format
from mls.utils.client import api_client
from mls.utils.style import success_format
from mls_core import AllocationApi


@click.group(cls=AllocationHelp)
def allocation():
    """Группа команд (входная точка) для работы с аллокациями.

    Синтаксис: mls allocation [command] [args] [options]

    """


@allocation.command(cls=ListHelp, name='list')
@opt_output_format
@api_client(AllocationApi)
def list_(api: AllocationApi):
    """Команда отображения доступных аллокаций.

    Синтаксис: mls allocation list [options]

    Пример: mls allocation list

    """
    click.echo(success_format(api.get_list_allocations()))


@allocation.command(cls=InstTypesHelp)
@opt_output_format
@click.argument('allocation_id')
@api_client(AllocationApi)
def inst_types(api: AllocationApi, allocation_id: uuid.UUID):
    """Команда отображения доступных инстанс типов в аллокациях.

    Синтаксис: mls allocation inst-types [allocation_id] [options]

    Пример: mls allocation inst-types 00000000-0000-4000-8000-000000000000

    """
    click.echo(success_format(api.get_instance_types_by_allocation_id(allocation_id)))
