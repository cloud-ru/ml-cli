"""Тестовые сценарии для проверки получения журналов."""
import click
import pytest

from mls.manager.job.utils import job_client


@pytest.fixture
def user_profile():
    """Фикстура настроек пользователя."""
    return {
        'apikey_id': 'test_id',
        'apikey_secret': 'test_secret',
        'workspace_id': 'test_workspace',
        'x_api_key': 'test_x_api_key',
        'output': 'json',
        'region': 'test_region',
    }


@pytest.fixture()
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
            [],
            {
                'debug': False,
                'endpoint_url': 'https://api.ai.cloud.ru/public/v2',
                'client_id': 'test_id',
                'client_secret': 'test_secret',
                'workspace_id': 'test_workspace',
                'x_api_key': 'test_x_api_key',
            },
            'json',
            'test_region',

        ],
        [
            ['--region', 'abc'],
            {
                'debug': False,
                'endpoint_url': 'https://api.ai.cloud.ru/public/v2',
                'client_id': 'test_id',
                'client_secret': 'test_secret',
                'workspace_id': 'test_workspace',
                'x_api_key': 'test_x_api_key',
            },
            'json',
            'abc',
        ],
        [
            ['--output', 'text'],
            {
                'debug': False,
                'endpoint_url': 'https://api.ai.cloud.ru/public/v2',
                'client_id': 'test_id',
                'client_secret': 'test_secret',
                'workspace_id': 'test_workspace',
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
                'workspace_id': 'test_workspace',
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


def test_output():
    """Исправьте меня."""
    assert 1 == 1


def test_http_200():
    """Исправьте меня."""
    assert 1 == 1


def test_http_400_500():
    """Исправьте меня."""
    assert 1 == 1


def test_jobs_cli_():
    """Включает в себя поведенческие тесты."""
    pass
