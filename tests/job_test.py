"""Тестовые сценарии для проверки получения журналов."""
import click
import pytest

from mls.manager.job.custom_types import output_choice
from mls.manager.job.custom_types import ProfileOptions
from mls.manager.job.custom_types import ViewRegionKeys
from mls.manager.job.utils import job_client


@pytest.fixture
def user_profile():
    """Фикстура настроек пользователя."""
    return {
        'key_id': 'test_id',
        'key_secret': 'test_secret',
        'x_workspace_id': 'test_workspace',
        'x_api_key': 'test_x_api_key',
        'output': 'json',
        'region': 'test_region',
    }


@pytest.fixture
def fake_command(monkeypatch, runner, user_profile):
    """Фикстура имитирующая поведение при создании команды cli.

    Подмешивает, удаляет и модифицирует пользовательский ввод исходя из настройки.
    """
    class ABC:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
    monkeypatch.setattr('mls.manager.job.utils.TrainingJobApi', ABC)
    monkeypatch.setattr('mls.manager.job.utils.read_profile', lambda x: user_profile)
    result = []

    @click.command()
    @click.option('-R', '--region', cls=ProfileOptions, index=0, type=ViewRegionKeys(), help='Ключ региона')
    @click.option('-O', '--output', cls=ProfileOptions, index=1, type=output_choice, help='Формат вывода в консоль')
    @job_client
    def command(api_job, region, *args, **kwargs):
        result.append([api_job, region, args, kwargs])

    def run(options):
        runner.invoke(command, options)
        return result.pop()

    return run


@pytest.mark.parametrize(
    'options, validate, output, region', [
        [
            ['--endpoint_url', 'https://api.ai.cloud.ru'],
            {
                'debug': False,
                'endpoint_url': 'https://api.ai.cloud.ru',
                'client_id': 'test_id',
                'client_secret': 'test_secret',
                'x_workspace_id': 'test_workspace',
                'x_api_key': 'test_x_api_key',
            },
            'json',
            'test_region',

        ],
        [
            ['--region', 'abc', '--endpoint_url', 'https://api.ai.cloud.ru/public/v2'],
            {
                'debug': False,
                'endpoint_url': 'https://api.ai.cloud.ru/public/v2',
                'client_id': 'test_id',
                'client_secret': 'test_secret',
                'x_workspace_id': 'test_workspace',
                'x_api_key': 'test_x_api_key',
            },
            'json',
            'abc',
        ],
        [
            ['--output', 'text', '--endpoint_url', 'https://api.ai.cloud.ru/public/v3'],
            {
                'debug': False,
                'endpoint_url': 'https://api.ai.cloud.ru/public/v3',
                'client_id': 'test_id',
                'client_secret': 'test_secret',
                'x_workspace_id': 'test_workspace',
                'x_api_key': 'test_x_api_key',
            },
            'text',
            'test_region',
        ],
        [
            ['--endpoint_url', 'text', '--debug'],
            {
                'debug': True,
                'endpoint_url': 'text',
                'client_id': 'test_id',
                'client_secret': 'test_secret',
                'x_workspace_id': 'test_workspace',
                'x_api_key': 'test_x_api_key',
            },
            'json',
            'test_region',
        ],
    ],
)
def test_overwrite_arguments(options, validate, output, region, fake_command, user_profile):
    """Тест проверки логики переопределения одних переменных другими."""
    obj, region_, *_ = fake_command(options)
    assert region_ == region
    assert obj.USER_OUTPUT_PREFERENCE == output
    assert obj.kwargs == validate
