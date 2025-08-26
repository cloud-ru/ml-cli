"""Тестирование структуры задач."""
from typing import Callable

import pytest
import yaml  # type: ignore
from click import NoSuchOption

from mls.manager.job.dataclasses import create_unknown_job_class
from mls.manager.job.dataclasses import Environment
from mls.manager.job.dataclasses import Resource


@pytest.fixture
def unknown_job_args(monkeypatch):
    """Фикстура неизвестной задачи."""
    expected_type = 'unknown_type'
    unknown_job_class: Callable = create_unknown_job_class(expected_type)  # type: ignore
    return unknown_job_class, expected_type


def test_init_args(unknown_job_args):
    """Попытка не дать достаточно аргументов."""
    unknown_job_class, expected_type = unknown_job_args
    with pytest.raises(NoSuchOption) as err:
        unknown_job_class(None, None, None, None, '', '', expected_type)
    assert err.value.args[0] == 'No such option: --script, job.script'


def test_init_args_image(unknown_job_args):
    """Попытка не дать достаточно аргументов."""
    unknown_job_class, expected_type = unknown_job_args
    with pytest.raises(AttributeError) as err:
        unknown_job_class(None, None, None, None, 'python', '', expected_type)
    assert err.value.args[0] == "'NoneType' object has no attribute 'image'"


def test_init_args_env(unknown_job_args):
    """Попытка не дать достаточно аргументов."""
    unknown_job_class, expected_type = unknown_job_args
    env = Environment('image', 'conda_name', None, None)
    with pytest.raises(AttributeError) as err:
        unknown_job_class(env, None, None, None, 'python', '', expected_type)
    assert err.value.args[0] == "'NoneType' object has no attribute 'instance_type'"


@pytest.fixture
def unknown_yaml():
    """Результат публикации yaml не известной задачи."""
    return {
        'job': {
            'description': 'set any useful description',
            'environment': {
                'conda_name': 'conda_name',
                'flags': {
                    'flag1': True,
                    'flag2': True,
                },
                'image': 'cr.ai.cloud.ru/aicloud-base-images/py3.10-torch2.1.2:0.0.40',
                'variables': {
                    'ENV_1': True,
                    'ENV_2': True,
                },
            },
            'health': {
                'external_actions': ['notify'],
                'internal_action': 'restart',
                'period': 20,
            },
            'policy': {
                'checkpoint_dir': '/home/jovyan/checkpoint',
                'internet_access': True,
                'priority_class': 'medium',
            },
            'resource': {
                'instance_type': 'a100.1gpu',
                'processes': 1,
                'workers': 1,
            },
            'script': 'python -c "from time import sleep; sleep(1000);" ',
            'type': 'binary,horovod,pytorch,pytorch2,pytorch_elastic,binary_exp',
        },
    }


def test_init_unknown_job(unknown_job_args, unknown_yaml):
    """Тесты на не известный тип задачи."""
    unknown_job_class, expected_type = unknown_job_args
    env = Environment('image', 'conda_name', None, None)
    res = Resource('instance_type', None, None)
    instance = unknown_job_class(env, res, None, None, 'python', '', expected_type)
    assert instance.type == expected_type
    assert instance.to_yaml(instance.type) == yaml.dump(unknown_yaml, default_flow_style=False)
    assert instance.to_json('region') == {
        'script': 'python',
        'base_image': 'image',
        'instance_type': 'instance_type',
        'region': 'region',
        'type': 'unknown_type',
        'n_workers': 1,
        'conda_env': 'conda_name',
    }
