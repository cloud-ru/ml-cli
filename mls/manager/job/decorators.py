"""Декораторы для функций команд."""
import click

from mls.manager.job.constants import job_statuses
from mls.manager.job.custom_types import cluster_key_input
from mls.manager.job.custom_types import ProfileOptions
from mls.manager.job.custom_types import status_inputs
from mls.utils.common_types import config_option_format_of_output
from mls.utils.common_types import PositiveIntWithZeroView
from mls.utils.common_types import RussianChoice

opt_output_format = click.option(
    '-O',
    '--output',
    cls=ProfileOptions,
    index=1,
    type=config_option_format_of_output,
    help=f'Формат вывода в консоль. {config_option_format_of_output.options}',
    default='json',
)

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
    help='ID очереди',
    default=None,
)
