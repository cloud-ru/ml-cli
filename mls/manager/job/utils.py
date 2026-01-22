"""Вспомогательные утилиты для модуля управления задачами.

Этот модуль предоставляет различные вспомогательные функции и утилиты,
используемые в разных частях модуля управления задачами. Включает в себя
функции для обработки данных, валидации входных значений, форматирования
вывода и прочие общие инструменты, необходимые для выполнения задач.
"""
import os
from functools import update_wrapper
from typing import List

import click
import yaml  # type: ignore

from .custom_types import ExternalActionView
from .custom_types import job_actions_in_fail_input
from .custom_types import job_types_input
from .custom_types import JobDebugOptions
from .custom_types import JobElasticOptions
from .custom_types import JobEnvironmentOptions
from .custom_types import JobHealthOptions
from .custom_types import JobPolicyAllocationOptions
from .custom_types import JobPolicyOptions
from .custom_types import JobPytorch2Options
from .custom_types import JobRequiredOptions
from .custom_types import JobResourceOptions
from .custom_types import priority_class
from .custom_types import ProfileOptions
from .custom_types import worker_input
from .dataclasses import Job
from mls.utils.common import read_profile
from mls.utils.common_types import DictView
from mls.utils.common_types import IntOrStrView
from mls.utils.common_types import RangeView
from mls.utils.settings import DEFAULT_PROFILE
from mls_core import TrainingJobApi


def common_cli_options(func):
    """Декоратор для добавления общих опций."""
    # Высший приоритет ближе к пользователю консоль
    # func = click.option('-R', '--region', cls=ProfileOptions, index=0, type=ViewRegionKeys(), help='Ключ региона')(func)

    # Средний приоритет загрузка из файла
    func = click.option(
        '-P', '--profile', cls=ProfileOptions,  index=4, default=DEFAULT_PROFILE,
        help='Определение параметров региона, формата вывода по имени профиля',
    )(func)

    # Опции имеющие умолчания
    # func = click.option('-O', '--output', cls=ProfileOptions,  index=1, type=output_choice, help='Формат вывода в консоль.')(func)
    func = click.option('-E', '--endpoint_url', cls=ProfileOptions, index=2, help='Базовый адрес API')(func)
    func = click.option('-D', '--debug',  cls=JobDebugOptions, is_flag=True, help='Вывод в консоль отладочной информации')(func)
    return func


def job_client(func):
    """Декоратор создающий api client instance на базе ввода пользователя."""

    @common_cli_options
    def init_client(*args, **kwargs):
        """Инициализация PublicApi client."""
        profile = read_profile(kwargs.pop('profile'))

        have_defaults = dict(
            debug=kwargs.pop('debug'),
        )
        stable_rules = dict(
            client_id=profile.get('key_id', ''),
            client_secret=profile.get('key_secret', ''),
            x_workspace_id=profile.get('x_workspace_id'),
            x_api_key=profile.get('x_api_key'),
            endpoint_url=kwargs.pop('endpoint_url', '') or profile.get('endpoint_url'),
        )
        calculated_options = dict(region=kwargs.pop('region', '') or profile.get('region', ''))
        client = TrainingJobApi(**have_defaults, **stable_rules)
        client.USER_OUTPUT_PREFERENCE = kwargs.pop('output', None) or profile.get('output', 'json')  # FIXME

        return func(client, *args, **kwargs, **calculated_options)

    return update_wrapper(init_client, func)


def read_yaml(file_path: str):
    """Читает YAML файл и возвращает содержимое в виде словаря."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise click.ClickException(
            f"Ошибка чтения YAML файла '{file_path}': {e}",
        )


def define_run_job_options() -> List:
    """Функция получения списка опций.

    По сути сокрытие - огромного количества опций.
    """
    option = click.option
    # Запрещены опции default так как config мы перезаписываем из опций переданных пользователем, а default = передано пользователем.
    return [
        # Node options
        option(
            '-i', '--instance_type', cls=JobRequiredOptions, index=0,
            type=click.STRING, help='Конфигурация ресурсов (eꓸgꓸ, v100ꓸ1gpu)',
        ),
        option('-w', '--workers', cls=JobResourceOptions, index=0, type=worker_input, help='Количество рабочих узлов'),
        option(
            '-p', '--processes', cls=JobResourceOptions, index=1, type=IntOrStrView(), help=(
                'int  -- прямое указание числа процессов, default -- расчет оптимального количества процессов для запуска задачи'
            ),
        ),

        # Job options
        option(
            '-t', '--type',  cls=JobRequiredOptions, index=2, type=job_types_input, help=f'Тип задачи обучения. {job_types_input.options}',
        ),
        option(
            '-s', '--script', cls=JobRequiredOptions, index=3, type=click.STRING,
            help='Путь к исполняемому файлу. Например, к скрипту - :file:'
                 '`/home/jovyan/test_scriptꓸpy` или к исполняемому файлу -ls, -rm, -pwd',
        ),
        option('-d', '--description', type=click.STRING, help='Описание задачи'),

        # Environment options
        option('-I', '--image', cls=JobRequiredOptions, index=1, type=click.STRING, help='Название образа'),
        option('-e', '--conda_name', cls=JobEnvironmentOptions, index=0, type=click.STRING, help='Название Conda-окружения в образе'),
        option(
            '-f', '--flags', cls=JobEnvironmentOptions, index=1, type=DictView('-f'),
            help='Дополнительные флаги: key1=value1,key2=value2',
        ),
        option(
            '-v', '--variables', cls=JobEnvironmentOptions, index=2, type=DictView('-v'),
            help='Переменные окружения: key1=value1,key2=value2',
        ),

        # Policy options
        option(
            '-r', '--max_retry', cls=JobPolicyAllocationOptions, index=2,
            type=RangeView(2, 100), help='Максимальное количество попыток перезапуска. От 3 до 100',
        ),
        option(
            '-k', '--checkpoint_dir', cls=JobPolicyOptions, index=1, type=click.STRING,
            help='Путь для сохранения checkpoint. Например, :file:`/home/jovyan/`',
        ),
        option('-A', '--internet_access', cls=JobPolicyOptions, index=0, type=click.BOOL, help='Определяет наличие доступа в интернет'),
        option(
            '--priority_class', cls=JobPolicyOptions, index=2, type=priority_class,
            help=f'Приоритет выполнения задачи. {priority_class.options}',
        ),
        option(
            '-a',
            '--allocation_name',
            cls=JobPolicyOptions,
            index=3,
            type=click.STRING,
            help='Имя аллокации, в которой запланировано или выполнено задание',
        ),
        option(
            '-q', '--queue_name', cls=JobPolicyOptions, index=3, type=click.STRING,
            help='Имя очереди, в которой будет запланировано и выполнено задание',
        ),

        # Health options
        option('--period', cls=JobHealthOptions, index=0, type=click.INT, help='Минутный интервал для отслеживания появления логов'),
        option(
            '--internal_action', cls=JobHealthOptions, index=1,
            type=job_actions_in_fail_input, help=f'Действие направленное к задаче обучения. {job_actions_in_fail_input.options}',
        ),
        # Исключение из правил это единственная опция
        option(
            '--external_actions', multiple=True, cls=JobHealthOptions, index=2,
            type=ExternalActionView(), default=['notify'], help=(
                'Действие направленное к пользователю. Доступные варианты: [], [\'notify\']'
            ),
        ),

        # ElasticJob options
        option(
            '--elastic_min_workers', cls=JobElasticOptions, index=0, type=IntOrStrView(),
            help='Минимальное количество воркеров.  '
                 'int -- прямое указание числа процессов, default -- расчет оптимального количества процессов для запуска задачи',

        ),
        option(
            '--elastic_max_workers', cls=JobElasticOptions, index=1, type=IntOrStrView(),
            help='Максимальное количество воркеров.  '
                 'int -- прямое указание числа процессов, default -- расчет оптимального количества процессов для запуска задачи',
        ),
        option(
            '--elastic_max_restarts', cls=JobElasticOptions, index=2, type=worker_input,
            help='Максимальное количество перезапусков',
        ),

        # Pytorch2Job options
        option(
            '--use_env', cls=JobPytorch2Options, type=click.BOOL, is_flag=True,
            help=(
                'Использование переменные окружения для конфигурации вместо профиля по умолчанию или явно заданного файла настроек'
            ),
        ),
    ]


def apply_options(func):
    """Включение параметров задачи.

    Выделено в отдельную функцию из-за большого количества опций.
    """
    options = define_run_job_options()
    for option in reversed(options):
        func = option(func)

    def forward_type_job(*args, **kwargs):
        """Проброс в mls job submit только собранный объект для запуска задачи."""
        config = kwargs.get('config')
        if config:
            from_yaml = read_yaml(kwargs.get('config')).get('job', {})
        else:
            default = 'Mls.yaml'
            if os.path.isfile(default):
                from_yaml = read_yaml(default).get('job', {})
            else:
                from_yaml = {}
        return func(*args, **kwargs, type_job=Job.fabric(from_yaml, **kwargs))

    return update_wrapper(forward_type_job, func)
