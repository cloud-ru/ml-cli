"""Описание интерфейса запуска распределённых задач обучения."""
import copy
import time
from typing import Callable

import click

from .constants import cluster_keys
from .constants import job_types
from .custom_types import filter_sort_choice
from .custom_types import FilterOptions
from .custom_types import JobRecommenderOptions
from .custom_types import SortOptions
from .dataclasses import Job
from .decorators import limit_selected
from .decorators import offset_selected
from .decorators import opt_output_format
from .decorators import queue_selected
from .decorators import regions_selected
from .decorators import status_of_task
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
from mls.utils.common_types import PositiveIntWithZeroView
from mls.utils.style import success_format


@click.group(cls=JobHelp)
def job():
    """Группа команд (входная точка) при работе с задачами обучения.

    Синтаксис: mls job [command] [args] [options]

    """


@job.command(cls=LogHelp)
@click.argument('name')
@click.option('-t', '--tail', type=PositiveIntWithZeroView(), help='Отображает последнюю часть файла логов', default=0)
@click.option('-v', '--verbose', is_flag=True, help='Подробный вывод журнала логов', default=False)
@click.option('-w', '--wait', is_flag=True, help='Флаг ожидания смены статуса с pending', default=False)
@job_client
def logs(api_job, name, tail, verbose, region, wait):
    """Команда получения журнала логов.

    Синтаксис: mls job logs [name] [options]

    Пример: mls job logs lm-mpi-job-00000000-0000-0000-0000-000000000000 -w

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
@opt_output_format
@job_client
def kill(api_job, name, region):
    """Команда остановки задачи обучения в регионе.

    Синтаксис: mls job kill [name] [options]

    Пример: mls job kill lm-mpi-job-00000000-0000-0000-0000-000000000000


    """
    click.echo(success_format(api_job.delete_job(name, region)))


@job.command(cls=RunHelp)
@click.option(
    '-c', '--config', cls=JobRecommenderOptions, type=Path(exists=True), help='Путь к YAML манифесту с описанием задачи', default=None,
)
@regions_selected
@opt_output_format
@apply_options
@job_client
def submit(api_job, region, type_job, *_, **__):
    """Команда для отправки задачи в очередь на выполнение.

    Синтаксис: mls job submit [options]

    Пример: mls job submit --config ./binary.yaml
    """
    click.echo(success_format(api_job.run_job(type_job.to_json(region))))


@job.command(cls=StatusHelp, name='status')
@click.argument('name')
@opt_output_format
@job_client
def status_(api_job, name, *_, **__):
    """Команда просмотра статуса задачи.

    Синтаксис: mls job status [name] [options]

    Пример: mls job status lm-mpi-job-00000000-0000-0000-0000-000000000000


    """
    click.echo(success_format(api_job.get_job_status(name)))


@job.command(cls=ListPodsHelp)
@click.argument('name')
@opt_output_format
@job_client
def pods(api_job, name, *_, **__):
    """Команда отображения списка подов задач пользователя.

    Синтаксис: mls job pods [name] [options]

    Пример: mls job pods lm-mpi-job-00000000-0000-0000-0000-000000000000

    """
    click.echo(success_format(api_job.get_pods(name)))


@job.command(cls=ListHelp, name='list')
@click.option('-a', '--allocation_name', help='Имя аллокации, в которой запланировано или выполнено задание', default=None)
@status_of_task
@regions_selected
@limit_selected
@offset_selected
@queue_selected
@opt_output_format
@job_client
def list_(api_job, region, queue, allocation_name, status, limit, offset):
    """Команда просмотра списка задач.

    Синтаксис: mls job list [options]

    Пример: mls job list --status Pending --status Running --queue 00000000-0000-0000-0000-000000000000 --limit 10

    """
    click.echo(success_format(api_job.get_list_jobs(region, queue, allocation_name, status, limit, offset)))


@job.command(cls=RestartHelp)
@click.argument('name')
@opt_output_format
@job_client
def restart(api_job, name, *_, **__):
    """Команда перезапуска задачи по имени.

    Синтаксис: mls job restart [name] [options]

    Пример: mls job restart lm-mpi-job-00000000-0000-0000-0000-000000000000

    """
    click.echo(success_format(api_job.restart_job(name)))


@job.command(cls=YamlHelp)
@click.argument('type', required=False, default='binary')
def yaml(type):  # pylint: disable=redefined-builtin
    """команда генерации yaml-файла по типу задачи.  Если аргумент type не передан, по умолчанию отображается задача типа binary.

    Синтаксис: mls job yaml [type]

    Пример: mls job yaml binary

    """
    click.echo(Job.to_yaml(type), nl=False)


@job.command(cls=TypeHelp)
def types():
    """Команда отображения типов задач.

    Синтаксис: mls job types

    Пример:  mls job types

    """
    click.echo(success_format('\n'.join(job_types)))


@job.command(cls=ClusterHelp)
def regions():
    """Отображает список регионов.

    Синтаксис: mls job regions

    Пример:  mls job regions

    """
    click.echo(success_format('\n'.join(cluster_keys)))


@job.command(cls=TableHelp)
@limit_selected
@offset_selected
@status_of_task
@click.option('-a', '--allocation_name', help='Имя аллокации, в которой запланировано или выполнено задание', default=None)
@regions_selected
@queue_selected
@click.option('-g', '--gpu_count', cls=FilterOptions, index=0, type=int, help='Количество GPU')
@click.option('-i', '--instance_type', cls=FilterOptions, index=1, help='Тип сервера')
@click.option('-d', '--description', cls=FilterOptions, index=2, help='Пользовательское описание задачи')
@click.option('-j', '--job_name', cls=FilterOptions, index=2, help='Название задачи')
@click.option(
    '--asc_sort', multiple=True, cls=SortOptions, type=filter_sort_choice,
    help=f'Сортировка загруженной информации в таблицу. {filter_sort_choice.options}',
)
@click.option(
    '--desc_sort', multiple=True, cls=SortOptions, type=filter_sort_choice,
    help=f'Сортировка загруженной информации в таблицу. {filter_sort_choice.options}',
)
@job_client
def table(
        api_job, region, queue, gpu_count, instance_type, description, allocation_name, job_name,
        status, limit, offset, asc_sort, desc_sort,
):
    """Команда просмотра таблицы с задачами.

    Синтаксис: mls job table [options]

    Пример:  mls job table --status Running --status Pending --queue 00000000-0000-0000-0000-000000000000 --limit 10

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
    data_source = api_job.get_list_jobs(region, queue, allocation_name, status, limit, offset).get('jobs', [])
    result = JobTableView(data_source, filters, sort).display()
    click.echo(success_format(result))
