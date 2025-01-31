"""Фикстуры тестов для pytest.

Этот модуль содержит общие фикстуры pytest, которые используются
в тестах по всему проекту. Фикстуры могут включать настройку тестовой среды,
мок-объекты, тестовые данные и т.д.
"""
import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Фикстура запуска приложения."""
    return CliRunner()
