"""Общие декораторы для функций команд."""
import click

from mls.manager.job.custom_types import ProfileOptions
from mls.utils.common_types import config_option_format_of_output


opt_output_format = click.option(
    '-O',
    '--output',
    cls=ProfileOptions,
    index=1,
    type=config_option_format_of_output,
    help=f'Формат вывода в консоль. {config_option_format_of_output.options}',
    default='json',
)
