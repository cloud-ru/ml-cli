"""Декораторы для функций команд."""
import click

from mls.manager.dts.custom_types import ALL_CONNECTOR_TYPES
from mls.manager.dts.custom_types import CUSTOM_CONNECTOR_TYPES
from mls.manager.dts.custom_types import OptionalOptions
from mls.manager.dts.custom_types import RequiredOptions
from mls.manager.job.custom_types import ProfileOptions
from mls.utils.common_types import config_option_format_of_output
from mls.utils.common_types import RussianChoice

opt_custom_connector_type = click.option(
    '--connector-type',
    help=f'Тип коннектора. {RussianChoice(CUSTOM_CONNECTOR_TYPES).options}',
    cls=RequiredOptions,
    required=True,
    type=RussianChoice(CUSTOM_CONNECTOR_TYPES),
    nargs=1,
)

opt_all_connector_types = click.option(
    '--connector-type',
    help=f'Тип коннектора. {RussianChoice(ALL_CONNECTOR_TYPES).options}',
    type=RussianChoice(ALL_CONNECTOR_TYPES),
    cls=OptionalOptions,
    default=None,
    nargs=1,
)

opt_connector_id_prompt = click.option(
    '--connector-id',
    prompt='ID коннектора',
    help='ID коннектора',
    nargs=1,
    cls=RequiredOptions,
)
opt_connector_id = click.option(
    '--connector-id',
    help='ID коннектора',
    required=True,
    cls=RequiredOptions,
    type=str,
    nargs=1,
)

opt_transfer_ids = click.option(
    '--transfer-id',
    'transfer_ids',
    required=True,
    help='ID правил переноса',
    multiple=True,
    expose_value=True,
)
opt_transfer_id = click.option(
    '--transfer-id',
    help='ID правила переноса',
    default=None,
    cls=RequiredOptions,
    required=True,
)
opt_transfer_id_optional = click.option(
    '--transfer-id',
    help='ID правила переноса',
    default=None,
    cls=OptionalOptions,
    required=False,
)
opt_source_name = click.option(
    '--source-name',
    help='Имя переносимого объекта',
    default=None,
    cls=OptionalOptions,
)
opt_history_id = click.option(
    '--history-id',
    help='ID истории правила переноса',
    default=None,
    cls=OptionalOptions,
)
arg_connector_ids = click.argument(
    'connector-ids', required=False, default=None, nargs=-1,
)
arg_transfer_ids = click.argument('transfer-ids', required=True, default=None, nargs=-1)
arg_transfer_id = click.argument('transfer-id', required=False, default=None, nargs=1)
opt_output_format = click.option(
    '-O',
    '--output',
    cls=ProfileOptions,
    index=1,
    type=config_option_format_of_output,
    help=f'Формат вывода в консоль. {config_option_format_of_output.options}',
    default='text',
)
opt_json_output_format = click.option(
    '-O',
    '--output',
    cls=ProfileOptions,
    index=1,
    type=config_option_format_of_output,
    help=f'Формат вывода в консоль. {config_option_format_of_output.options}',
    default='json',
)


def validate_positive(ctx, param, value):
    """Проверка параметра на позитивное значение."""
    _ = ctx
    if value is not None and value < 0:
        raise click.BadParameter(f'Значение {param} должно быть >= 0')

    return value


opt_page_size = click.option(
    '--page-size',
    help='Количество элементов на странице, передается совместно с --page-number',
    required=False,
    default=None,
    type=int,
    callback=validate_positive,
    cls=OptionalOptions,
)
opt_page_number = click.option(
    '--page-number',
    help='Номер страницы, передается совместно с --page-size',
    required=False,
    default=None,
    type=int,
    callback=validate_positive,
    cls=OptionalOptions,
)
