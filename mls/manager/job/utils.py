"""Вспомогательные утилиты для модуля управления задачами.

Этот модуль предоставляет различные вспомогательные функции и утилиты,
используемые в разных частях модуля управления задачами. Включает в себя
функции для обработки данных, валидации входных значений, форматирования
вывода и прочие общие инструменты, необходимые для выполнения задач.
"""
from configparser import NoSectionError
from functools import update_wrapper
from typing import List

import click
import yaml  # type: ignore

from .custom_types import DictView
from .custom_types import ExecuteScriptView
from .custom_types import ExternalActionView
from .custom_types import int_or_default
from .custom_types import InternalActionView
from .custom_types import JobDebugOptions
from .custom_types import JobElasticOptions
from .custom_types import JobEnvironmentOptions
from .custom_types import JobHealthOptions
from .custom_types import JobPolicyAllocationOptions
from .custom_types import JobPolicyOptions
from .custom_types import JobPytorch2Options
from .custom_types import JobRequiredOptions
from .custom_types import JobResourceOptions
from .custom_types import JobSparkOptions
from .custom_types import json
from .custom_types import MaxRetryInView
from .custom_types import NFSPathView
from .custom_types import priority_class
from .custom_types import ProfileOptions
from .custom_types import ViewTypeTask
from .dataclasses import Job
from mls.utils.common import load_saved_config
from mls.utils.common_types import positive_int_with_zero
from mls.utils.execption import ConfigReadError
from mls.utils.settings import DEFAULT_PROFILE
from mls.utils.settings import SECRET_PASSWORD
from mls_core import TrainingJobApi


def common_cli_options(func):
    """Декоратор для добавления общих опций."""
    # Высший приоритет ближе к пользователю консоль
    # func = click.option('-R', '--region', cls=ProfileOptions, index=0, type=ViewRegionKeys(), help='Ключ региона')(func)

    # Средний приоритет загрузка из файла
    func = click.option(
        '-P', '--profile', cls=ProfileOptions,  index=4, default=DEFAULT_PROFILE,
        help='Определить параметры региона, формата вывода ... по имени профиля.',
    )(func)

    # Опции имеющие умолчания
    # func = click.option('-O', '--output', cls=ProfileOptions,  index=1, type=output_choice, help='Формат вывода в консоль')(func)
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
        client.USER_OUTPUT_PREFERENCE = kwargs.pop('output', None) or profile.get('output', json)

        return func(client, *args, **kwargs, **calculated_options)

    return update_wrapper(init_client, func)


def read_profile(profile_name):
    """Загружает (только существующий) профиль.

    Функция проверяет наличие секции профиля в файлах конфигурации и создаёт её,
    если она отсутствует.

    Аргументы:
        profile_name (str): Имя профиля, который загружается.

    Возвращает:
        dict : Собранный в словарь профиль
    """
    config, credentials = load_saved_config(SECRET_PASSWORD)
    try:
        return {**dict(config.items(profile_name)), **dict(credentials.items(profile_name))}
    except NoSectionError as err:
        raise ConfigReadError(f'Нет секции с названием {err.section}')


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
            type=click.STRING, help='Конфигурация ресурсов (e.g., v100.1gpu).',
        ),
        option('-w', '--workers', cls=JobResourceOptions, index=0, type=positive_int_with_zero, help='Количество рабочих узлов.'),
        option('-p', '--processes', cls=JobResourceOptions, index=1, type=int_or_default, help='Кол-во процессов.'),

        # Job options
        option('-t', '--type',  cls=JobRequiredOptions, index=2, type=ViewTypeTask(), help='Тип задачи обучения'),
        option('-s', '--script', cls=JobRequiredOptions, index=3, type=ExecuteScriptView(), help='Путь к исполняемому файлу.'),
        option('-d', '--description', type=click.STRING, help='Описание задачи.'),

        # Environment options
        option('-I', '--image', cls=JobRequiredOptions, index=1, type=click.STRING, help='Название образа. '),
        option('-e', '--conda_name', cls=JobEnvironmentOptions, index=0, type=click.STRING, help='Название Conda окружения в образе.'),
        option('-f', '--flags', cls=JobEnvironmentOptions, index=1, type=DictView('-f'), help='Дополнительные флаги.'),
        option('-v', '--variables', cls=JobEnvironmentOptions, index=2, type=DictView('-v'), help='Переменные окружения.'),

        # Policy options
        option(
            '-r', '--max_retry', cls=JobPolicyAllocationOptions, index=2,
            type=MaxRetryInView(), help='Макс. количество попыток перезапуска.',
        ),
        option('-k', '--checkpoint_dir', cls=JobPolicyOptions, index=1, type=NFSPathView(), help='Путь для сохранения checkpoint'),
        option('-a', '--internet_access', cls=JobPolicyOptions, index=0, type=click.BOOL, help='Разрешён ли доступ в интернет.'),
        option('--priority_class', cls=JobPolicyOptions, index=2, type=priority_class, help='Приоритет выполнения задачи.'),

        # Health options
        option('--period', cls=JobHealthOptions, index=0, type=click.INT, help='Минутный интервал для отслеживания появления логов.'),
        option(
            '--internal_action', cls=JobHealthOptions, index=1,
            type=InternalActionView(), help='Действие направленное к задачи обучения.',
        ),
        # Исключение из правил это единственная опция
        option(
            '--external_actions', multiple=True, cls=JobHealthOptions, index=2,
            type=ExternalActionView(), default=['notify'], help='Действие направленное к пользователю',
        ),

        # ElasticJob options
        option(
            '--elastic_min_workers', cls=JobElasticOptions, index=0, type=int_or_default,
            help='Минимальное количество воркеров.',
        ),
        option(
            '--elastic_max_workers', cls=JobElasticOptions, index=1, type=int_or_default,
            help='Максимальное количество воркеров.',
        ),
        option(
            '--elastic_max_restarts', cls=JobElasticOptions, index=2, type=positive_int_with_zero,
            help='Максимальное количество перезапусков.',
        ),

        # SparkJob options
        option('--spark_memory', cls=JobSparkOptions, type=click.FLOAT, help='Объем памяти для Spark.'),

        # Pytorch2Job options
        option(
            '--use_env', cls=JobPytorch2Options, type=click.BOOL,
            is_flag=True, help='Использовать torch.distributed.launch с --use_env',
        ),
    ]


def apply_options(func):
    """Включение параметров задачи.

    Выделено в отдельную функцию из-за большого количества опций
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
            from_yaml = {}
        return func(*args, **kwargs, type_job=Job.fabric(from_yaml, **kwargs))

    return update_wrapper(forward_type_job, func)
