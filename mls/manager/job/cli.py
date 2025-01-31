"""Описание интерфейса запуска распределённых задач обучения."""
import click

from .custom_types import job_choices
from .help import JobHelp
from .help import KillHelp
from .help import ListHelp
from .help import ListPodsHelp
from .help import LogHelp
from .help import RestartHelp
from .help import RunHelp
from .help import StatusHelp
from .utils import job_client
from .utils import read_yaml
from mls.utils.common_types import Path
from mls.utils.common_types import positive_int_with_zero
from mls.utils.style import success_format


@click.group(cls=JobHelp)
def job():
    """Группа команд (входная точка) при работе с задачами обучения.

    Пример: mls job [command] [args] [options]
    """


@job.command(cls=LogHelp)
@click.argument('name')
@click.option('--tail', type=positive_int_with_zero, help='Отображает последнею часть файла', default=0)
@click.option('--verbose', is_flag=True, help='Подробный вывод журнала', default=False)
@job_client
def logs(api_job, name, tail, verbose, region):
    """Команда получения журнала (logs).

    Позволяет получить журнал

    Пример: mls job logs [NAME] [options]
    """
    click.echo(success_format(api_job.get_job_logs(name, region, tail, verbose)))


@job.command(cls=KillHelp)
@click.argument('name')
@job_client
def kill(api_job, name, region):
    """Команда остановки задачи обучения в кластера.

    Пример: mls job kill [NAME] [options]
    """
    click.echo(success_format(api_job.delete_job(name, region)))


@job.command(cls=RunHelp)
@click.option('--config', type=Path(exists=True), help='Путь к YAML файлу с описанием задачи', default=None)
@click.option('--instance-type', help='Тип ресурса', default=None)
@click.option('--image', help='Название образа', default=None)
@click.option('--job-description', help='Описание задачи', default=None)
@click.option('--script', help='Путь к сценарию запуска', default=None)
@click.option('--type', help='Тип задачи', default=None)
@click.option('--number_of_workers', type=positive_int_with_zero, help='Количество обработчиков задачи', default=1)
@job_client
def run(api_job, region, config, instance_type, image, job_description, script, type, number_of_workers):
    """Команда запуска задачи.

    Пример: Файла конфигурации

    1.yaml

    job:

        instance_type: a100plus.1gpu.80vG.12C.96G

        image: cr.ai.cloud.ru/9136e8ca-7a11-4d48-a850-7ff8d6888f3b/job-ada-xland:latest

        job_description: h100-1x-lapo

        script: /home/jovyan/quick-start/job_launch_pt/train_distributed_example-torch2.py

        type: pytorch2

        number_of_workers: 1


    Пример: mls job run --config 1.yaml

        Или

    Пример: mls job run --instance_type <...> --image <...> --job_description <...> --script <...> --type <...> --number_of_workers <...>

        Или

    Пример: mls job run --config 1.yaml  --job_description <...>
    """
    job_arguments = {}
    if config:
        job_arguments = read_yaml(config).get('job', job_arguments)
    payload = {
        'script': script or job_arguments.get('script'),
        'base_image': image or job_arguments.get('image'),
        'instance_type': instance_type or job_arguments.get('instance_type'),
        'region': region,
        'type': type or job_arguments.get('type'),
        'n_workers': number_of_workers or job_arguments.get('number_of_workers'),
        'job_desc': job_description or job_arguments.get('job_description'),
    }

    click.echo(success_format(api_job.run_job(payload)))


@job.command(cls=StatusHelp)
@click.argument('name')
@job_client
def status(api_job, name, region):
    """Команда просмотра статуса задачи.

    Пример: mls job status [NAME] [options]
    """
    click.echo(success_format(api_job.get_job_status(name, region)))


@job.command(cls=ListPodsHelp)
@click.argument('name')
@job_client
def pods(api_job, name, region):
    """Команда просмотра статуса подов.

    Пример: mls job pods [NAME] [options]
    """
    click.echo(success_format(api_job.get_pods(name, region)))


@job.command(cls=ListHelp, name='list')
@click.option('--allocation_name', help='Набор выделенных ресурсов GPU и CPU', default=None)
@click.option('--status', type=job_choices, multiple=True, help='Статусы задач', default=None)
@click.option('--limit', help='Лимит отображения количества задача', default=6000, type=positive_int_with_zero)
@click.option('--offset', help='Номер начала отображения списка', default=0, type=positive_int_with_zero)
@job_client
def list_(api_job, region, allocation_name, status, limit, offset):
    """Команда просмотра списка задачи.

    Пример: mls job list [options]
    """
    click.echo(success_format(api_job.get_list_jobs(region, allocation_name, status, limit, offset)))


@job.command(cls=RestartHelp)
@click.argument('name')
@job_client
def restart(api_job, name, region):
    """Команда перезапуска задачи по имени.

    Пример: mls job restart [NAME] [options]
    """
    click.echo(success_format(api_job.restart_job(name, region)))
