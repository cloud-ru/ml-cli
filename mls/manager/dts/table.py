"""Модуль table содержит вспомогательные функции для обработки табличного представления данных."""
from datetime import datetime

from tabulate import tabulate  # type: ignore

from mls.manager.dts.custom_types import CONNECTOR_DEFAULT_FIELDS
from mls.manager.dts.custom_types import CONNECTOR_FIELD_NAMES
from mls.manager.dts.custom_types import CronViewModel
from mls.manager.dts.custom_types import DAYS
from mls.manager.dts.custom_types import TRANSFER_DEFAULT_FIELDS
from mls.manager.dts.custom_types import TRANSFER_FIELD_NAMES
from mls.schema.table import filter_by
from mls.schema.table import sort_by
from mls.schema.table import TableView


def process_cron(ct: CronViewModel) -> str:
    """Функция обработки расписания правила переноса."""
    result = 'Неизвестно'

    if not ct.start_at:
        return result

    if ct.period:
        result = f'Кажд. {int(ct.period)}ч'

    elif ct.time:
        time = datetime.fromisoformat(ct.start_at).strftime('%H:%M')
        if ct.weekdays:
            day = DAYS.get(ct.weekdays[0])
            result = f'Кажд. {day} в {time}'
        elif ct.monthdays:
            result = f'Кажд. месяц {ct.monthdays[0]} числа в {time}'
        else:
            result = f'Кажд. день в {time}'
    else:
        result = 'Один раз'

    return result


def process_transfer_table_content(entity, fields) -> list:
    """Функция подготовки данных для табличного представления правила переноса."""
    fields = [f.replace('-', '_') for f in fields]

    start_at = None
    schedule = 'Неизвестно'
    result: list = []
    if not isinstance(entity, dict):
        return result

    if (ct := entity.get('crontab')) is not None:
        cron = CronViewModel(**ct)
        start_at = cron.start_at
        schedule = process_cron(cron)

    for field in fields:
        f = None
        match field:
            case 'source':
                f = entity.get('query', {}).get('source')
            case 'destination':
                f = entity.get('query', {}).get('destination')
            case 'start_at':
                f = start_at
            case 'schedule':
                f = schedule
            case _:
                f = entity.get(field)

        result.append(f)

    return result


def process_connector_table_content(entity, fields) -> list:
    """Функция подготовки данных для табличного представления коннектора."""
    fields = [f.replace('-', '_') for f in fields]
    result: list = []
    if not isinstance(entity, dict):
        return result

    for field in fields:
        value = entity.get(field)
        result.append(value)

    return result


def display_transfers(data, fields):
    """Выборка из JSON-данных и отображение tabulate для трансферов."""
    if not fields:
        fields = TRANSFER_DEFAULT_FIELDS.keys()

    headers = [TRANSFER_FIELD_NAMES.get(f) for f in fields]

    table_data = []
    for entity in data:
        table_data.append(process_transfer_table_content(entity, fields))

    return tabulate(table_data, headers, tablefmt='pretty')


def display_connectors(data, fields):
    """Выборка из JSON-данных и отображение tabulate для коннекторов."""
    if not fields:
        fields = CONNECTOR_DEFAULT_FIELDS.keys()

    headers = [CONNECTOR_FIELD_NAMES.get(f) for f in fields]

    table_data = []
    for entity in data:
        table_data.append(process_connector_table_content(entity, fields))

    return tabulate(table_data, headers, tablefmt='pretty')


class DataTransferTableView(TableView):
    """Специализированное табличное представление для отображения данных."""

    def __init__(self, data, filters, sorters, schema, fields):
        """Инициализация таблицы."""
        super().__init__(data, filters, sorters, schema=schema)
        self.fields = fields

    def display(self):
        """Применяет фильтры и сортировки."""
        for apply in self.filters:
            self.data = filter_by(self.data, apply)
        self.data = sort_by(self.data, self.sorters)
        return self.schema(self.data, self.fields)
