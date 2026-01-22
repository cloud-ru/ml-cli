"""Описание интерфейса управления правилами переноса."""
from dataclasses import asdict
from datetime import datetime

import click

from mls.manager.dts.custom_types import ALL_CONNECTOR_TYPES
from mls.manager.dts.custom_types import ConnectorTarget
from mls.manager.dts.custom_types import ConnectorTypes
from mls.manager.dts.custom_types import CronViewModel
from mls.manager.dts.custom_types import OptionalOptions
from mls.manager.dts.custom_types import RequiredOptions
from mls.manager.dts.custom_types import STRATEGY
from mls.manager.dts.custom_types import TARGET_CONNECTOR_TYPES
from mls.manager.dts.custom_types import Transfer
from mls.manager.dts.custom_types import TRANSFER_FIELD_NAMES
from mls.manager.dts.custom_types import TransferCreateOptional
from mls.manager.dts.custom_types import TransferCreateRequired
from mls.manager.dts.custom_types import TransferQuery
from mls.manager.dts.decorators import arg_transfer_ids
from mls.manager.dts.decorators import opt_history_id
from mls.manager.dts.decorators import opt_output_format
from mls.manager.dts.decorators import opt_page_number
from mls.manager.dts.decorators import opt_page_size
from mls.manager.dts.decorators import opt_source_name
from mls.manager.dts.decorators import opt_transfer_id
from mls.manager.dts.decorators import opt_transfer_id_optional
from mls.manager.dts.help import TransferActivateHelp
from mls.manager.dts.help import TransferCreateHelp
from mls.manager.dts.help import TransferDeactivateHelp
from mls.manager.dts.help import TransferDeleteHelp
from mls.manager.dts.help import TransferHelp
from mls.manager.dts.help import TransferHistoryHelp
from mls.manager.dts.help import TransferListHelp
from mls.manager.dts.help import TransferLogsHelp
from mls.manager.dts.help import TransferStopHelp
from mls.manager.dts.help import TransferUpdateHelp
from mls.manager.dts.table import DataTransferTableView
from mls.manager.dts.table import display_transfers
from mls.manager.dts.utils import client
from mls.manager.dts.utils import process_json
from mls.manager.dts.utils import validate_ints
from mls.utils.common_types import RussianChoice
from mls.utils.style import success_format
from mls_core.client import DTSApi


@click.group(cls=TransferHelp)
def transfer():
    """Группа команд (входная точка) для работы с правилами переноса.

    Синтаксис: mls transfer [command] [args] [options]
    """


@transfer.command(cls=TransferCreateHelp, name='create')
@click.option('--name', help='Имя правила переноса', nargs=1, cls=TransferCreateRequired)
@click.option(
    '--connector-id',
    help='ID коннектора источника',
    nargs=1,
    cls=TransferCreateRequired,
)
@click.option(
    '--dst-connector-id',
    help='ID коннектора места назначения',
    nargs=1,
    cls=TransferCreateRequired,
)
@click.option(
    '--connector-type',
    help=f'Тип коннектора источника. {RussianChoice(ALL_CONNECTOR_TYPES).options}',
    type=RussianChoice(ALL_CONNECTOR_TYPES),
    nargs=1,
    cls=TransferCreateRequired,
)
@click.option(
    '--dst-connector-type',
    help=f'Тип коннектора места назначения. {RussianChoice(TARGET_CONNECTOR_TYPES).options}',
    type=RussianChoice(TARGET_CONNECTOR_TYPES),
    nargs=1,
    cls=TransferCreateRequired,
)
@click.option(
    '--source',
    help="Источник данных. Если источников несколько, укажите через запятую, например 'folder1/,folder5/'",
    type=str,
    required=True,
    cls=TransferCreateRequired,
)
@click.option(
    '--destination',
    help="Место назначения. Укажите как минимум корень '/'",
    type=str,
    required=True,
    cls=TransferCreateRequired,
)
@click.option(
    '--weekday',
    callback=lambda ctx, param, value: validate_ints(ctx, param, value, 1, 7),
    type=int,
    help='В какие дни недели будет повторяться (1-7, где 1 - Пн)',
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--monthday',
    callback=lambda ctx, param, value: validate_ints(ctx, param, value, 1, 31),
    help='Какого числа каждый месяц будет повторяться (1-31)',
    type=int,
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--period',
    type=int,
    help='Каждые ХХ часов будет повторяться (2 - каждые 2 часа)',
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--description',
    help='Описание правила переноса',
    type=str,
    default='',
    cls=TransferCreateOptional,
)
@click.option(
    '--cluster-name',
    help='Имя кластера',
    type=str,
    default='christofari-1',
    nargs=1,
    cls=TransferCreateOptional,
)
@click.option(
    '--strategy',
    help=f'Стратегия переноса. {RussianChoice(STRATEGY).options}',
    type=RussianChoice(STRATEGY),
    cls=TransferCreateRequired,
)
@opt_output_format
@client
def create(
    api: DTSApi,
    name: str,
    connector_id: str,
    dst_connector_id: str,
    connector_type: ConnectorTypes,
    dst_connector_type: ConnectorTarget,
    cluster_name: str,
    strategy: str,
    source: str,
    destination: str,
    weekday: str,
    monthday: str,
    period: int | None = None,
    description: str | None = None,
):  # noqa # type: ignore
    """Команда создания нового правила переноса.

    В правиле периодического переноса может быть указана только одна из опций --weekday, --monthday, --period.

    Синтаксис: mls transfer create [options]

    Пример: mls transfer create --name MyTransfer --connector-id 5f3ec6de-152b-42ec-b5f0-6c18f69c7713
 --dst-connector-id 44e6e6a8-5224-4f5e-93e6-7790dc8ea6d9 --connector-type s3custom --dst-connector-type s3custom
 --source folder1/subfolder,folder2/manifest.yaml --destination my_dest_folder --strategy write_all
    """
    source = [s.strip() for s in source.split(',')] if ',' in source else source  # type: ignore
    now = datetime.utcnow()

    u_input = Transfer(
        name=name,
        connector_id=connector_id,
        destination_connector_id=dst_connector_id,
        connector_type=connector_type,
        destination_connector_type=dst_connector_type,
        cluster_name=cluster_name,
        strategy=strategy,
        query=TransferQuery(source=source, destination=destination),
        description=description,
        crontab={'start_at': now.strftime('%Y-%m-%dT%H:%M:%S')},
    )

    schedule = {'monthdays': monthday, 'weekdays': weekday, 'period': period}
    crontab: dict[str, str | int | list[int]] = {k: v for k, v in schedule.items() if v is not None}

    if len(crontab) > 1:
        raise click.BadParameter(
            message=(
                'Для создания правила периодического переноса может быть'
                ' передана только одна из опций расписания --weekday, --monthday, --period'
            ),
        )

    crontab_fields = ('monthdays', 'weekdays')

    has_crontab_fields = any(crontab.get(field) for field in crontab_fields)
    if crontab.get('period') is not None:
        u_input.crontab['period'] = period  # type: ignore

    else:
        if has_crontab_fields:
            crontab['time'] = now.time().strftime('%H:%M')

            for field in ('weekdays', 'monthdays'):
                if field in crontab:
                    crontab[field] = [crontab[field]]  # type: ignore

            u_input.crontab.update(crontab)  # type: ignore

    click.echo(success_format(api.transfer_create(Transfer(**asdict(u_input)))))


@transfer.command(cls=TransferDeleteHelp, name='delete')
@arg_transfer_ids
@opt_output_format
@client
def delete(api, transfer_ids):
    """Команда удаления одного и более правил переноса.

    Синтаксис: mls transfer delete [args]

    Пример: mls transfer delete ebe0e039-2f8c-4d54-8298-92fbff2989ba
    """
    click.echo(success_format(api.transfer_delete(transfer_ids=transfer_ids)))


@transfer.command(cls=TransferListHelp, name='list')
@opt_output_format
@opt_page_size
@opt_page_number
@click.option(
    '--field',
    'fields',
    help=f'Выбор параметров правила переноса для отображения. {RussianChoice(TRANSFER_FIELD_NAMES.keys()).options}',
    cls=OptionalOptions,
    type=RussianChoice(TRANSFER_FIELD_NAMES.keys()),
    multiple=True,
    default=None,
)
@client
def list_(api: DTSApi, page_size: int, page_number: int, fields: list):
    """Команда получения всех правил переноса пользователя.

    Синтаксис: mls transfer list [options]

    Пример: mls transfer list --field cluster-name --field description --field source-category
    """
    transfers_list = api.transfer_list()

    if api.USER_OUTPUT_PREFERENCE == 'json':
        process_json(transfers_list, page_number, page_size)

    else:
        result = DataTransferTableView(
            transfers_list,
            filters=[],
            sorters=[],
            schema=display_transfers,
            fields=fields,
        ).display()

        click.echo(success_format(result))


@transfer.command(cls=TransferListHelp, name='get')
@opt_transfer_id
@opt_output_format
@client
def get(api: DTSApi, transfer_id: str):
    """Команда получения правила переноса.

    Синтаксис: mls transfer get [options]

    Пример: mls transfer get --transfer-id 12c408ec-a4cd-4346-8f76-7364687d14f7
    """
    click.echo(success_format(api.transfer_get(transfer_id=transfer_id)))


@transfer.command(cls=TransferActivateHelp, name='activate')
@opt_transfer_id
@opt_output_format
@client
def activate(api: DTSApi, transfer_id: str):
    """Команда активации периодического правила переноса.

    Синтаксис: mls transfer activate [options]

    Пример: mls transfer activate --transfer-id 12c408ec-a4cd-4346-8f76-7364687d14f6
    """
    click.echo(success_format(api.transfer_switch(transfer_id=transfer_id, state=True)))


@transfer.command(cls=TransferDeactivateHelp, name='deactivate')
@opt_transfer_id
@opt_output_format
@client
def deactivate(api: DTSApi, transfer_id: str):
    """Команда деактивации периодического правила переноса.

    Синтаксис: mls transfer deactivate [args] [options]

    Пример: mls transfer deactivate --transfer-id 12c408ec-a4cd-4346-8f76-7364687d14f6
    """
    click.echo(
        success_format(api.transfer_switch(transfer_id=transfer_id, state=False)),
    )


@transfer.command(cls=TransferLogsHelp, name='logs')
@opt_transfer_id
@opt_history_id
@opt_output_format
@client
def logs(api: DTSApi, transfer_id: str | None = None, history_id: str | None = None):
    """Команда получения логов (событий) переноса.

    Синтаксис: mls transfer logs [options]

    Пример: mls transfer logs --transfer-id 12c408ec-a4cd-4346-8f76-7364687d14f6
    """
    if not transfer_id and not history_id:
        raise click.UsageError(
            'Пропущена опция (необходимо передать --transfer_id или --history-id)',
        )

    click.echo(
        success_format(
            api.transfer_logs(transfer_id=transfer_id, history_id=history_id),
        ),
    )


@transfer.command(cls=TransferStopHelp, name='stop')
@click.option(
    '--transfer-id',
    help='ID правила переноса',
    required=True,
    cls=RequiredOptions,
)
@click.option(
    '--execution-date',
    help='Дата запуска переноса в формате 1970-01-13T14:55:35',
    required=True,
    cls=RequiredOptions,
)
@opt_output_format
@client
def cancel(api: DTSApi, transfer_id: str, execution_date: datetime):
    """Команда остановки выполняющегося переноса.

    Синтаксис: mls transfer stop [options]

    Пример: mls transfer stop --transfer-id 12c408ec-a4cd-4346-8f76-7364687d14f6 --execution-date 1970-01-13T14:55:35
    """
    click.echo(success_format(api.transfer_cancel(transfer_id, execution_date)))


@transfer.command(cls=TransferUpdateHelp, name='update')
@click.option(
    '--transfer-id',
    help='ID правила переноса',
    nargs=1,
    cls=TransferCreateRequired,
)
@click.option(
    '--period',
    help='Частота запуска правила переноса. По умолчанию перенос выполняется один раз',
    type=int,
    default=None,
    cls=TransferCreateOptional,
)
@click.option(
    '--name',
    help='Имя правила переноса',
    nargs=1,
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--connector-id',
    help='ID коннектора источника',
    nargs=1,
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--dst-connector-id',
    help='ID коннектора места назначения',
    nargs=1,
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--source',
    help="Источник данных (если несколько, укажите через запятую, например 'folder1/,folder5/')",
    type=str,
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--destination',
    help="Место назначения (укажите как минимум корень '/')",
    type=str,
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--description',
    help='Описание правила переноса',
    type=str,
    default=None,
    cls=TransferCreateOptional,
)
@click.option(
    '--cluster-name',
    help='Имя кластера',
    type=str,
    default=None,
    nargs=1,
    cls=TransferCreateOptional,
)
@click.option(
    '--strategy',
    help=f'Стратегия переноса {RussianChoice(STRATEGY).options}',
    type=RussianChoice(STRATEGY),
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--connector-type',
    help=f'Тип коннектора источника. {RussianChoice(ALL_CONNECTOR_TYPES).options}',
    type=RussianChoice(ALL_CONNECTOR_TYPES),
    nargs=1,
    cls=TransferCreateOptional,
    default=None,
)
@click.option(
    '--dst-connector-type',
    help=f'Тип коннектора места назначения. {RussianChoice(TARGET_CONNECTOR_TYPES).options}',
    type=RussianChoice(TARGET_CONNECTOR_TYPES),
    nargs=1,
    cls=TransferCreateOptional,
    default=None,
)
@opt_output_format
@client
def update(
    api: DTSApi,
    transfer_id: str,
    name,
    connector_id,
    dst_connector_id,
    connector_type,
    dst_connector_type,
    source,
    destination,
    cluster_name,
    period,
    strategy,
    description,
):
    """Команда обновления периодического правила переноса.

    Синтаксис: mls transfer update [options]

    Пример: mls transfer update --transfer-id 12c408ec-a4cd-4346-8f76-7364687d14f6
    """
    if not any(
        [
            name,
            connector_id,
            dst_connector_id,
            connector_type,
            dst_connector_type,
            source,
            destination,
            cluster_name,
            period,
            strategy,
            description,
        ],
    ):
        raise click.ClickException(message='Нужно передать хотя бы одну опцию')

    if source:
        source = [s.strip() for s in source.split(',')] if ',' in source else source

    t = {
        'name': name,
        'connector_id': connector_id,
        'destination_connector_id': dst_connector_id,
        'query': {'source': source, 'destination': destination},
        'connector_type': connector_type,
        'destination_connector_type': dst_connector_type,
        'cluster_name': cluster_name,
        'strategy': strategy,
        'favorite': False,
        'description': description,
    }

    if period and period > 0:
        t['crontab'] = asdict(CronViewModel(period=period))

    t = {k: v for k, v in t.items() if v is not None}

    click.echo(success_format(api.transfer_update(transfer_id, t)))


@transfer.command(cls=TransferHistoryHelp, name='history')
@opt_transfer_id_optional
@opt_source_name
@opt_output_format
@client
def history(api: DTSApi, transfer_id: str | None, source_name: str | None):
    """Команда получения истории запусков правил(а) переноса.

    Синтаксис: mls transfer history [options]

    Пример: mls transfer history --transfer-id 12c408ec-a4cd-4346-8f76-7364687d14f6 --source-name my-file.jpg
    """
    click.echo(success_format(api.transfer_history(transfer_id, source_name)))
