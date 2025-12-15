"""Модуль представлений структур для запуска задач.

Данный модуль выполняет задачу сокрытия логики в определении структур данных. В частных представлениях определены yaml и json структуры.
"""
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from dataclasses import is_dataclass
from dataclasses import MISSING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

import click
import yaml  # type: ignore

from .constants import job_types
from .constants import priority

T = TypeVar('T', bound='MergeMixin')

binary, horovod, pytorch, pytorch2, pytorch_elastic, binary_exp = job_types
low, medium, high = priority


def note(text):
    """Функция для генерации yaml контракта."""
    return field(metadata={'note': text})  # pylint: disable=invalid-field-call


class MergeMixin:
    """Класс Миксин для определения внутреннего наполнения собственных, дата-классов в фабричных методах."""
    @classmethod
    def from_dict(cls: Type[T], **kwargs) -> T:
        """Функция очистки параметров из kwargs."""
        if not is_dataclass(cls):
            raise TypeError(f'{cls.__name__} is not a dataclass.')
        field_names = {f.name for f in fields(cls)}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in field_names}
        return cls(**filtered_kwargs)

    @classmethod
    def merge(cls: Type[T], options: Dict[str, Any], **kwargs: Dict[str, Any]):
        """Функция забора значений из конфига, замена пользовательским вводом либо замена на default."""
        if not is_dataclass(cls):
            raise TypeError(f'{cls.__name__} не является dataclass.')
        field_defaults = {f.name: f.default for f in fields(cls) if f.default is not MISSING}
        # В настоящий момент MISSING будет установлен для всех полей (т/е default убираю)
        if field_defaults:
            raise ValueError('Задано поведение по умолчанию')

        result_options = {}
        for f in fields(cls):
            key = f.name
            value = kwargs.get(key)
            if cls.is_empty(value):
                value = options.get(key, None)

            result_options[key] = value
        return cls.from_dict(**result_options)

    @staticmethod
    def is_empty(value: Any) -> bool:
        """Метод валидации для поля."""
        return value in (None, '', [], {}, ())


@dataclass
class HealthProbe(MergeMixin):
    """Структура проб."""
    period: Optional[int] = note(20)
    internal_action: Optional[str] = note('restart')
    external_actions: Optional[List[str]] = note(['notify'])


@dataclass
class Resource(MergeMixin):
    """Структура описания ресурса."""
    instance_type: str = note('a100.1gpu')
    workers: Optional[int] = note(1)
    processes: Optional[int] = note(1)


@dataclass
class Environment(MergeMixin):
    """Структура Окружения."""
    image: str = note('cr.ai.cloud.ru/aicloud-base-images/py3.10-torch2.1.2:0.0.40')
    conda_name: Optional[str] = note('conda_name')
    flags: Optional[Dict[str, str]] = note({'flag1': True, 'flag2': True})
    variables: Optional[Dict[str, str]] = note({'ENV_1': True, 'ENV_2': True})


@dataclass
class Policy(MergeMixin):
    """Структура Планировщика."""
    priority_class: Optional[str] = note('medium')
    checkpoint_dir: Optional[str] = note('/home/jovyan/checkpoint')
    internet_access: Optional[bool] = note(True)
    allocation_name: Optional[str] = note('my-favorite-allocation')
    queue_name: Optional[str] = note('my-favorite-queue')


@dataclass
class VolcanoPolicy(Policy):
    """Структура Volcano."""
    max_retry: int = note(5)


@dataclass
class Pytorch2Environment(Environment):
    """Класс дополнение к основному Environment для Pytorch2 задач обучения."""
    use_env: bool = note(False)


@dataclass
class ElasticResource(Resource):
    """Класс дополнение к основному Resource для Elastic."""
    elastic_min_workers: Optional[int] = note(2)
    elastic_max_workers: Optional[int] = note(3)
    workers: Optional[int] = note(3)

    def __post_init__(self):
        """Метод валидации аргументов до вызова."""
        if self.elastic_min_workers > self.workers:
            raise click.BadArgumentUsage(
                f'Не выполнено условие (workers >= elastic_min_workers) {self.workers} >= {self.elastic_min_workers}',
            )
        if self.elastic_max_workers != self.workers:
            raise click.BadArgumentUsage(
                f'Не выполнено условие (workers == elastic_max_workers) {self.workers} == {self.elastic_max_workers}',
            )


@dataclass
class ElasticPolicy(Policy):
    """Класс дополнение к Policy для Elastic."""
    elastic_max_restarts: Optional[int] = note(5)


@dataclass
class Job(MergeMixin):
    """Структура Job."""
    environment: Optional[Environment]
    resource: Optional[Resource]
    policy: Optional[Policy]
    health: Optional[HealthProbe]
    script: str = note('python -c "from time import sleep; sleep(1000);" ')
    description: Optional[str] = note('set any useful description')
    type: str = note(f"{','.join(job_types)}")

    def __post_init__(self):
        """Метод Принудительной валидации."""
        if not self.script:
            raise click.NoSuchOption('--script, job.script')
        if not self.environment.image:
            raise click.NoSuchOption('--image, job.environment.image')
        if not self.resource.instance_type:
            raise click.NoSuchOption('--instance_type, job.resource.instance_type')
        if not self.type:
            raise click.NoSuchOption('--type, job.type')

    def to_json(self, region) -> dict:
        """Метод сопоставления dataclass структуры в структуру api."""
        return {
            'script': self.script,
            'base_image': self.environment.image if self.environment and self.environment.image else '',
            'instance_type': self.resource.instance_type if self.resource and self.resource.instance_type else '',
            'region': region,
            'type': self.type,
            'n_workers': self.resource.workers if self.resource and self.resource.workers else 1,
            **({'job_desc': self.description} if self.description else {}),
            **({'processes_per_worker': self.resource.processes} if self.resource and self.resource.processes else {}),
            **({'internet': self.policy.internet_access} if self.policy and self.policy.internet_access else {}),
            **({'allocation_name': self.policy.allocation_name} if self.policy and self.policy.allocation_name else {}),
            **({'queue_name': self.policy.queue_name} if self.policy and self.policy.queue_name else {}),
            **({'conda_env': self.environment.conda_name} if self.environment and self.environment.conda_name else {}),
            **({'priority_class': self.policy.priority_class} if self.policy and self.policy.priority_class else {}),
            **({'checkpoint_dir': self.policy.checkpoint_dir} if self.policy and self.policy.checkpoint_dir else {}),
            **({
                'health_params': {
                    'log_period': self.health.period,
                    'action': self.health.internal_action,
                    'sub_actions': [*(self.health.external_actions if self.health.external_actions else [])],
                },
            } if self.health and self.health.period else {}),
            **({'flags': self.environment.flags} if self.environment and self.environment.flags else {}),
            **({'env_variables': self.environment.variables} if self.environment and self.environment.variables else {}),
        }

    @classmethod
    def _dataclass_to_dict(cls, datacls):
        result = {}
        for f in fields(datacls):
            field_name = f.name
            field_type = f.type
            meta = f.metadata if f.metadata else None
            if getattr(field_type, '__args__', None) and is_dataclass(field_type.__args__[0]):
                result[field_name] = cls._dataclass_to_dict(field_type.__args__[0])
            elif meta:
                result[field_name] = meta.get('note', '')
            elif getattr(field_type, '__args__', None):
                result[field_name] = str(field_type.__args__[0])
            else:
                result[field_name] = str(field_type)
        return result

    @classmethod
    def to_yaml(cls, type_):
        """Метод получения yaml задач."""
        job_structure = cls._dataclass_to_dict(cls.mapping(type_))
        return yaml.dump({'job': job_structure}, default_flow_style=False)

    @classmethod
    def mapping(cls, type_) -> Type[T]:
        """Метод сопоставления задачи ее типу."""
        return defaultdict(
            lambda: create_unknown_job_class(type_), {
                pytorch2: Pytorch2Job,
                binary: BinaryJob,
                horovod: HorovodJob,
                pytorch: PytorchJob,
                binary_exp: BinaryExpJob,
                pytorch_elastic: ElasticJob,
                # nogpu: NoGpuJob, # Сокрыт
            },
        )[type_]

    @classmethod
    def _structure(cls, type_):
        """Метод уточнения полей в при использовании фабрики."""
        return (
            getattr(cls.mapping(type_), '__dataclass_fields__')['environment'].type.__args__[0],
            getattr(cls.mapping(type_), '__dataclass_fields__')['resource'].type.__args__[0],
            getattr(cls.mapping(type_), '__dataclass_fields__')['policy'].type.__args__[0],
            getattr(cls.mapping(type_), '__dataclass_fields__')['health'].type.__args__[0],
        )

    @classmethod
    def fabric(cls, from_yaml, **kwargs):
        """Фабрика для создания задач."""
        type_ = kwargs.get('type') or from_yaml.get('type')
        environment, resource, policy, health = cls._structure(type_)
        env = environment.merge(from_yaml.get('environment', {}), **kwargs)
        res = resource.merge(from_yaml.get('resource', {}), **kwargs)
        pol = policy.merge(from_yaml.get('policy', {}), **kwargs)
        hea = health.merge(from_yaml.get('health', {}), **kwargs)
        description = kwargs.get('description') or from_yaml.get('description')
        script = kwargs.get('script') or from_yaml.get('script')
        return cls.mapping(type_)(env, res, pol, hea, script, description, type_)


@dataclass
class VolcanoJob(Job):
    """Класс разделения Volcano задач обучения."""
    policy: Optional[VolcanoPolicy]

    def to_json(self, region) -> dict:
        """Дополнение полезной нагрузкой для задач Volcano."""
        return {
            **super().to_json(region),
            **({'max_retry': self.policy.max_retry} if self.policy and self.policy.max_retry else {}),
        }


@dataclass
class Pytorch2Job(VolcanoJob):
    """Структура Pytorch2Job."""
    environment: Optional[Pytorch2Environment]
    type: str = note(pytorch2)
    script: str = note('/home/jovyan/quick-start/job_launch_pt/train_distributed_example-torch2.py')

    def to_json(self, region) -> dict:
        """Дополнение полезной нагрузкой для задач Pytorch2."""
        return {
            **super().to_json(region),
            **(
                {
                    'pytorch_use_env': self.environment.use_env,
                } if self.environment and self.environment.use_env else {}
            ),
        }


@dataclass
class ElasticJob(Job):
    """Структура ElasticJob."""
    resource: Optional[ElasticResource]
    policy: Optional[ElasticPolicy]
    type: str = note(pytorch_elastic)

    def to_json(self, region) -> dict:
        """Дополнение elastic спецификой данных для отправки."""
        return {
            **super().to_json(region),
            **({'elastic_max_restarts': self.policy.elastic_max_restarts} if self.policy and self.policy.elastic_max_restarts else {}),
            **({'elastic_min_workers': self.resource.elastic_min_workers} if self.resource and self.resource.elastic_min_workers else {}),
            **({'elastic_max_workers': self.resource.elastic_max_workers} if self.resource and self.resource.elastic_max_workers else {}),
        }


# @dataclass # Сокрыт
# class NoGpuJob(Job):
#     """Класс для работы с CPU задачами."""
#     type = note(nogpu)


@dataclass
class BinaryJob(VolcanoJob):
    """Структура BinaryJob."""
    type: str = note(binary)


@dataclass
class HorovodJob(VolcanoJob):
    """Структура HorovodJob."""
    type: str = note(horovod)


@dataclass
class PytorchJob(VolcanoJob):
    """Структура PytorchJob."""
    script: str = note('/home/jovyan/quick-start/pytorch-example/train_distributed_example.py')
    type: str = note(pytorch)


@dataclass
class BinaryExpJob(VolcanoJob):
    """Структура BinaryExpJob."""
    type: str = note(binary_exp)


def create_unknown_job_class(type_) -> Type[Job]:
    """Фабрика задач с не известным типом."""

    @dataclass
    class UnknownJob(Job):
        pass  # pylint: disable=unnecessary-pass

    UnknownJob.type = type_
    return UnknownJob
