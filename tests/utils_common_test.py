"""Тестовые сценарии для проверки работы utils.common."""
from configparser import NoSectionError
from unittest.mock import MagicMock
from unittest.mock import patch

import click
import pytest

from mls.manager.job.utils import read_profile
from mls.utils.common import handle_click_exception
from mls.utils.common import load_saved_config
from mls.utils.execption import ConfigReadError


def test_read_profile():
    """Тест для имитации успешного чтения."""
    with patch('mls.utils.common.ConfigParser') as mock_config:
        mock_config.return_value.read.return_value = True
        mock_config.return_value.items.return_value = [('output', 'json')]
        assert read_profile('default') == {'output': 'json'}


def test_read_profile_no_section():
    """Тестирование вызова исключения при отсутствии секции."""
    with patch('mls.utils.common.ConfigParser') as mock_config:
        mock_config.return_value.read.return_value = True
        mock_config.return_value.items.side_effect = NoSectionError('abc')
        with pytest.raises(ConfigReadError):
            read_profile('abc')


def test_load_saved_config():
    """Тест вызова чтения из ConfigParser."""
    with (
        patch('mls.utils.common.ConfigParser') as mock_config,
        patch('mls.utils.common.CONFIG_FILE', 'path/to/config_file'),
        patch('mls.utils.common.CREDENTIALS_FILE', 'path/to/credentials_file'),
    ):
        mock_config.return_value.read.return_value = True
        mock_config.return_value.read_string.return_value = True

        config, credentials = load_saved_config()

        assert config.read.call_count == 1
        assert credentials.read_string.call_count == 1


@pytest.fixture
def mock_ctx():
    """Фикстура для создания мокированного контекста click."""
    ctx = MagicMock(spec=click.Context)
    ctx.get_help.return_value = 'Используйте эту команду так...'
    return ctx


@patch('mls.utils.common.click.echo')
def test_handle_click_exception_with_no_such_option(mock_echo, mock_ctx):
    """Тестирование обработки исключения при отсутствии опции."""
    err = click.NoSuchOption(option_name='--nonexistent', message='No such option')

    handle_click_exception(err, mock_ctx)
    help_text, error_message = [execution.args for execution in mock_echo.mock_calls]
    red_color_start = '\x1b[31m\x1b[1m'
    red_color_end = '\x1b[0m'
    assert help_text == ('Используйте эту команду так...',)
    assert error_message == (f'{red_color_start}Ошибка: отсутствует опция: --nonexistent{red_color_end}',)


@patch('mls.utils.common.click.echo')
def test_handle_click_exception_with_missing_parameter(mock_echo, mock_ctx):
    """Тестирование обработки исключения при отсутствующем параметре."""
    err = click.MissingParameter(message='Не существует такого параметра')
    handle_click_exception(err, mock_ctx)
    help_text, error_message = [execution.args for execution in mock_echo.mock_calls]
    red_color_start = '\x1b[31m\x1b[1m'
    red_color_end = '\x1b[0m'
    assert help_text == ('Используйте эту команду так...',)
    assert error_message == (f'{red_color_start}Ошибка: отсутствует параметр: {red_color_end}',)
