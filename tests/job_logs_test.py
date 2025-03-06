"""Тестирование таблицы."""
import pytest

from mls.cli import cli
from mls_core import TrainingJobApi


@pytest.fixture
def read_profile():
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
def mock_api_job(monkeypatch, read_profile):
    """Имитация работы api client."""
    def get_job_status_generator():
        yield {'status': 'pending'}
        yield {'status': 'running'}
        yield {'status': 'running'}
        yield {'status': 'running'}
        yield {'status': 'running'}
        yield {'status': 'running'}
        yield {'status': 'completed'}

    generator = get_job_status_generator()

    class MockTrainingJobApi(TrainingJobApi):
        """Мокирование _get_auth_token поведения."""

        def _get_auth_token(self, client_id: str, client_secret: str):
            return 'ABC'

        def get_job_status(self, name=None):
            return next(generator)

        def get_job_logs(self, name: str, region: str, tail: int = 0, verbose: bool = False):
            return 'ABC'

        def stream_logs(self, name, region, tail=0, verbose=False):
            yield 'ABC'
            yield 'PDF'

    monkeypatch.setattr('mls.manager.job.utils.read_profile', lambda x: read_profile)
    monkeypatch.setattr('mls.manager.job.utils.TrainingJobApi', lambda *a, **kw: MockTrainingJobApi)


def test_logs_command_basic(runner, mock_api_job):
    """Тестирование базового вызова."""
    result = runner.invoke(
        cli,
        ['job', 'logs', 'name_job'],
    )
    assert result.output == 'ABC\n'


def test_logs_command_basic_wait(runner, mock_api_job):
    """Тестирование базового вызова."""
    result = runner.invoke(
        cli,
        ['job', 'logs', 'name_job', '-w'],
        catch_exceptions=False,
    )

    assert result.output == 'pending\nABC\nPDF\n'
