"""Декораторы для функций команд."""
import click

from mls.manager.job.constants import job_statuses
from mls.manager.job.custom_types import cluster_key_input
from mls.manager.job.custom_types import ProfileOptions
from mls.manager.job.custom_types import status_inputs
from mls.utils.common_types import PositiveIntWithZeroView
from mls.utils.common_types import RussianChoice

status_of_task = click.option(
    '-s',
    '--status',
    multiple=True,
    type=RussianChoice(job_statuses),
    help=f'Статусы задач. {status_inputs.options}',
    default=None,
)

regions_selected = click.option(
    '-R', '--region',
    cls=ProfileOptions,
    index=0,
    type=cluster_key_input,
    help=f'Ключ региона. {cluster_key_input.options}',
)

limit_selected = click.option(
    '-l',
    '--limit',
    help='Лимит отображения количества задач',
    default=6000, type=PositiveIntWithZeroView(),
)

offset_selected = click.option(
    '-o',
    '--offset',
    help='Смещение относительно начала списка',
    default=0, type=PositiveIntWithZeroView(),
)


queue_selected = click.option(
    '-q',
    '--queue',
    multiple=False,
    help='ID очереди. Чтобы узнать ID очереди, выполните mls allocation list, затем mls queue list <allocation-id>',
    default=None,
)

date_begin_selected = click.option(
    '-b',
    '--start_date',
    multiple=False,
    help='Начальная дата и время для фильтрации данных в формате ISO. Если end_date не указан, система использует текущую дату и время',
    default=None,
    type=click.DateTime(),
)

date_end_selected = click.option(
    '-e',
    '--end_date',
    multiple=False,
    help='Конечная дата и время для фильтрации данных в формате ISO',
    default=None,
    type=click.DateTime(),
)
