"""Модуль содержащий клиентов для работы с платформой MLSPACE."""
import http.client
import json
import logging
import sys
import time
from functools import wraps

import requests
from requests.adapters import HTTPAdapter  # type: ignore
from requests.sessions import ChunkedEncodingError  # type: ignore
from urllib3.util.retry import Retry

from mls_core.exeptions import AuthorizationError
from mls_core.exeptions import DataStreamingFailure


class _CommonPublicApiInterface:
    """API клиент."""
    AUTH_ENDPOINT = 'service_auth'

    def __init__(
            self,
            endpoint_url: str,
            client_id: str,
            client_secret: str,
            workspace_id: str,
            x_api_key: str,
            max_retries: int = 3,  # TODO Вынести опции в settings core проекта
            backoff_factor: float = 0.3,  # TODO Вынести опции в settings
            connect_timeout: int = 5,  # TODO Вынести опции в settings
            read_timeout: int = 5,  # TODO Вынести опции в settings
            debug: bool = False,

    ):
        """Инициализация класса PublicApi.

        :param endpoint_url: Базовый URL API.
        :param client_id: Идентификатор клиента.
        :param client_secret: Секрет клиента.
        :param workspace_id: Идентификатор воркспейса
        :param x_api_key: ключ доступа к воркспейсу
        :param max_retries: Максимальное количество попыток повторного запроса.
        :param backoff_factor: Фактор экспоненциальной задержки между повторными попытками.
        :param connect_timeout: Таймаут подключения (в секундах).
        :param read_timeout: Таймаут чтения (в секундах).
        :param debug: Включение отладочного режима.

        """
        self._endpoint_url = endpoint_url
        self._connect_timeout = connect_timeout
        self._read_timeout = read_timeout

        self._logger = self._create_logger(debug)
        self._init_session(backoff_factor, max_retries)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        headers = {
            'authorization': self._get_auth_token(client_id, client_secret),
            'x-workspace-id': workspace_id,
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
                'HEAD', 'GET', 'PUT',
                'DELETE', 'OPTIONS', 'POST',
            ],
        )

        session.mount('https://', HTTPAdapter(max_retries=retries))
        self._session = session

    def _create_logger(self, debug: bool):  # TODO Настройка форматтера settings
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.WARNING)

        handler = logging.StreamHandler(sys.stdout)
        # TODO Настройка форматтера settings core проетка
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s:%(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        # Включает отладочный вывод для `requests`, `urllib3` и `http.client`.
        if debug:
            # Включаем отладку для http.client (работает только в Python 3)
            http.client.HTTPConnection.debuglevel = 1

            # Настройка логирования для библиотеки `requests` и `urllib3`
            logging.basicConfig()
            logging.getLogger('urllib3').setLevel(logging.DEBUG)
            logging.getLogger('urllib3').propagate = True

            logger.setLevel(logging.DEBUG)

        return logger

    def _request(self, method: str, path: str, **kwargs):
        timeout = kwargs.pop(
            'timeout', (self._connect_timeout, self._read_timeout),
        )
        headers = kwargs.pop('headers', {})

        try:
            response = self._session.request(
                method, f'{self._endpoint_url}/{path}', headers=headers, timeout=timeout, **kwargs,
            )
            response.raise_for_status()
        except requests.exceptions.RetryError as ex:
            self._logger.debug(ex)
        else:
            if response.headers.get('content-type') == 'application/json':
                return response.json()
            else:
                return response.text

    def _get_auth_token(self, client_id: str, client_secret: str):
        try:
            response: dict = self.post(
                self.AUTH_ENDPOINT, json={
                    'client_id': client_id, 'client_secret': client_secret,
                },
            )
        except requests.exceptions.HTTPError as ex:
            self._logger.debug(ex)
            raise AuthorizationError(ex)
        return response['token']['access_token']

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


class TrainingJobApi(_CommonPublicApiInterface):
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
            else:
                return result
        else:
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
    def get_job_logs(self, name: str, region: str, tail: int = 0, verbose: bool = False):
        """Получение логов задачи."""
        params = {'region': region, 'tail': tail, 'verbose': verbose}
        return self.get(f'jobs/{name}/logs', params=params)

    @_handle_api_response
    def get_job_status(self, name, region):
        """Получение статуса задачи."""
        return self.get(f'jobs/{name}')

    @_handle_api_response
    def get_list_jobs(self, region, allocation_name, status, limit, offset):
        """Получение логов задачи."""
        params = {
            'region': region, 'allocation_name': allocation_name,
            'status': status, 'limit': limit, 'offset': offset,
        }
        return self.get('jobs', params=params)

    @_handle_api_response
    def get_pods(self, name, region):
        """Вызов получения списка подов для задач pytorch (elastic) или spark."""
        return self.get(f'jobs/spark/{name}/pods')

    @_handle_api_response
    def delete_job(self, name, region):
        """Вызов завершения работы задачи."""
        params = {'region': region}
        return self.delete(f'jobs/{name}', params=params)

    @_handle_api_response
    def restart_job(self, name, region):
        """Вызов перезапуска задачи."""
        payload = {'job_name': name}
        return self.post('jobs/restart', json=payload)

    @_handle_api_response
    def run_job(self, payload):
        """Вызов запуска задачи."""
        return self.post('jobs', json=payload)

    def stream(self, method: str, path: str, **kwargs):
        """Выполняет HTTP запрос с использованием заданного метода к указанному пути возвращает данные порционно(потоково).

        :param method: HTTP метод запроса
        :param path: Путь запроса, который будет добавлен к базовому URL
        :param kwargs: Дополнительные параметры запроса.
        :return: Генератор, который возвращает данные ответа по частям. В случае ошибки запроса возвращает статус ответа с описанием ошибки.
        """
        timeout = kwargs.pop('timeout', (self._connect_timeout, self._read_timeout))
        headers = kwargs.pop('headers', {})
        try:
            response = self._session.request(
                method, f'{self._endpoint_url}/{path}', headers=headers, timeout=timeout,  stream=True, **kwargs,
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
                for chunk in response.iter_content(chunk_size=256, decode_unicode=True):
                    yield chunk
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
