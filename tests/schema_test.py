"""Тесты на проверку представления таблиц."""
import pytest

from mls.schema.table import display_jobs
from mls.schema.table import filter_by
from mls.schema.table import JobTableView
from mls.schema.table import sort_by
from mls.schema.table import TableView


def test_view():
    """Тест проверяющий инициализацию класса."""
    assert TableView([], [], [], lambda x: 'abc').display() == 'abc'


def test_view_filter():
    """Тест проверяющий фильтры."""
    assert TableView(
        [
            {'bar': 'hello', 'foo': 'world'},
            {'foo': 'hello', 'bar': 'world'},
        ],
        [
            {'field': 'bar', 'type': 'like', 'values': 'w'},
        ],
        [

        ], lambda x: x,
    ).display() == [{'foo': 'hello', 'bar': 'world'}]


def test_view_jobs_display_method():
    """Тест проверяющий метод отображения в задачах."""
    assert JobTableView([], [], []).schema.__name__ == 'display_jobs'


def test_display_jobs_headers():
    """Тест проверяющий заголовки в таблице."""
    assert display_jobs([]) == (
        '+------------+--------+---------+---------------+-----------------+----------------+--------------+\n'
        '| Имя задачи | Статус |  Регион | Instance Type | Описание задачи | Количество GPU | Длительность |\n'
        '+------------+--------+---------+---------------+-----------------+----------------+--------------+\n'
        '+------------+--------+---------+---------------+-----------------+----------------+--------------+'
    )


@pytest.fixture
def sample():
    """Фикстура ответа от public-api."""
    return [
        {
            'uid': '232d33b0-e3a4-49a7-85c1-000000000000',
            'job_name': 'lm-mpi-job-d305a5a8-12c6-4a65-801d-000000000000',
            'status': 'Pending',
            'region': 'DGX2-MT',
            'instance_type': 'v100.1gpu',
            'job_desc': 'set any useful description',
            'created_dt': '2025-02-24T10:59:38Z',
            'updated_dt': '2025-02-24T11:11:04.911528Z',
            'completed_dt': None,
            'cost': '0.0',
            'gpu_count': 1,
            'duration': '761461s',
            'namespace': 'ai0001905-05377',
        },

    ]


def test_display_jobs_body(sample):
    """Тест проверяющий стиль таблицы."""
    assert display_jobs(sample) == (
        '+-------------------------------------------------+'
        '---------+---------+---------------+----------------------------+----------------+------------------+\n'
        '|                   Имя задачи                    |'
        ' Статус  |  Регион | Instance Type |      Описание задачи       | Количество GPU |   Длительность   |\n'
        '+-------------------------------------------------+'
        '---------+---------+---------------+----------------------------+----------------+------------------+\n'
        '| lm-mpi-job-d305a5a8-12c6-4a65-801d-000000000000 |'
        ' Pending | DGX2-MT |   v100.1gpu   | set any useful description |       1        | 8 days, 19:31:01 |\n'
        '+-------------------------------------------------+'
        '---------+---------+---------------+----------------------------+----------------+------------------+'
    )


def test_filter_by_in(sample):
    """Тест проверяющий работу фильтров."""
    assert filter_by(sample, {'field': 'job_desc', 'type': 'in', 'values': ['v', 'w']}) == sample, 'Нету in метода'


def test_filter_by_eq(sample):
    """Тест проверяющий работу фильтров."""
    assert [*filter_by(sample, {'field': 'job_desc', 'type': 'eq', 'values': 'set'})] == []
    assert [*filter_by(sample, {'field': 'job_desc', 'type': 'eq', 'values': 'set any useful description'})] == sample


def test_sort_key(sample):
    """Тест проверяющий сортировку."""
    sample.append(
        {
            'uid': '232d33b0-e3a4-49a7-85c1-000000000000',
            'job_name': 'lm-mpi-job-d305a5a8-12c6-4a65-801d-000000000000',
            'status': 'Running',
            'region': 'DGX2-MT',
            'instance_type': 'v100.1gpu',
            'job_desc': 'set any useful description',
            'created_dt': '2025-02-24T10:59:38Z',
            'updated_dt': '2025-02-24T11:11:04.911528Z',
            'completed_dt': None,
            'cost': '0.0',
            'gpu_count': 2,
            'duration': '761461s',
            'namespace': 'ai0001905-05377',
        },
    )
    assert sort_by(sample, [{'field': 'status', 'direction': 'asc'}])[0] != sort_by(sample, [{'field': 'status', 'direction': 'desc'}])[0]
    assert sort_by(
        sample, [{'field': 'gpu_count', 'direction': 'asc'}],
    )[0] != sort_by(
        sample, [{'field': 'gpu_count', 'direction': 'desc'}],
    )[0]
