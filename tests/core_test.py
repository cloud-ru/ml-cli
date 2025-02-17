"""Тесты mls-core."""
from unittest.mock import patch

import pytest
import responses
from requests import ReadTimeout

from mls_core import TrainingJobApi


@pytest.fixture
def api_client():
    """Фисктура клиента Public-api."""
    class MockTrainingJobApi(TrainingJobApi):
        """Мокирование _get_auth_token поведения."""
        ENDPOINT_URL = 'https://fake.api.com'

        def _get_auth_token(self, client_id: str, client_secret: str):
            return 'ABC'
    return MockTrainingJobApi(
        endpoint_url=MockTrainingJobApi.ENDPOINT_URL,
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


@responses.activate
def test_stream_data_with_success(monkeypatch, api_client):
    """Проверка работы получения логов в потоковом режиме."""
    name, region = 'name', 'region'
    test_path = f'jobs/{name}/logs'
    body = 'chunk1chunk2'

    responses.add(responses.GET, f'{api_client.ENDPOINT_URL}/{test_path}', body=body, stream=True)
    response = api_client.stream_logs(name, region)
    assert body == ''.join(response)


@responses.activate
def test_stream_data_with_timeout(monkeypatch, api_client):
    """Проверка работы получения логов с ошибкой таймаута."""
    name, region = 'name', 'region'

    monkeypatch.setattr(
        'mls_core.client.requests.Session.request',
        lambda *args, **kwargs: (_ for _ in ()).throw(ReadTimeout('Connection timed out')),
    )

    with pytest.raises(ReadTimeout) as err:
        list(api_client.stream_logs(name, region))

    assert ('Connection timed out',) == err.value.args


@responses.activate
def test_stream_without_data(monkeypatch, api_client):
    """Проверка работы получения логов с ошибкой от api."""
    name, region = 'name', 'region'
    test_path = f'jobs/{name}/logs'

    responses.add(responses.GET, f'{api_client.ENDPOINT_URL}/{test_path}', stream=True, status=404, body='Not found')
    response = api_client.stream_logs(name, region)
    assert '404, Not found' == ''.join(response)
