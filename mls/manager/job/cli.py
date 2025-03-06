"""Описание интерфейса запуска распределённых задач обучения."""
import copy
import time
from typing import Callable

import click

from .custom_types import cluster_keys
from .custom_types import filter_sort_choice
from .custom_types import FilterOptions
from .custom_types import job_choices
from .custom_types import job_types
from .custom_types import JobRecommenderOptions
from .custom_types import output_choice
from .custom_types import ProfileOptions
from .custom_types import SortOptions
from .custom_types import ViewRegionKeys
from .dataclasses import Job
from .help import ClusterHelp
from .help import JobHelp
from .help import KillHelp
from .help import ListHelp
from .help import ListPodsHelp
from .help import LogHelp
from .help import RestartHelp
from .help import RunHelp
from .help import StatusHelp
from .help import TableHelp
from .help import TypeHelp
from .help import YamlHelp
from .utils import apply_options
from .utils import job_client
from mls.schema import JobTableView
from mls.utils.common_types import Path
from mls.utils.common_types import positive_int_with_zero
from mls.utils.style import success_format


# from mls.utils.schema import TableView, display_jobs


@click.group(cls=JobHelp)
def job():
    """Группа команд (входная точка) при работе с задачами обучения.

    Синтаксис: mls job [command] [args] [options]
    """


@job.command(cls=LogHelp)
@click.argument('name')
@click.option('-t', '--tail', type=positive_int_with_zero, help='Отображает последнюю часть файла логов', default=0)
@click.option('-v', '--verbose', is_flag=True, help='Подробный вывод журнала логов', default=False)
@click.option('-w', '--wait', is_flag=True, help='Флаг ожидания смены статуса с pending', default=False)
@job_client
def logs(api_job, name, tail, verbose, region, wait):
    """Команда получения журнала логов.

    Синтаксис: mls job logs [NAME] [options]
    """
    copy_client = copy.deepcopy(api_job)
    copy_client.USER_OUTPUT_PREFERENCE = None
    status__: Callable = lambda: copy_client.get_job_status(name).get('status')

    if wait:
        iteration = 0
        while True:
            current_status = status__()
            if current_status == 'pending':
                time.sleep(1 * (iteration + 0.2))
                iteration += 1
                click.echo(success_format(current_status))
            else:
                break

    if status__() == 'running':
        generator = api_job.stream_logs(name, region, tail, verbose)
        counter = 0
        last_position = 0
        while True:
            try:
                value = next(generator)
            except StopIteration:
                last_position = counter
                if status__() == 'running':
                    generator = api_job.stream_logs(name, region, tail, verbose)
                else:
                    break
            else:
                if last_position > 0:
                    last_position -= 1
                    continue
                counter += 1
                click.echo(success_format(value))

    else:
        click.echo(success_format(api_job.get_job_logs(name, region, tail, verbose)))


@job.command(cls=KillHelp)
@click.argument('name')
@click.option('-O', '--output', cls=ProfileOptions,  index=1, type=output_choice, help='Формат вывода в консоль')
@job_client
def kill(api_job, name, region):
    """Команда остановки задачи обучения в регионе.

    Синтаксис: mls job kill [NAME] [options]
    """
    click.echo(success_format(api_job.delete_job(name, region)))


@job.command(cls=RunHelp)
@click.option(
    '-c', '--config', cls=JobRecommenderOptions, type=Path(exists=True), help='Путь к YAML манифесту с описанием задачи', default=None,
)
@click.option('-R', '--region', cls=ProfileOptions, index=0, type=ViewRegionKeys(), help='Ключ региона')
@click.option('-O', '--output', cls=ProfileOptions,  index=1, type=output_choice, help='Формат вывода в консоль')
@apply_options
@job_client
def submit(api_job, region, type_job, *_, **__):
    """Функция для отправки задачи."""
    click.echo(success_format(api_job.run_job(type_job.to_json(region))))


@job.command(cls=StatusHelp, name='status')
@click.argument('name')
@click.option('-O', '--output', cls=ProfileOptions,  index=1, type=output_choice, help='Формат вывода в консоль')
@job_client
def status_(api_job, name):
    """Команда просмотра статуса задачи.

    Синтаксис: mls job status [NAME] [options]
    """
    click.echo(success_format(api_job.get_job_status(name)))


@job.command(cls=ListPodsHelp)
@click.argument('name')
@click.option('-O', '--output', cls=ProfileOptions,  index=1, type=output_choice, help='Формат вывода в консоль')
@job_client
def pods(api_job, name):
    """Команда просмотра статусов подов.

    Синтаксис: mls job pods [NAME] [options]
    """
    click.echo(success_format(api_job.get_pods(name)))


@job.command(cls=ListHelp, name='list')
@click.option('-a', '--allocation_name', help='Набор выделенных ресурсов GPU и CPU', default=None)
@click.option('-s', '--status', type=job_choices, multiple=True, help='Статусы задач', default=None)
@click.option('-l', '--limit', help='Лимит отображения количества задач', default=6000, type=positive_int_with_zero)
@click.option('-o', '--offset', help='Смещение относительно начала списка', default=0, type=positive_int_with_zero)
@click.option('-O', '--output', cls=ProfileOptions,  index=1, type=output_choice, help='Формат вывода в консоль')
@job_client
def list_(api_job, region, allocation_name, status, limit, offset):
    """Команда просмотра списка задач.

    Синтаксис: mls job list [options]
    """
    click.echo(success_format(api_job.get_list_jobs(region, allocation_name, status, limit, offset)))


@job.command(cls=RestartHelp)
@click.argument('name')
@click.option('-O', '--output', cls=ProfileOptions,  index=1, type=output_choice, help='Формат вывода в консоль')
@job_client
def restart(api_job, name):
    """Команда перезапуска задачи по имени.

    Синтаксис: mls job restart [NAME] [options]
    """
    click.echo(success_format(api_job.restart_job(name)))


@job.command(cls=YamlHelp)
@click.argument('type', required=False, default='binary')
def yaml(type):
    """Справочный метод.

    Например:
        mls job yaml binary > binary.yaml

    Без переданного TYPE - показывает задачу binary

    Совет:

        Запустите: mls job types

        Из полученного списка используйте TYPE : mls job yaml <TYPE>
    """
    click.echo(Job.to_yaml(type), nl=False)


@job.command(cls=TypeHelp)
def types():
    """Справочный метод - типы задач."""
    click.echo(success_format('\n'.join(job_types)))


@job.command(cls=ClusterHelp)
def regions():
    """Справочный метод - Список регинов."""
    click.echo(success_format('\n'.join(cluster_keys)))


@job.command(cls=TableHelp)
@click.option('-l', '--limit', help='Лимит отображения количества задач.', default=6000, type=positive_int_with_zero)
@click.option('-o', '--offset', help='Смещение относительно начала списка.', default=0, type=positive_int_with_zero)
@click.option('-s', '--status', type=job_choices, multiple=True, help='Статусы задач', default=None)
@click.option('-a', '--allocation', help='Набор выделенных ресурсов GPU и CPU.', default=None)
@click.option('-R', '--region', cls=ProfileOptions, index=0, type=ViewRegionKeys(), help='Ключ региона.')
@click.option('-g', '--gpu_count', cls=FilterOptions, index=0, type=int)
@click.option('-i', '--instance_type', cls=FilterOptions, index=1)
@click.option('-d', '--description', cls=FilterOptions, index=2)
@click.option('-j', '--job_name', cls=FilterOptions, index=2)
@click.option('--asc_sort', multiple=True, cls=SortOptions, type=filter_sort_choice, help='Сортировка загруженной информации в таблицу.')
@click.option('--desc_sort', multiple=True, cls=SortOptions, type=filter_sort_choice, help='Сортировка загруженной информации в таблицу.')
@job_client
def table(api_job, region, gpu_count, instance_type, description, allocation, job_name, status, limit, offset, asc_sort, desc_sort):
    """Команда просмотра таблицы с задачами.

    Синтаксис: mls job table [options]

    Основана на `mls job list`, но имеет опции фильтрации и сортировки по загруженному списку.

    """
    filters = [
        *([{'field': 'gpu_count', 'values': gpu_count, 'type': 'eq'}] if gpu_count else []),
        *([{'field': 'instance_type', 'values': instance_type, 'type': 'like'}] if instance_type else []),
        *([{'field': 'job_desc', 'values': description, 'type': 'like'}] if description else []),
        *([{'field': 'job_name', 'values': job_name, 'type': 'like'}] if job_name else []),
    ]
    sort = [
        *[{'field': asc,  'direction': 'asc'} for asc in asc_sort],
        *[{'field': desc,  'direction': 'desc'} for desc in desc_sort],
    ]

    api_job.USER_OUTPUT_PREFERENCE = None
    data_source = api_job.get_list_jobs(region, allocation, status, limit, offset).get('jobs', [])
    result = JobTableView(data_source, filters, sort).display()
    click.echo(success_format(result))
