"""Тесты имитирующие ошибки не связанные с работой cli."""
import socket
from unittest.mock import MagicMock
from unittest.mock import patch

import click
import requests
import urllib3
from urllib3.connection import HTTPConnection
from urllib3.connectionpool import ConnectionPool

from mls.cli import auto_complete_function
from mls.cli import entry_point
from mls.utils.common import suggest_autocomplete
from mls.utils.execption import ConfigReadError
from mls.utils.execption import ConfigWriteError
from mls.utils.style import error_format


def test_entry_point_success():
    """Тест успешного вызова cli() без исключений."""
    with patch('mls.cli.cli') as mock_cli:
        entry_point()
        mock_cli.assert_called_once_with(standalone_mode=False)


def test_entry_point_config_read_error():
    """Тест обработки исключения ConfigReadError."""
    with patch('mls.cli.cli') as mock_cli, patch('mls.cli.click.echo') as mock_echo:
        mock_cli.side_effect = ConfigReadError('Ошибка чтения конфигурации')
        entry_point()
        mock_echo.assert_called_once_with(error_format('Ошибка чтения конфигурации'))


@patch('mls.cli.cli')
@patch('mls.cli.click.echo')
def test_entry_point_config_write_error(mock_echo, mock_cli):
    """Тест обработки ConfigWriteError."""
    mock_cli.side_effect = ConfigWriteError('ошибка записи конфигурации')
    entry_point()
    error_text, *_ = [execution.args for execution in mock_echo.mock_calls][0]
    assert error_text == '\x1b[31m\x1b[1mошибка записи конфигурации\x1b[0m'


@patch('mls.cli.cli')
@patch('mls.cli.click.echo')
def test_entry_point_click_exception(mock_echo, mock_cli):
    """Тест обработки click.ClickException."""
    error = click.ClickException('click exception')
    error.ctx = MagicMock()
    mock_cli.side_effect = error
    entry_point()
    error_text, *_ = [execution.args for execution in mock_echo.mock_calls][1]
    assert error_text == '\x1b[31m\x1b[1mclick exception\x1b[0m'


@patch('mls.cli.cli')
@patch('mls.cli.click.echo')
def test_entry_point_abort(mock_echo, mock_cli):
    """Тест обработки click.exceptions.Abort."""
    error = mock_cli.side_effect = click.exceptions.Abort()
    error.ctx = MagicMock()
    mock_cli.side_effect = error
    entry_point()
    error_text, *_ = [execution.args for execution in mock_echo.mock_calls][0]
    assert error_text == '\x1b[22mОборвано пользователем\x1b[0m'


@patch('mls.cli.cli')
@patch('mls.cli.click.echo')
def test_entry_point_max_retry_error(mock_echo, mock_cli):
    """Тест обработки urllib3.exceptions.MaxRetryError."""
    mock_cli.side_effect = urllib3.exceptions.MaxRetryError(ConnectionPool('abc.com', 80), url='http://abc.com')
    entry_point()
    error_text, *_ = [execution.args for execution in mock_echo.mock_calls][0]
    assert error_text == '\x1b[31m\x1b[1mДостигнут предел по количеству обращений к http://abc.com\x1b[0m'


@patch('mls.cli.cli')
@patch('mls.cli.click.echo')
def test_entry_point_name_resolution_error(mock_echo, mock_cli):
    """Тест обработки urllib3.exceptions.NameResolutionError."""
    mock_cli.side_effect = urllib3.exceptions.NameResolutionError('abc.com', HTTPConnection('abc.com'), socket.gaierror())
    entry_point()
    error_text, *_ = [execution.args for execution in mock_echo.mock_calls][0]
    assert error_text == '\x1b[31m\x1b[1mОшибка разрешения ip адреса при обращении к домену abc.com\x1b[0m'


@patch('mls.cli.cli')
@patch('mls.cli.click.echo')
def test_entry_point_connection_error(mock_echo, mock_cli):
    """Тест обработки requests.exceptions.ConnectionError."""
    mock_cli.side_effect = requests.exceptions.ConnectionError()
    entry_point()
    error_text, *_ = [execution.args for execution in mock_echo.mock_calls][0]
    assert error_text == '\x1b[31m\x1b[1mНе удалось установить соединение за указанное время\x1b[0m'


def test_cli_autocomplete():
    """Тест наполнения map для cli."""
    mapping = {}
    auto_complete_function(mapping)
    assert mapping['mls job restart'] == ['name', '--debug', '--endpoint_url', '--output', '--profile', '--region']


def test_cli_suggest():
    """Тестирование предполагаемых предложений по вводу для пользователя."""
    mapping = {}
    auto_complete_function(mapping)
    assert suggest_autocomplete('mls job re', mapping) == ['restart']
    assert suggest_autocomplete('mls job ru', mapping) == ['run']
    assert suggest_autocomplete('mls j', mapping) == ['job']
    assert suggest_autocomplete('mls co', mapping) == ['configure']
