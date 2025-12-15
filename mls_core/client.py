"""Модуль содержащий клиентов для работы с платформой MLSPACE."""
import http.client
import json
import logging
import sys
import time
from dataclasses import asdict
from datetime import datetime
from functools import wraps
from typing import Optional
from uuid import UUID

import click
import requests
from requests.adapters import HTTPAdapter  # type: ignore
from requests.sessions import ChunkedEncodingError  # type: ignore
from urllib3.util.retry import Retry

from .exceptions import AuthorizationError
from .exceptions import DataStreamingFailure
from .exceptions import InvalidAuthorizationToken
from .setting import BACKOFF_FACTOR
from .setting import CONNECT_TIMEOUT
from .setting import MAX_RETRIES
from .setting import READ_TIMEOUT
from .setting import SSL_VERIFY
from mls.manager.dts.custom_types import ALL_CONNECTOR_TYPES
from mls.manager.dts.custom_types import ConnectorInput
from mls.manager.dts.custom_types import CronViewModel
from mls.manager.dts.custom_types import CUSTOM_CONNECTOR_TYPES
from mls.manager.dts.custom_types import Transfer
from mls.manager.dts.custom_types import TransferUpdate


class CommonPublicApiInterface:
    """API клиент."""

    AUTH_ENDPOINT = 'service_auth'
    USER_OUTPUT_PREFERENCE = None

    def __init__(
        self,
        endpoint_url: str,
        client_id: str,
        client_secret: str,
        x_workspace_id: str,
        x_api_key: str,
        max_retries: int = MAX_RETRIES,
        backoff_factor: float = BACKOFF_FACTOR,
        connect_timeout: int = CONNECT_TIMEOUT,
        read_timeout: int = READ_TIMEOUT,
        ssl_verify=SSL_VERIFY,
        debug: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        """Инициализация класса PublicApi.

        :param endpoint_url: Базовый URL API.
        :param client_id: Идентификатор клиента.
        :param client_secret: Секрет клиента.
        :param x_workspace_id: Идентификатор воркспейса.
        :param x_api_key: ключ доступа к воркспейсу.
        :param max_retries: Максимальное количество попыток повторного запроса.
        :param backoff_factor: Фактор экспоненциальной задержки между повторными попытками.
        :param connect_timeout: Таймаут подключения (в секундах).
        :param read_timeout: Таймаут чтения (в секундах).
        :param ssl_verify: Параметр проверки сертификатов.
        :param debug: Включение отладочного режима.
        :param logger: Журнал приложения.

        """
        self._endpoint_url = endpoint_url
        self._connect_timeout = connect_timeout
        self._read_timeout = read_timeout
        self._debug = debug

        self._logger = (
            logger if logger is not None else self._create_logger(self._debug)
        )
        self._init_session(backoff_factor, max_retries)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.ssl_verify = ssl_verify
        self.workspace_id = x_workspace_id

        headers = {
            'authorization': self._get_auth_token(client_id, client_secret),
            'x-workspace-id': x_workspace_id,
            'x-api-key': x_api_key,
        }

        self._session.headers.update(headers)

    def _init_session(self, backoff_factor: float, max_retries: int):
        session = requests.Session()

        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=[
                'HEAD',
                'GET',
                'PUT',
                'DELETE',
                'OPTIONS',
                'POST',
            ],
        )

        session.mount('https://', HTTPAdapter(max_retries=retries))
        self._session = session

    def _create_logger(self, debug: bool):
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.WARNING)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s:%(name)s:%(message)s',
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        # Включает отладочный вывод для `requests`, `urllib3` и `http.client`.
        if debug:
            # Включаем отладку для http.client (работает только в Python 3)
            http.client.HTTPConnection.debuglevel = 1

            # Настройка логирования для библиотеки `requests` и `urllib3`
            logging.getLogger('urllib3').setLevel(logging.DEBUG)
            logging.getLogger('urllib3').propagate = True

            logger.setLevel(logging.DEBUG)

        return logger

    def _request(self, method: str, path: str, **kwargs):
        timeout = kwargs.pop(
            'timeout',
            (self._connect_timeout, self._read_timeout),
        )
        headers = kwargs.pop('headers', {})

        try:
            response = self._session.request(
                method,
                f'{self._endpoint_url}/{path}',
                headers=headers,
                timeout=timeout,
                **kwargs,
                verify=self.ssl_verify,
            )
            response.raise_for_status()
        except requests.exceptions.RetryError as ex:
            self._logger.debug(ex)
            return None
        if response.headers.get('content-type') == 'application/json':
            return response.json()
        return response.text

    def _get_auth_token(self, client_id: str, client_secret: str):
        try:
            response: dict = self.post(
                self.AUTH_ENDPOINT,
                json={
                    'client_id': client_id,
                    'client_secret': client_secret,
                },
            )
            if not (token := response['token']['access_token']):
                self._logger.debug(response)
                raise InvalidAuthorizationToken()

            return token
        except requests.exceptions.HTTPError as ex:
            self._logger.debug(ex)
            raise AuthorizationError(ex) from ex

    def get(self, *args, **kwargs):
        """GET запрос."""
        return self._request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        """POST запрос."""
        return self._request('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        """PUT запрос."""
        return self._request('PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        """DELETE запрос."""
        return self._request('DELETE', *args, **kwargs)

    def options(self, *args, **kwargs):
        """OPTIONS запрос."""
        return self._request('OPTIONS', *args, **kwargs)

    def head(self, *args, **kwargs):
        """HEAD запрос."""
        return self._request('HEAD', *args, **kwargs)

    @staticmethod
    def _handle_api_response(method):
        """Метод обработки ответа от API."""
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                response = method(self, *args, **kwargs)
            except requests.exceptions.HTTPError as ex:
                response = self._handle_http_error(ex)
            return self._user_preference_output(response)

        return wrapper

    def _user_preference_output(self, result):
        """Формат вывода пользователю сообщений."""
        if self.USER_OUTPUT_PREFERENCE:
            if self.USER_OUTPUT_PREFERENCE == 'json' and isinstance(result, (dict, list)):
                return json.dumps(result, indent=4, ensure_ascii=False)
            return result
        return result

    def _handle_http_error(self, ex):
        """Обработка исключений HTTPError."""
        self._logger.debug(ex)
        if ex.response.headers.get('content-type') == 'application/json':
            result = ex.response.json()
        else:
            result = ex.response.text
        return self._user_preference_output(result)


class TrainingJobApi(CommonPublicApiInterface):
    """Выделенный клиент api содержащий логику взаимодействия с задачами обучения."""

    USER_OUTPUT_PREFERENCE = None

    @staticmethod
    def _handle_api_response(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                response = method(self, *args, **kwargs)
            except requests.exceptions.HTTPError as ex:
                response = self._handle_http_error(ex)
            return self._user_preference_output(response)

        return wrapper

    def _user_preference_output(self, result):
        """Формат вывода пользователю сообщений."""
        if self.USER_OUTPUT_PREFERENCE:
            if self.USER_OUTPUT_PREFERENCE == 'json' and isinstance(result, dict):
                return json.dumps(result, indent=4, ensure_ascii=False)
            return result
        return result

    def _handle_http_error(self, ex):
        """Обработка исключений HTTPError."""
        self._logger.debug(ex)
        if ex.response.headers.get('content-type') == 'application/json':
            result = ex.response.json()
        else:
            result = ex.response.text
        return self._user_preference_output(result)

    @_handle_api_response
    def get_job_logs(
        self, name: str, region: str, tail: int = 0, verbose: bool = False,
    ):
        """Получение логов задачи."""
        params = {'region': region, 'tail': tail, 'verbose': verbose}
        return self.get(f'jobs/{name}/logs', params=params)

    @_handle_api_response
    def get_job_status(self, name):
        """Получение статуса задачи."""
        return self.get(f'jobs/{name}')

    @_handle_api_response
    def get_list_jobs(self, region, queue, allocation_name, status, limit, offset):
        """Получение логов задачи."""
        params = {
            'region': region,
            'allocation_name': allocation_name,
            'status': status,
            'limit': limit,
            'offset': offset,
            'queue_id': queue,
        }
        return self.get('jobs', params=params)

    @_handle_api_response
    def get_pods(self, name):
        """Вызов получения списка подов для задач pytorch (elastic)."""
        return self.get(f'jobs/elastic/{name}/pods')

    @_handle_api_response
    def delete_job(self, name, region):
        """Вызов завершения работы задачи."""
        params = {'region': region}
        return self.delete(f'jobs/{name}', params=params)

    @_handle_api_response
    def restart_job(self, name):
        """Вызов перезапуска задачи."""
        payload = {'job_name': name}
        return self.post('jobs/restart', json=payload)

    @_handle_api_response
    def run_job(self, payload):
        """Вызов запуска задачи."""
        return self.post('jobs', json=payload)

    def stream(self, method: str, path: str, **kwargs):
        """Выполняет HTTP запрос с использованием заданного метода к указанному пути возвращает данные порционно(потоково).

        :param method: HTTP метод запроса.
        :param path: Путь запроса, который будет добавлен к базовому URL.
        :param kwargs: Дополнительные параметры запроса.
        :return: Генератор, который возвращает данные ответа по частям. В случае ошибки запроса возвращает статус ответа с описанием ошибки.
        """
        timeout = kwargs.pop('timeout', (self._connect_timeout, self._read_timeout))
        headers = kwargs.pop('headers', {})
        try:
            response = self._session.request(
                method,
                f'{self._endpoint_url}/{path}',
                headers=headers,
                timeout=timeout,
                stream=True,
                **kwargs,
                verify=self.ssl_verify,
            )
        except requests.exceptions.RetryError as ex:
            self._logger.debug(ex)
        else:
            if response.status_code == 200:
                yield from self._stream_data_with_retry(response)
            else:
                yield f'{response.status_code}, {response.text}'

    def _stream_data_with_retry(self, response):
        """Потоково читает данные ответа, пытаясь снова при возникновении ошибки `ChunkedEncodingError`.

        :param response: Объект ответа `requests. Response`, из которого будут читаться данные.
        :return: Генератор, возвращающий данные ответа по частям.

        В случае повторяющихся ошибок `ChunkedEncodingError` до достижения максимального количества попыток
        инициирует исключение `DataStreamingFailure`.
        """
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                yield from response.iter_content(chunk_size=256, decode_unicode=True)
                return
            except ChunkedEncodingError as er:
                sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                self._logger.debug(
                    f'Обработка ошибки потоковой передачи данных: {er}. Ожидаем {sleep_time} секунд перед следующей попыткой.',
                )
                time.sleep(sleep_time)
                last_error = er
            finally:
                response.close()

        raise DataStreamingFailure(
            f'Не удалось выполнить потоковое чтение данных после {self.max_retries} '
            f'повторных попыток из-за ошибки кодирования Chunk. Последняя ошибка: {last_error}',
        )

    def stream_logs(self, name, region, tail=0, verbose=False):
        """Выполняет потоковую загрузку логов для указанной задачи с использованием заданных параметров.

        :param name: Имя задачи, для которой запрашиваются логи.
        :param region: Регион, в котором выполнена задача.
        :param tail: Количество последних строк лога для отображения.
        :param verbose: Флаг, указывающий на необходимость вывода подробных логов.
        :return: Вызывает функцию `stream`, чтобы выполнить потоковую загрузку логов задачи.
        """
        params = {'region': region, 'tail': tail, 'verbose': verbose}
        yield from self.stream('GET', f'jobs/{name}/logs', params=params)


class ConnectorRoutes:
    """Адреса API коннекторов."""
    LIST: str = 'data_transfer/v3/connectors'
    CREATE: str = 'data_transfer/v3/connectors'
    UPDATE: str = 'data_transfer/v3/connectors/{conn_type}/{conn_id}'
    TRY: str = 'data_transfer/v3/connectors/{conn_type}/{conn_id}/try'
    TRY_LOGS: str = 'data_transfer/v3/connectors/{conn_type}/{conn_id}/try/logs'
    HALT: str = 'data_transfer/v3/connectors/{conn_type}/{conn_id}/halt'
    DELETE: str = 'data_transfer/v2/connectors'
    GET: str = 'data_transfer/v3/connectors/{conn_type}/{conn_id}'
    SOURCES: str = 'data_transfer/v2/connectors/sources'


class TransferRoutes:
    """Адреса API правил переноса."""
    CREATE: str = 'data_transfer/v5/transfer'
    DELETE: str = 'data_transfer/v2/transfer'

    HISTORY: str = 'data_transfer/v3/history'
    LIST: str = 'data_transfer/v4/transfer'
    GET: str = 'data_transfer/v4/transfer/{transfer_id}'
    SWITCH: str = 'data_transfer/v4/transfer/{transfer_id}/switch'
    LOGS: str = 'data_transfer/v2/events/list'
    CANCEL: str = 'data_transfer/v2/history/cancel'
    UPDATE: str = 'data_transfer/v5/transfer/{transfer_id}'


class DTSApi(CommonPublicApiInterface):
    """Выделенный API-клиент, содержащий логику взаимодействия с коннекторами, правилами переноса и их историей."""

    USER_OUTPUT_PREFERENCE = None

    @staticmethod
    def _handle_api_response(method):
        """Метод обработки ответа от API."""
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                response = method(self, *args, **kwargs)
            except requests.exceptions.HTTPError as ex:
                response = self._handle_http_error(ex)
            return self._user_preference_output(response)

        return wrapper

    def _user_preference_output(self, result):
        """Формат вывода пользователю сообщений."""
        if self.USER_OUTPUT_PREFERENCE:
            if self.USER_OUTPUT_PREFERENCE == 'json' and isinstance(
                result, (dict, list),
            ):
                return json.dumps(result, indent=4, ensure_ascii=False)
            return result
        return result

    def _handle_http_error(self, ex):
        """Обработка исключений HTTPError."""
        self._logger.debug(ex)
        if ex.response.headers.get('content-type') == 'application/json':
            result = ex.response.json()
        else:
            result = ex.response.text
        return self._user_preference_output(result)

    @staticmethod
    def is_type_valid(typ):
        """Проверка валидности типа коннектора."""
        return typ in ALL_CONNECTOR_TYPES

    @staticmethod
    def is_custom_type_valid(typ):
        """Проверка валидности кастомного типа коннектора."""
        return typ in CUSTOM_CONNECTOR_TYPES

    @staticmethod
    def are_ids_valid(values) -> bool:
        """Проверка валидности uuid значений."""
        try:
            _ = [UUID(value) for value in values]
            return True

        except ValueError:
            return False

    def filter_by_type(self, connectors: list, typ: str) -> list:
        """Фильтрация коннекторов по типу."""
        if not typ:
            return connectors

        if not self.is_type_valid(typ):
            return []

        return list(filter(lambda d: d['source_type'] == typ, connectors))

    @staticmethod
    def filter_by_connector_ids(connectors, connector_ids) -> list:
        """Фильтрация коннекторов по ids."""
        return list(filter(lambda d: d['connector_id'] in connector_ids, connectors))

    @_handle_api_response
    def conn_sources(self):
        """Получение схем параметров для коннектора."""
        return self.get(ConnectorRoutes.SOURCES)

    @_handle_api_response
    def conn_list(self, connector_ids=None, typ=None):
        """Получение одного или списка коннекторов."""
        connectors = self.get(ConnectorRoutes.LIST)
        by_type = self.filter_by_type(connectors, typ)

        if not connector_ids:
            return by_type

        if not self.are_ids_valid(connector_ids):
            return []

        return self.filter_by_connector_ids(by_type, connector_ids)

    @_handle_api_response
    def conn_create(self, connector: ConnectorInput, public: bool = False):
        """Создание коннектора."""
        body = asdict(connector)
        if public:
            body['workspace_id'] = self._session.headers.get('x-workspace-id')

        return self.post(ConnectorRoutes.CREATE, json=body)

    @_handle_api_response
    def conn_update(self, conn_id, conn_type, params):
        """Обновление параметров коннектора."""
        return self.post(
            ConnectorRoutes.UPDATE.format(conn_type=conn_type, conn_id=conn_id),
            json=asdict(params),
        )

    @_handle_api_response
    def conn_activate(self, conn_id, conn_type):
        """Активация коннектора."""
        res = self.post(
            ConnectorRoutes.TRY.format(conn_id=conn_id, conn_type=conn_type),
        )
        logs = self.get(
            ConnectorRoutes.TRY_LOGS.format(conn_id=conn_id, conn_type=conn_type),
        )
        res['logs'] = logs

        return res

    @_handle_api_response
    def conn_deactivate(self, conn_id, conn_type):
        """Деактивация коннектора."""
        return self.post(
            ConnectorRoutes.HALT.format(conn_id=conn_id, conn_type=conn_type),
        )

    @_handle_api_response
    def conn_delete(self, conn_ids):
        """Удаление коннектора."""
        return self.delete(ConnectorRoutes.DELETE, params={'ids': conn_ids})

    @_handle_api_response
    def conn_params(self, conn_id, conn_type):
        """Получение параметров коннектора."""
        return self.get(
            ConnectorRoutes.GET.format(conn_id=conn_id, conn_type=conn_type),
        )

    @_handle_api_response
    def transfer_create(self, transfer: Transfer):
        """Создание правила переноса."""
        return self.post(TransferRoutes.CREATE, json=asdict(transfer))

    @_handle_api_response
    def transfer_delete(self, transfer_ids: list):
        """Удаления правил переноса."""
        return self.delete(TransferRoutes.DELETE, params={'ids': transfer_ids})

    def get_transfers(self):
        """Вспомогательный метод для получения списка правил переноса."""
        return self.get(TransferRoutes.LIST)

    @_handle_api_response
    def transfer_list(self):
        """Получение списка всех правил переноса с обработкой вывода."""
        return self.get_transfers()

    def transfer(self, transfer_id: str):
        """Вспомогательный метод для получения провила переноса."""
        return self.get(TransferRoutes.GET.format(transfer_id=transfer_id))

    @_handle_api_response
    def transfer_get(self, transfer_id: str):
        """Получение информации о провиле переноса."""
        return self.transfer(transfer_id=transfer_id)

    @_handle_api_response
    def transfer_switch(self, transfer_id: str, state: bool):
        """Активация/Деактивация периодического правила переноса."""
        return self.post(
            TransferRoutes.SWITCH.format(transfer_id=transfer_id),
            json={'active': state},
        )

    @_handle_api_response
    def transfer_logs(self, transfer_id: str | None = None, history_id: str | None = None):
        """Получение событий по переносу."""
        params: dict[str, int | str] = {'offset': 0, 'limit': 100}
        if transfer_id:
            params['transfer_id'] = transfer_id

        if history_id:
            params['history_id'] = history_id

        return self.get(TransferRoutes.LOGS, params=params)

    @_handle_api_response
    def transfer_cancel(self, transfer_id: str, execution_date: datetime):
        """Остановка выполнения переноса."""
        body = {'transfer_id': transfer_id, 'execution_date': execution_date}

        return self.post(TransferRoutes.CANCEL, json=body)

    @_handle_api_response
    def transfer_update(self, transfer_id: str, params: dict):
        """Обновление периодического правила переноса."""
        t = {}
        try:
            if not self.is_periodic(transfer_id):
                raise click.exceptions.BadParameter(
                    'правило переноса не найдено или перенос не периодический',
                )

            transfer = self.transfer_get(transfer_id)
            if isinstance(transfer, str):
                t = json.loads(transfer)

            elif isinstance(transfer, dict):
                t = transfer
        except Exception as e:
            raise click.ClickException(
                message=f'Не удалось проверить информацию по переданному transfer-id: {e}',
            )

        q = params.get('query', {})
        tu = TransferUpdate(
            cluster_name=params.get('cluster_name', t.get('cluster_name')),
            connector_id=params.get('connector_id', t.get('connector_id')),
            destination_connector_id=params.get(
                'destination_connector_id', t.get('destination_connector_id'),
            ),
            name=params.get('name', t.get('name')),
            favorite=params.get('favorite', t.get('favorite')),
            strategy=params.get('strategy', t.get('strategy')),
            query=q if all([q.get('source'), q.get('destination')]) else t.get('query'),
            connector_type=params.get('connector_type', t.get('source_category')),
            destination_connector_type=params.get(
                'destination_connector_type', t.get('destination_source_category'),
            ),
            description=params.get('description', t.get('description')),
            crontab=params.get('crontab', t.get('crontab')),
        )

        return self.post(
            TransferRoutes.UPDATE.format(transfer_id=transfer_id), json=asdict(tu),
        )

    def is_periodic(self, transfer_id):
        """Проверка, является ли правило переноса периодическим."""
        try:
            res = self.transfer(transfer_id)
            if not res.get('crontab'):
                return False

            ct = CronViewModel(**res.get('crontab'))

            if not any([ct.time, ct.weekdays, ct.monthdays, ct.period]):
                return False

        except requests.exceptions.HTTPError:
            return False

        return True

    @_handle_api_response
    def transfer_history(self, transfer_id: str | None, source_name: str | None):
        """Получение истории правила переноса."""
        params = {}
        if source_name:
            params['source_name'] = source_name

        if transfer_id:
            params['transfer_id'] = transfer_id

        return self.get(TransferRoutes.HISTORY, params=params)
