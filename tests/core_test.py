"""Тесты mls-core."""
from unittest.mock import patch

import pytest

from mls_core import TrainingJobApi


@pytest.fixture
def api_client():
    """Фисктура клиента Public-api."""
    class MockTrainingJobApi(TrainingJobApi):
        """Мокирование _get_auth_token поведения."""

        def _get_auth_token(self, client_id: str, client_secret: str):
            return 'ABC'
    return MockTrainingJobApi(
        endpoint_url='https://fake.api.com',
        client_id='fake_id',
        client_secret='fake_secret',
        workspace_id='fake_workspace',
        x_api_key='fake_key',
        debug=True,
    )


@patch('mls_core.TrainingJobApi._request', return_value={'status': 'success'})
def test_training_api(mock_request, api_client):
    """Использование мокирования для _request метода вместо того, чтобы реализовать полную цепочку запроса."""
    assert api_client.get_job_status('fake_job', 'fake_region') == {'status': 'success'}
    assert api_client.get_job_logs('fake_job', 'fake_region') == {'status': 'success'}
    assert api_client.get_list_jobs('fake_region', 'allocation_name', 'status', 'limit', 'offset') == {'status': 'success'}
    assert api_client.get_pods('fake_job', 'fake_region') == {'status': 'success'}
    assert api_client.delete_job('fake_job', 'fake_region') == {'status': 'success'}
    assert api_client.restart_job('fake_job', 'fake_region') == {'status': 'success'}
    assert api_client.run_job({}) == {'status': 'success'}
