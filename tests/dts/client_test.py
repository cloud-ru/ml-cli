"""Тестовые сценарии методов клиента."""
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from mls.manager.dts.custom_types import ConnectorInput
from mls.manager.dts.custom_types import S3Type
from mls_core import DTSApi


class TestClient:
    """Класс тестов на клиент DTSApi."""

    IDS = [str(uuid4()) for i in range(0, 3)]
    CONNECTORS = [
        {
            'connector_id': 'b095933c-9627-460e-be84-fd12ea8e8617',
            'workspace_id': None,
            'name': 'test1',
            'source_type': 's3custom',
        },
        {
            'connector_id': '35e53ea7-72b9-4e96-b415-4520958428a7',
            'workspace_id': '632bd5e3-e66e-4610-85d4-da2f0b1c1467',
            'name': 'test2',
            'source_type': 'postgresql',
        },
        {
            'connector_id': '80a533fb-8f79-4efe-95f2-64c26c209e68',
            'workspace_id': '632bd5e3-e66e-4610-85d4-da2f0b1c1467',
            'name': 'test2.2',
            'source_type': 'postgresql',
        },
    ]

    @pytest.fixture
    def mock_post(self):
        """Имитация отправки post-запроса."""
        with patch.object(DTSApi, 'post') as mock:
            yield mock

    @staticmethod
    def datetime_now():
        """Текущее значение времени в UTC."""
        return datetime.utcnow()

    @staticmethod
    def mock_api():
        """Имитация объекта DTSApi."""
        return DTSApi(
            endpoint_url='https://test-ep',
            client_id='id1',
            client_secret='secret2',
            x_workspace_id='x-ws-id3',
            x_api_key='x-api-key4',
        )

    def test_transfer_cancel(self, mock_post):
        """Проверка метода отмены переноса."""
        obj = self.mock_api()
        result = obj.transfer_cancel('test123', self.datetime_now())
        mock_post.assert_called()

        assert result == mock_post.return_value

    def test_transfer_cancel_exception_handling(self, mock_post):
        """Проверка отмены переноса при получении ошибки."""
        obj = self.mock_api()
        mock_post.side_effect = Exception('API error')

        with pytest.raises(Exception, match='API error'):
            obj.transfer_cancel('test123', self.datetime_now())

    @pytest.mark.parametrize('valid_type', ['nfs', 's3custom', 's3evolution'])
    def test_is_type_valid(self, valid_type):
        """Проверка метода валидности типа коннектора."""
        with patch('mls.manager.dts.custom_types.ALL_CONNECTOR_TYPES', valid_type):
            assert DTSApi.is_type_valid(valid_type) is True

    @pytest.mark.parametrize('valid_type', ['mssql', 'mysql', 'postgresql'])
    def test_is_custom_type_valid(self, valid_type):
        """Проверка метода валидности кастомного типа коннектора."""
        with patch('mls.manager.dts.custom_types.CUSTOM_CONNECTOR_TYPES', valid_type):
            assert DTSApi.is_custom_type_valid(valid_type) is True

    @pytest.mark.parametrize(
        'ids, bool_result', [(IDS, True), (['1', 'test-text', '$%^&'], False)],
    )
    def test_are_ids_valid(self, ids, bool_result):
        """Проверка валидности значений ID коннекторов на uuid тип."""
        assert DTSApi.are_ids_valid(ids) is bool_result

    @pytest.mark.parametrize(
        'typ, count', [('s3custom', 1), ('postgresql', 2), ('invalid', 0), ('', 3)],
    )
    def test_filter_by_type(self, typ, count, mock_post):
        """Проверка фильтрации по типу коннектора."""
        obj = self.mock_api()
        res = obj.filter_by_type(self.CONNECTORS, typ)
        assert len(res) == count

    def test_filter_by_connector_ids(self):
        """Проверка фильтрации по ID коннекторов."""
        connector_ids = [
            'b095933c-9627-460e-be84-fd12ea8e8617',
            '35e53ea7-72b9-4e96-b415-4520958428a7',
        ]
        filtered = DTSApi.filter_by_connector_ids(self.CONNECTORS, connector_ids)
        assert len(filtered) == 2

    def test_conn_create(self, mock_post, public=True):
        """Проверка метода создания коннектора."""
        conn = ConnectorInput(
            name='Test',
            source_type='s3custom',
            parameters=S3Type(
                endpoint='test-ep',
                bucket='test-bucket',
                access_key_id='test-ak',
                security_key='test-sk',
            ),
        )
        api = self.mock_api()
        created = api.conn_create(conn, public)
        mock_post.assert_called()
        assert created == mock_post.return_value
