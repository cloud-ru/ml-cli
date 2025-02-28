"""Тесты на проверку запуска задач."""
import os

import pytest
import responses
import yaml  # type: ignore

from mls.cli import cli
from mls.manager.job import utils
from mls.utils.settings import ENDPOINT_URL
from mls_core import TrainingJobApi


@pytest.fixture
def load_profile(monkeypatch):
    """Загружаем профиль для тестов."""
    profile = dict(
        region='SR008',
        output='json',
        endpoint_url=ENDPOINT_URL,
        key_id='key_id',
        key_secret='key_secret',
        x_workspace_id='x_workspace_id',
        x_api_key='x_api_key',
    )
    monkeypatch.setattr(utils, 'read_profile', lambda x: profile)


@pytest.fixture
def samples(load_profile):
    """Считывает все YAML файлы из заданного каталога и возвращает словарь с именем файла и его содержанием."""
    def sample_read(template):
        directory_path = './samples'

        yaml_contents = {}

        for filename in os.listdir(directory_path):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                file_path = os.path.join(directory_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    yaml_contents[filename] = yaml.safe_load(file)
        return yaml_contents[template]
    return sample_read


@pytest.fixture
def mock_responses():
    """Имитация ответа api."""
    auth_url = ENDPOINT_URL + '/service_auth'
    token_response = {
        'token': {
            'access_token': 'fake-token',
        },
    }
    responses.add(
        responses.POST,
        auth_url,
        json=token_response,
        status=200,
    )
    responses.add(
        responses.POST,
        ENDPOINT_URL + '/jobs',
        json={
            'job_name': 'lm-mpi-job-3d69d31f-3553-4b2b-8046-9d8c6e9451a6',
            'status': 'Pending',
            'created_at': 1740466803,
        },
        status=200,
    )


@pytest.fixture
def client_api(monkeypatch):
    """Расширяем работу api."""
    test_object = []

    class TrainingMock(TrainingJobApi):
        def run_job(self, payload):
            test_object.append(payload)
            test_object.append(self)
            return super().run_job(payload)

    monkeypatch.setattr(utils, 'TrainingJobApi', TrainingMock)
    return test_object


def asserts(job_client, payload_, res):
    """Группа проверок соответствия yaml json."""
    assert res['job']['description'] == payload_['job_desc']
    assert res['job']['script'] == payload_['script']
    assert res['job']['type'] == payload_['type']
    assert res['job']['environment']['conda_name'] == payload_['conda_env']
    assert res['job']['environment']['flags'] == payload_['flags']
    assert res['job']['environment']['variables'] == payload_['env_variables']
    assert res['job']['environment']['image'] == payload_['base_image']
    assert res['job']['resource']['instance_type'] == 'a100.1gpu'
    assert payload_['instance_type'] == 'v100.1gpu'
    assert res['job']['resource']['processes'] == payload_['processes_per_worker']
    assert res['job']['resource']['workers'] == payload_['n_workers']
    assert res['job']['health']['external_actions'] == payload_['health_params']['sub_actions']
    assert res['job']['health']['internal_action'] == payload_['health_params']['action']
    assert res['job']['health']['period'] == payload_['health_params']['log_period']
    assert res['job']['policy']['checkpoint_dir'] == payload_['checkpoint_dir']
    assert res['job']['policy']['internet_access'] == payload_['internet']
    assert res['job']['policy']['priority_class'] == payload_['priority_class']
    assert 'max_retry' not in payload_
    assert payload_['region'] == 'DGX2-MT'
    assert job_client.USER_OUTPUT_PREFERENCE == 'text'


@pytest.mark.parametrize(
    'template', [
        'template.pytorch.yaml',
        'template.binary.yaml',
        'template.binary_exp.yaml',
        # 'template.nogpu.yaml',
        'template.pytorch2.yaml',
        'template.spark.yaml',
        'template.pytorch_elastic.yaml',
    ],
)
@responses.activate
def test_run_job_params(client_api, mock_responses, samples, template, runner, monkeypatch):
    """Список проверок того что samples валидных аргументы. И перезапись параметров yaml из консоли."""
    res = samples(template)
    result = runner.invoke(
        cli,
        ['job', 'submit', '--config', f'./samples/{template}', '--instance_type', 'v100.1gpu', '-R', 'DGX2-MT', '-r', '0', '-O', 'text'],
    )
    payload_, job_client = client_api

    assert result.output == (
        "{'job_name': 'lm-mpi-job-3d69d31f-3553-4b2b-8046-9d8c6e9451a6', 'status': 'Pending', 'created_at': 1740466803}\n"
    )

    asserts(job_client, payload_, res)


@responses.activate
def test_pytorch_period(client_api, mock_responses, load_profile, runner, monkeypatch):
    """Проверка выключения параметра health_params."""
    runner.invoke(
        cli, [
            'job', 'submit', '--config', './samples/template.pytorch.yaml', '--instance_type', 'v100.1gpu', '-R', 'DGX2-MT',
            '-r', '0', '--period', '0',
        ],
    )
    payload_, _ = client_api
    assert 'health_params' not in payload_


@pytest.mark.parametrize(
    'template', [
        # 'template.nogpu.yaml',
        'template.spark.yaml',
        'template.pytorch_elastic.yaml',
    ],
)
@responses.activate
def test_run_max_retry(client_api, mock_responses, samples, template, runner, monkeypatch):
    """Проверка игнорирования не своих параметров."""
    result = runner.invoke(
        cli,
        ['job', 'submit', '--config', f'./samples/{template}', '--instance_type', 'v100.1gpu', '-R', 'DGX2-MT', '-r', '4', '-O', 'text'],
    )

    assert result.output == (
        "{'job_name': 'lm-mpi-job-3d69d31f-3553-4b2b-8046-9d8c6e9451a6', 'status': 'Pending', 'created_at': 1740466803}\n"
    )
    payload_, job_client = client_api
    assert 'max_retry' not in payload_
    assert 'max_retry' not in samples(template)['job']['policy']


@responses.activate
def test_max_retry_binary_ignore(client_api, mock_responses, samples, runner, monkeypatch):
    """Проверка игнорирования не своих параметров."""
    template = 'template.pytorch_elastic.yaml'
    runner.invoke(
        cli, ['job', 'submit', '--config', f'./samples/{template}', '--instance_type', 'v100.1gpu', '-R', 'DGX2-MT', '-r', '10'],
    )
    payload_, _ = client_api
    assert 'max_retry' not in payload_


@responses.activate
def test_use_env_pytorch_ignore(client_api, mock_responses, samples, runner, monkeypatch):
    """Проверка игнорирования не своих параметров."""
    template = 'template.pytorch.yaml'
    runner.invoke(
        cli,
        [
            'job', 'submit', '--config', f'./samples/{template}', '--instance_type', 'v100.1gpu', '-R', 'DGX2-MT', '-r', '10',
            '--use_env',
        ],
    )
    payload_, _ = client_api
    assert 'pytorch_use_env' not in payload_


@responses.activate
def test_use_env_pytorch2(client_api, mock_responses, samples, runner, monkeypatch):
    """Проверка доставки специфичных переменных pytorch2."""
    template = 'template.pytorch2.yaml'
    runner.invoke(
        cli,
        [
            'job', 'submit', '--config', f'./samples/{template}', '--instance_type', 'v100.1gpu', '-R', 'DGX2-MT', '-r', '10',
            '--use_env', '-d', 'pytorch_elastic',
        ],
    )

    payload_, _ = client_api
    assert 'pytorch_use_env' in payload_


@responses.activate
def test_elastic_pytorch_ignore(client_api, mock_responses, samples, runner, monkeypatch):
    """Проверка игнорирования не своих параметров."""
    template = 'template.pytorch.yaml'
    runner.invoke(
        cli,
        [
            'job', 'submit', '--config', f'./samples/{template}', '--instance_type', 'v100.1gpu', '-R', 'DGX2-MT', '-r', '10',
            '--elastic_max_workers', '3', '--elastic_min_workers', '2', '-w', '2',
        ],
    )

    payload_, _ = client_api
    assert 'elastic_min_workers' not in payload_
    assert 'elastic_max_workers' not in payload_


@responses.activate
def test_elastic_pytorch(client_api, mock_responses, samples, runner, monkeypatch):
    """Проверка доставки специфичных переменных pytorch."""
    template = 'template.pytorch_elastic.yaml'
    runner.invoke(
        cli,
        [
            'job', 'submit', '--config', f'./samples/{template}', '--instance_type', 'v100.1gpu', '-R', 'DGX2-MT', '-r', '10',
            '--elastic_max_workers', '3', '--elastic_min_workers', '2', '-w', '3',
        ],
    )
    payload_, _ = client_api
    assert 'elastic_min_workers' in payload_
    assert 'elastic_max_workers' in payload_
