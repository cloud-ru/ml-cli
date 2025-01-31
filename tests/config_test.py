"""Тестовые сценарии для проверки работы профилей."""
import os
from itertools import combinations

import pytest
from click.testing import CliRunner

from mls.cli import configure
from mls.manager.configure.utils import configure_profile
from mls.manager.configure.utils import mask_secret
from mls.utils.common import load_saved_config


@pytest.fixture
def config_env(monkeypatch):
    """Фикстура замены профиля ~.mls.

    Параметры:
            monkeypatch: FixtureFunction

    Фикстура подменяет CONFIG_FILE и CREDENTIALS_FILE на /tmp
    """
    tmp_config_file = '/tmp/test/config'
    tmp_credentials_file = '/tmp/test/credentials'
    monkeypatch.setattr('mls.utils.settings.CONFIG_FILE', tmp_config_file)
    monkeypatch.setattr('mls.utils.common.CONFIG_FILE', tmp_config_file)
    monkeypatch.setattr('mls.manager.configure.utils.CONFIG_FILE', tmp_config_file)

    monkeypatch.setattr('mls.utils.common.CREDENTIALS_FILE', tmp_credentials_file)
    monkeypatch.setattr('mls.utils.settings.CREDENTIALS_FILE', tmp_credentials_file)
    monkeypatch.setattr('mls.manager.configure.utils.CREDENTIALS_FILE', tmp_credentials_file)

    return tmp_config_file, tmp_credentials_file


@pytest.fixture
def config_clean(config_env, request):
    """Фикстура удаления профиля.

    Фикстура обращается за измененным профилем через config_env и
    обеспечивает удаление конфигурационных файлов после тестов

    Параметры:
            config_env: FixtureFunction
            request: FixtureFunction

    Возвращает:
        tuple(str, str): Пути к расположению конфигурационных файлов
    """

    def fin():
        for item in config_env:
            if os.path.isfile(item):
                os.remove(item)

    fin()
    request.addfinalizer(fin)
    return config_env


@pytest.fixture
def profile_read(config_clean):  # TODO
    """Фикстура чтения профиля.

    Фикстура прочитывает файлы

    Параметры:
            config_clean: FixtureFunction

    Возвращает:
        tuple(ConfigParser, ConfigParser): ConfigParser для config и crededentials
    """

    def _tmp_config(name):
        configure_profile(name)
        return load_saved_config()

    return _tmp_config


@pytest.fixture
def mock_inputs(monkeypatch):
    """Фикстура имитации ввода пользователя.

    Фикстура подменяет builtins.input на генератор

    Параметры:
            config_clean: FixtureFunction

    Возвращает:
        tuple(ConfigParser, ConfigParser): ConfigParser для config и crededentials
    """

    def _mock(inputs):
        api_key, secret, region, workspace_id, output, x_api_key = inputs
        updated_inputs = [
            api_key or '', secret or '',
            region or '', workspace_id or '',
            output or '', x_api_key or '',
        ]
        inputs_iter = iter(updated_inputs)
        monkeypatch.setattr('builtins.input', lambda prompt: next(inputs_iter))
        return updated_inputs

    return _mock


@pytest.mark.parametrize(
    'profile_name, inputs', [
        (
            'default', [
                'my_api_key_default', 'my_secret_key_default',
                'workspace_id_default', 'x_api_key', 'DGX-MT', 'text',
            ],
        ),
        (
            'custom_profile', [
                'my_api_key', 'my_secret_key',
                '00000000-0000-0000-0000-000000000000', 'x_api_key', 'DGX-MT', '',
            ],
        ),
        (
            'custom_profile', [
                'my_api_key', 'my_secret_key',
                '00000000-0000-0000-0000-000000000000', 'x_api_key', 'DGX-MT', 'json',
            ],
        ),
    ],
)
def test_configure_profile(profile_read, mock_inputs, profile_name, inputs):
    """Тест соответствия ввода пользователя для настройки профиля custom_profile файлам конфигурации."""
    api_key, secret, workspace_id, x_api_key, region, output = mock_inputs(inputs)
    config, crededentials = profile_read(profile_name)
    assert config.has_section(profile_name)
    assert crededentials.has_section(profile_name)
    assert crededentials.get(profile_name, 'mls_apikey_id') == api_key
    assert crededentials.get(profile_name, 'mls_apikey_secret') == secret
    assert crededentials.get(profile_name, 'workspace_id') == workspace_id
    assert crededentials.get(profile_name, 'x_api_key') == x_api_key

    assert config.get(profile_name, 'region') == region
    assert config.get(profile_name, 'output') == output


options = ([
    'my_api_key', 'my_secret_key', 'DGX-MT',
    'workspace_id', 'output', 'x_api_key',
])

combinations_one_none = [  # type: ignore
    options[:i] + [None] +  # type: ignore
    options[i + 1:] for i in range(len(options))  # type: ignore
]  # type: ignore

combinations_with_two_none = [
    [None if i in pair else options[i] for i in range(len(options))] for pair in combinations(range(len(options)), 2)
]


@pytest.mark.parametrize(
    'inputs', [
        *combinations_one_none,
        *combinations_with_two_none,
    ],
)
def test_configure_profile_default(profile_read, mock_inputs, inputs):
    """Тест соответствия ввода пользователя без указания имени профиля файлам конфигурации."""
    api_key, secret, workspace_id, x_api_key, region, output = mock_inputs(
        inputs,
    )
    config, crededentials = profile_read(None)
    assert crededentials.has_section('default')
    assert config.has_section('default')
    assert crededentials.get('default', 'mls_apikey_id') == api_key
    assert crededentials.get('default', 'mls_apikey_secret') == secret
    assert crededentials.get('default', 'workspace_id') == workspace_id
    assert crededentials.get('default', 'x_api_key') == x_api_key

    assert config.get('default', 'output') == output
    assert config.get('default', 'region') == region


def test_mask_secret():
    """Тест маскировки секстетов при выводе в консоль."""
    assert not mask_secret(None)
    assert not mask_secret('')
    assert mask_secret(secret='123') == '**3'
    assert mask_secret(secret='1231') == '***1'
    assert mask_secret(secret='123456789---z') == '...********z'
    assert mask_secret(secret='123456789--z') == '***********z'
    assert mask_secret(secret='12345678') == '*******8'
    assert mask_secret(secret='123456789') == '********9'


def test_configure_with_prompt(monkeypatch, profile_read):
    """Тест многократного ввода без перезаписи профиля."""
    inputs = iter(
        [
            'my_api_key\n', 'my_secret_key\n', '00000000-0000-0000-0000-000000000000\n', 'x-api-key\n',
            'DGX-MT\n', '\n',
        ] + ['', '', '', ''] * 3,
    )
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    runner = CliRunner()
    runner.invoke(configure, ['--profile', 'Alice'])
    result = runner.invoke(configure, ['--profile', 'Alice'])
    config, crededentials = profile_read('Alice')

    assert result.exit_code == 0, result.output
    assert "Профиль 'Alice' успешно сохранен!" in result.output
    assert crededentials.get('Alice', 'mls_apikey_id') == 'my_api_key'
    assert crededentials.get('Alice', 'mls_apikey_secret') == 'my_secret_key'
    assert crededentials.get('Alice', 'workspace_id') == '00000000-0000-0000-0000-000000000000'
    assert crededentials.get('Alice', 'x_api_key') == 'x-api-key'

    assert config.get('Alice', 'region') == 'DGX-MT'
    assert not config.get('Alice', 'output')

# TODO Добавить тест на отсутствие профиля
