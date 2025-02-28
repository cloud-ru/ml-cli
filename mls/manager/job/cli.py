"""Описание интерфейса запуска распределённых задач обучения."""
import click

from .custom_types import cluster_keys
from .custom_types import job_choices
from .custom_types import job_types
from .custom_types import JobRecommenderOptions
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
from .help import TypeHelp
from .help import YamlHelp
from .utils import apply_options
from .utils import job_client
from mls.utils.common_types import Path
from mls.utils.common_types import positive_int_with_zero
from mls.utils.style import success_format


@click.group(cls=JobHelp)
def job():
    """Группа команд (входная точка) при работе с задачами обучения.

    Синтаксис: mls job [command] [args] [options]
    """


@job.command(cls=LogHelp)
@click.argument('name')
@click.option('-t', '--tail', type=positive_int_with_zero, help='Отображает последнюю часть файла логов', default=0)
@click.option('-v', '--verbose', is_flag=True, help='Подробный вывод журнала логов', default=False)
@job_client
def logs(api_job, name, tail, verbose, region):
    """Команда получения журнала логов.

    Синтаксис: mls job logs [NAME] [options]
    """
    click.echo(success_format(api_job.get_job_logs(name, region, tail, verbose)))


@job.command(cls=KillHelp)
@click.argument('name')
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
@apply_options
@job_client
def submit(api_job, region, type_job, *_, **__):
    """Функция для отправки задачи."""
    click.echo(success_format(api_job.run_job(type_job.to_json(region))))


@job.command(cls=StatusHelp, name='status')
@click.argument('name')
@job_client
def status_(api_job, name, region):
    """Команда просмотра статуса задачи.

    Синтаксис: mls job status [NAME] [options]
    """
    click.echo(success_format(api_job.get_job_status(name, region)))


@job.command(cls=ListPodsHelp)
@click.argument('name')
@job_client
def pods(api_job, name, region):
    """Команда просмотра статусов подов.

    Синтаксис: mls job pods [NAME] [options]
    """
    click.echo(success_format(api_job.get_pods(name, region)))


@job.command(cls=ListHelp, name='list')
@click.option('-a', '--allocation_name', help='Набор выделенных ресурсов GPU и CPU', default=None)
@click.option('-s', '--status', type=job_choices, multiple=True, help='Статусы задач', default=None)
@click.option('-l', '--limit', help='Лимит отображения количества задач', default=6000, type=positive_int_with_zero)
@click.option('-o', '--offset', help='Смещение относительно начала списка', default=0, type=positive_int_with_zero)
@job_client
def list_(api_job, region, allocation_name, status, limit, offset):
    """Команда просмотра списка задач.

    Синтаксис: mls job list [options]
    """
    click.echo(success_format(api_job.get_list_jobs(region, allocation_name, status, limit, offset)))


@job.command(cls=RestartHelp)
@click.argument('name')
@job_client
def restart(api_job, name, region):
    """Команда перезапуска задачи по имени.

    Синтаксис: mls job restart [NAME] [options]
    """
    click.echo(success_format(api_job.restart_job(name, region)))


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
