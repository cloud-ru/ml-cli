"""Модуль хранения представлений ML Space (MLS).

Данный модуль устанавливает схему для отображения в табличном виде.
"""
from datetime import timedelta

from tabulate import tabulate   # type: ignore


def sort_by(json_data, options):
    """Сортирует JSON-данные по нескольким полям с указанными направлениями.

    :param json_data: Список словарей для сортировки.
    :param options: Список критериев сортировки вида:
                   [{'field': 'имя_поля', 'direction': 'asc/desc'}]
    :return: Отсортированный список.
    """

    def _sort_key(item):
        """Генерирует ключ для сортировки на основе критериев."""
        sort_key = []
        for opt in options:
            field = opt['field']
            direction = opt['direction']
            value = item.get(field)
            if isinstance(value, (int, float)):
                sort_key.append(-value if direction == 'desc' else value)
            else:

                sort_key.append(-hash(value) if direction == 'desc' else hash(value))
        return tuple(sort_key)

    return sorted(json_data, key=_sort_key)


def filter_by(json_data, options):
    """Фильтрует JSON-данные по нескольким полям с указанными направлениями.

    :param json_data: Список словарей для фильтрации.
    :param options: Список критериев фильтрации вида:
                   [{'field': 'имя_поля', 'values': 'Any', 'type': 'FilterTypes'}]. # TODO Вынести в класс
    :return: Отфильтрованный список.
    """
    key = options['field']
    values = options['values']
    type_filter = options['type']
    if type_filter == 'eq':
        return filter(lambda x: x[key] == values, json_data)
    if type_filter == 'like':
        return filter(lambda x: values in x[key], json_data)
    return json_data


def display_jobs(json_data):
    """Выборка из json данных и отображение tabulate."""
    headers = [
        'Имя задачи', 'Статус', ' Регион', 'Instance Type', 'Описание задачи', 'Количество GPU', 'Длительность', 'ID очереди',
        'Название очереди', 'Название аллокации',
    ]
    # "Дата Создания", "Дата обновления", "Дата Завершения", "Цена", "Namespace"
    table_data = []
    for job in json_data:
        duration_seconds = int(job.get('duration', '0s').rstrip('s'))
        duration = timedelta(seconds=duration_seconds)
        table_data.append([
            job.get('job_name'),
            job.get('status'),
            job.get('region'),
            job.get('instance_type'),
            job.get('job_desc') or '-',
            job.get('gpu_count'),
            f'{duration}',
            job.get('queue_id'),
            job.get('queue_name'),
            job.get('allocation_name'),
            # job.get("created_dt"),
            # job.get("updated_dt"),
            # job.get("completed_dt") or '-',
            # job.get("cost"),
            # job.get("namespace"),
        ])

    return tabulate(table_data, headers, tablefmt='pretty')


class TableView:
    """Табличное представление для отображения json ответа."""

    def __init__(self, data, filters, sorters, schema):
        """Инициализация класса TableView."""
        self.filters = filters
        self.sorters = sorters
        self.schema = schema
        self.data = data

    def display(self):
        """Применяет фильтры и сортировки."""
        for apply in self.filters:
            self.data = filter_by(self.data, apply)
        self.data = sort_by(self.data, self.sorters)
        return self.schema(self.data)


class JobTableView(TableView):
    """Специализированное табличное представление для отображения списка задач (jobs).

    Args:
        data (List[Dict]):
            Список словарей с исходными данными о задачах
        filters (List[FilterConfig]): # TODO Вынести в класс
            Конфигурация фильтрации данных (объекты с полями 'field' и 'value').
        sorters (List[SorterConfig]): # TODO Вынести в класс
            Конфигурация сортировки (объекты с полями 'field' и 'direction').
        schema (DisplaySchema, optional):
            Схема отображения столбцов. По умолчанию используется display_jobs.
    """

    def __init__(self, data, filters, sorters, schema=None):
        """Инициализация класса JobTableView."""
        super().__init__(data, filters, sorters, schema=display_jobs)
