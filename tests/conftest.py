"""Фикстуры тестов для pytest.

Этот модуль содержит общие фикстуры pytest, которые используются
в тестах по всему проекту. Фикстуры могут включать настройку тестовой среды,
мок-объекты, тестовые данные и т.д.
"""
import re
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import responses
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Фикстура запуска приложения."""
    return CliRunner()


@pytest.fixture
def test_profile():
    """Подмена профиля на тестовый."""
    profile = {
        'key_id': 'test_id',
        'key_secret': 'test_secret',
        'x_workspace_id': '00000000-0000-4000-8000-000000000000',
        'x_api_key': 'test_x_api_key',
        'output': 'json',
        'region': 'test_region',
        'endpoint_url': 'https://test-url/public/v2',
    }
    with patch('mls.utils.client.read_profile') as mock_profile:
        mock_profile.return_value = profile
        yield profile


@pytest.fixture
def mock_auth():
    """Мок авторизации."""
    responses.post(
        re.compile(r'https?://[^:/\s]+(?::\d+)?/public/v2/service_auth'),
        json={'token': {'access_token': 'very_secret_token'}},
    )
    yield


@pytest.fixture
def mock_api_client():
    """Мок апи клиента."""
    mock_instance = MagicMock()

    with patch('mls.utils.client.create_client_instance', return_value=mock_instance):
        yield mock_instance
