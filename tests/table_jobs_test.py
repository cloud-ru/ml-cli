"""Тестирование таблицы."""
import pytest

from mls.cli import cli
from mls.schema import JobTableView
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
    response = {
        'jobs': [{
            'job_name': 'test-job',
            'status': 'running',
            'gpu_count': 2,
            'instance_type': 'gpu-large',
            'job_desc': 'test description',
        }],
    }

    class MockTrainingJobApi(TrainingJobApi):
        """Мокирование _get_auth_token поведения."""

        def _get_auth_token(self, client_id: str, client_secret: str):
            return 'ABC'

        def get_list_jobs(self, *a, **kw):
            return response

        def get_job_logs(self, name: str, region: str, tail: int = 0, verbose: bool = False):
            return 'ABC'

    monkeypatch.setattr('mls.manager.job.utils.read_profile', lambda x: read_profile)
    monkeypatch.setattr('mls.manager.job.utils.TrainingJobApi', lambda *a, **kw: MockTrainingJobApi)
    return response


def test_table_command_basic(runner, mock_api_job, monkeypatch):
    """Тестирование базового вызова."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ['job', 'table', '-l100', '-g2', '-jtes'],
            obj={'api_job': mock_api_job},
        )
        assert result.exit_code == 0
        assert result.output == (
            '+------------+---------+---------+---------------+------------------+----------------+--------------+\n'
            '| Имя задачи | Статус  |  Регион | Instance Type | Описание задачи  | Количество GPU | Длительность |\n'
            '+------------+---------+---------+---------------+------------------+----------------+--------------+\n'
            '|  test-job  | running |         |   gpu-large   | test description |       2        |   0:00:00    |\n'
            '+------------+---------+---------+---------------+------------------+----------------+--------------+\n'
        )


def test_table_command_basic_filter(runner, mock_api_job, monkeypatch):
    """Тестирование базового вызова."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ['job', 'table', '-R', 'A100-MT', '-l100', '-o0', '-j0d', '-g2', '--status', 'Pending'],
            obj={'api_job': mock_api_job},
        )
        assert result.exit_code == 0
        assert result.output == (
            '+------------+--------+---------+---------------+-----------------+----------------+--------------+\n'
            '| Имя задачи | Статус |  Регион | Instance Type | Описание задачи | Количество GPU | Длительность |\n'
            '+------------+--------+---------+---------------+-----------------+----------------+--------------+\n'
            '+------------+--------+---------+---------------+-----------------+----------------+--------------+\n'
        )


def test_table_command_basic_no_status(runner, mock_api_job, monkeypatch):
    """Тестирование базового вызова."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ['job', 'table', '-R', 'A100-MT', '-l100', '-o0', '-j0d', '-g1', '--status', 'Foo'],
            obj={'api_job': mock_api_job},
        )

        assert result.exit_code == 2
        assert result.output == (
            'Usage: cli job table [OPTIONS]\n'
            "Try 'cli job table --help' for help.\n"
            '\n'
            "Error: Invalid value for '-s' / '--status': Недопустимый выбор 'Foo'. "
            "Допустимые варианты: 'Completed', 'Completing', 'Deleted', 'Failed', 'Pending', 'Running', 'Stopped', "
            "'Succeeded', 'Terminated'\n"
        )


def test_filters_and_sorting_no_created_at(runner, mock_api_job, monkeypatch):
    """Тестирование параметров фильтрации и сортировки."""
    test_filters = []
    test_sort = []

    def capture_args(self, data, filters, sort):
        nonlocal test_filters, test_sort
        test_filters = filters
        test_sort = sort
        return 'mocked table'

    monkeypatch.setattr(JobTableView, '__init__', capture_args)

    result = runner.invoke(
        cli,
        [
            'job', 'table',
            '-R', 'A100-MT',
            '-g', '2',
            '--asc_sort', 'gpu_count',
            '--desc_sort', 'created_at',
        ],
        obj={'api_job': mock_api_job},
    )
    assert not test_filters
    assert not test_sort
    assert result.exit_code == 2
    assert result.output == (
        'Usage: cli job table [OPTIONS]\n'
        "Try 'cli job table --help' for help.\n"
        '\n'
        "Error: Invalid value for '--desc_sort': Недопустимый выбор 'created_at'. "
        "Допустимые варианты: 'gpu_count', 'instance_type', 'job_desc', 'job_name'\n"
    )


def test_filters_and_sorting(runner, mock_api_job, monkeypatch):
    """Тестирование параметров фильтрации и сортировки."""
    test_filters = []
    test_sort = []

    def capture_args(self, data, filters, sort):
        nonlocal test_filters, test_sort
        test_filters = filters
        test_sort = sort
        return

    monkeypatch.setattr(JobTableView, '__init__', capture_args)
    monkeypatch.setattr(JobTableView, 'display', lambda self: 'mocked table')

    result = runner.invoke(
        cli,
        [
            'job', 'table',
            '-R', 'A100-MT',
            '-g', '2',
            '--asc_sort', 'gpu_count',
            '--desc_sort', 'instance_type',
        ],
        obj={'api_job': mock_api_job},
    )
    assert result.exit_code == 0

    # Проверка фильтров
    assert any(f['field'] == 'gpu_count' for f in test_filters)

    # Проверка сортировки
    assert {'field': 'gpu_count', 'direction': 'asc'} in test_sort
    assert {'field': 'instance_type', 'direction': 'desc'} in test_sort
