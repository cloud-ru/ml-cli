"""Фикстуры тестов для pytest."""
import pytest

from mls.manager.dts.custom_types import Connector
from mls.manager.dts.custom_types import ConnectorInput
from mls.manager.dts.custom_types import S3Type
from mls.manager.dts.custom_types import Transfer
from mls_core import DTSApi

CONNECTOR_ID = WORKSPACE_ID = 'ac39eff1-9b36-4345-a395-4d1a18cc6a68'

CONNECTOR = {
    'connector_id': CONNECTOR_ID,
    'workspace_id': WORKSPACE_ID,
    'name': 'test_name',
    'source_type': 'nfsprivate',
    'system': True,
    'favorite': True,
    'status': 'success',
    'type_status': 'Test: success',
    'created': '2020-02-208T12:33:53.715491',
    'modified': '2020-02-208T12:33:53.715491',
    'uid': 'cd278a3a-8585-478a-95cb-6a74c2af245f',
    'parameters': {'namespace': 'ns0000001-00001'},
}

TRANSFER = {
    'transfer_id': '40e36b8d-cb6c-4726-8e8c-2b1d51285934',
    'uid': '26de1d4a-9474-4488-b1c8-88d9a1fae4d6',
    'cluster_name': 'christofari-1',
    'connector_id': '3c79fcd7-2b03-4472-93d8-50f4f121e8d6',
    'destination_connector_id': '89dd8df1-ee3b-40c0-b517-bece7339a566',
    'workspace_id': 'f80db757-39d7-4287-a509-56697679e9f9',
    'name': 'ИмяПереноса',
    'description': 'Тестовое правило переноса с запуском каждый понедельник в 12:55',
    'source_category': 's3custom',
    'destination_source_category': 's3custom',
    'strategy': 'write_all',
    'crontab': {
        'start_at': '2025-01-01T12:55:55',
        'time': '12:55',
        'weekdays': [1],
        'monthdays': None,
        'period': None,
    },
    'system': False,
    'favorite': False,
    'query': {
        'source': ['folder1/other-subfolder'],
        'destination': 'transfer-destination-folder',
    },
    'active': True,
    'created': '2025-01-01TT12:55:55.152317',
    'modified': '2025-01-01TT12:55:55.152317',
    'execution_date': None,
}

TRANSFERS = [
    TRANSFER,
    {
        'transfer_id': 'f6c75f1b-2559-4eed-a982-5acb6c4439ce',
        'uid': 'fd59b4c4-1a46-4635-9dfe-cafef9a955ec',
        'cluster_name': 'christofari-1',
        'connector_id': '8852458b-4749-4a9e-8034-1f5c859fc076',
        'destination_connector_id': 'dbea2149-a9d4-4066-97da-c4a0fb6a5eb0',
        'workspace_id': 'e9d46f99-8626-4648-9231-a1fcb2270bab',
        'name': 'ИмяПереноса',
        'description': 'Тестовое правило переноса с периодом 2ч',
        'source_category': 's3custom',
        'destination_source_category': 's3custom',
        'strategy': 'write_all',
        'crontab': {
            'start_at': '2025-01-01T12:55:56',
            'time': None,
            'weekdays': None,
            'monthdays': None,
            'period': 2,
        },
        'system': False,
        'favorite': False,
        'query': {
            'source': ['folder1/other-subfolder'],
            'destination': 'transfer-destination-folder',
        },
        'active': True,
        'created': '2025-01-01TT12:55:56.152317',
        'modified': '2025-01-01TT12:55:56.152317',
        'execution_date': None,
    },
]


@pytest.fixture
def read_profile():
    """Фикстура настроек пользователя."""
    return {
        'key_id': 'test_id_123',
        'key_secret': 'test_secret_456',
        'x_workspace_id': 'ac39eff1-9b36-4345-a395-4d1a18cc6a68',
        'x_api_key': '21f7283c-21c4-49fc-878a-79efbffccb58',
        'output': 'json',
        'region': 'test_region',
    }


def mock_validate_connector_exists(api, connector_id, connector_type):
    """Имитация существующего коннектора."""
    return True


def mock_validate_connector_not_exists(api, connector_id, connector_type):
    """Имитация несуществующего коннектора."""
    return False


def mock_collect_connector_params(connector_type):
    """Имитация коннектора."""
    return Connector(
        name='Test',
        parameters=S3Type(
            endpoint='test-ep',
            bucket='bucket-name',
            access_key_id='AK',
            security_key='SK',
        ),
    )


@pytest.fixture
def mock_api_dts(monkeypatch, read_profile):
    """Имитация работы api client."""

    class MockDTSApi(DTSApi):
        USER_OUTPUT_PREFERENCE = 'json'

        def _get_auth_token(self, client_id: str, client_secret: str):
            """Мокирование _get_auth_token поведения."""
            return 'ABC'

        def conn_sources(self=None):
            """Получение схем параметров для коннектора."""
            return [{'source_type': 's3mlspace', 'source_name': 'S3 ML Space'}]

        def conn_list(self, connector_ids=None, typ=None):
            """Получение одного или списка коннекторов."""
            return [CONNECTOR]

        def conn_create(self, connector: ConnectorInput, public: bool = False):
            """Создание коннектора."""
            return CONNECTOR

        def conn_update(self, conn_id, conn_type, params=None):
            """Обновление параметров коннектора."""
            return {
                'connector_id': '9e12966e-2713-49b2-9cd5-21e0e7b82c5a',
                'workspace_id': '22b7815c-f862-46b4-9a13-91128d85b805',
                'name': 'Name',
                'source_type': 's3custom',
                'system': False,
                'favorite': False,
                'status': 'failed',
                'type_status': 'Test: failed',
                'created': '2025-04-23T10:21:30.616182',
                'modified': '2025-05-16T11:58:40.813057',
                'uid': '3a2e90e6-3452-4d6e-b75a-4bd9b26abac4',
                'parameters': {'endpoint': 'asd', 'bucket': '123'},
            }

        def conn_activate(self, conn_id, conn_type=None):
            """Активация коннектора."""
            return {
                'connector_id': '58577044-64c7-41eb-9993-edafab55829c',
                'workspace_id': '22b7815c-f862-46b4-9a13-91128d85b805',
                'parameters': {
                    'endpoint': 'https://some.host.ru',
                    'bucket': 'test_bucket',
                },
                'logs': {
                    'status': 'success',
                    'logs': [
                        'Connect to https://some.host.ru',
                        'Get info about bucket test_bucket',
                        'OK!',
                    ],
                },
            }

        def conn_deactivate(self, conn_id, conn_type=None):
            """Деактивация коннектора."""
            return {
                'connector_id': '58577044-64c7-41eb-9993-edafab55829c',
                'workspace_id': '22b7815c-f862-46b4-9a13-91128d85b805',
                'parameters': {
                    'endpoint': 'https://some.host.ru',
                    'bucket': 'test_bucket',
                },
            }

        def conn_delete(self=None, conn_ids: list = None):  # type: ignore
            """Удаление коннектора."""
            return ['58577044-64c7-41eb-9993-edafab55829c']

        def transfer_create(self, transfer: Transfer = None):  # type: ignore
            """Создание правила переноса."""
            return TRANSFER

        def transfer_delete(self=None, transfer_ids: list = None):  # type: ignore
            """Удаления правил переноса."""
            return [
                '40e36b8d-cb6c-4726-8e8c-2b1d51285934',
                'f6c75f1b-2559-4eed-a982-5acb6c4439ce',
            ]

        def transfer_list(self=None):  # type: ignore
            """Получение списка всех правил переноса с обработкой вывода."""
            return TRANSFERS

        def transfer_get(self=None, transfer_id: str = None):  # type: ignore
            """Получение информации о провиле переноса."""
            if TRANSFER.get('transfer_id') == transfer_id:
                return TRANSFER

            return {}

        def transfer_switch(self=None, transfer_id: str = None, state: bool = False):  # type: ignore
            """Активация/Деактивация периодического правила переноса."""
            TRANSFER['active'] = state
            return TRANSFER

        def transfer_cancel(
            self, transfer_id: str = None, execution_date=None,  # type: ignore
        ):
            """Остановка выполнения переноса."""
            return {'status': 'cancelled'}

        def transfer_logs(self=None, transfer_id: str = None, history_id: str = None):  # type: ignore
            """Получение событий по переносу."""
            return {
                'count': 1,
                'items': [
                    {
                        'id': '40e36b8d-cb6c-4726-8e8c-2b1d51285933',
                        'transfer_id': '40e36b8d-cb6c-4726-8e8c-2b1d51285934',
                        'history_id': '769e3712-754d-474a-8cc8-f09f18bf092c',
                        'event_type': 305,
                        'event_category': 2,
                        'event_count': 2,
                        'last_object': '',
                        'last_log': 'there was nothing to transfer',
                    },
                ],
            }

        def transfer_history(
            self, transfer_id: str | None, source_name: str | None = None,  # type: ignore
        ):
            """Получение истории правила переноса."""
            return {
                'data': [
                    {
                        'date_from': '2025-05-21T12:55:55.355925',
                        'date_to': '2025-05-21T12:55:55.355925',
                        'history_id': '769e3712-754d-474a-8cc8-f09f18bf092c',
                        'uid': '2cd7310e-88a2-4e1d-b595-bd46b5f711d5',
                        'workspace_id': 'f80db757-39d7-4287-a509-56697679e9f9',
                        'transfer_id': '40e36b8d-cb6c-4726-8e8c-2b1d51285934',
                        'execution_date': '2025-05-21T12:55:55',
                        'transfer_name': 'ИмяПереноса',
                        'source_connector_name': 'test-conn',
                        'destination_connector_name': 'dst-conn',
                        'source': 'folder2/manifest.yaml',
                        'destination': 'transfer-destination-folder',
                        'source_name': 'manifest.yaml',
                        'source_type': 'folder',
                        'size': None,
                        'size_bytes': 0,
                        'rows_count': None,
                        'progress': 100,
                        'status': 'success',
                        'favorite': False,
                    },
                ],
                'total_count': 1,
            }

        def transfer_update(self=None, transfer_id: str = None, params: dict = None):  # type: ignore
            """Обновление периодического правила переноса."""
            TRANSFER['name'] = 'updated-name'
            TRANSFER['connector_id'] = 'updated-connector'
            TRANSFER['destination_connector_id'] = 'updated-dst-connector'
            return TRANSFER

    monkeypatch.setattr('mls.manager.dts.utils.read_profile', lambda x: read_profile)
    monkeypatch.setattr('mls.manager.dts.utils.DTSApi', lambda *a, **kw: MockDTSApi)
    monkeypatch.setattr(
        'mls.manager.dts.connector_cli.DTSApi', lambda *a, **kw: MockDTSApi,
    )
    monkeypatch.setattr(
        'mls.manager.dts.connector_cli.collect_connector_params',
        mock_collect_connector_params,
    )
    monkeypatch.setattr(
        'mls.manager.dts.connector_cli.validate_connector_exists',
        mock_validate_connector_exists,
    )
