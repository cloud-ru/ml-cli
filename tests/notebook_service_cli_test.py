"""Тесты общего CLI-слоя notebook-сервисов."""
from pathlib import Path

import pytest

from mls.manager.notebook_service.cli import parse_optional_json_array
from mls.manager.notebook_service.cli import parse_optional_json_object
from mls.manager.notebook_service.cli import parse_optional_string_mapping_json_object
from mls.manager.notebook_service.cli import resolve_region


def test_notebook_service_cli_parses_json_helpers():
    """Общий слой парсит JSON-опции для Jupyter Server и TensorBoard."""
    assert parse_optional_json_array('[{"bucket_name": "b"}]') == [{'bucket_name': 'b'}]
    assert parse_optional_json_object('{"s3_credentials_source": "iam-product-sa"}') == {
        's3_credentials_source': 'iam-product-sa',
    }


def test_notebook_service_cli_rejects_non_string_mapping_values():
    """String mapping helper отклоняет нестроковые значения."""
    with pytest.raises(ValueError, match='tensorboard_params'):
        parse_optional_string_mapping_json_object('{"--port": 6006}', 'tensorboard_params')


def test_notebook_service_cli_resolves_region_from_profile():
    """Регион берётся из CLI/YAML или профиля пользователя."""
    assert resolve_region(None, 'SR008') == 'SR008'


@pytest.mark.parametrize(
    'path',
    [
        Path('mls/manager/jupyter_server/utils.py'),
        Path('mls/manager/tensorboard/utils.py'),
    ],
)
def test_notebook_service_utils_do_not_disable_duplicate_code(path):
    """JS/TensorBoard utils не должны скрывать реальное дублирование."""
    assert 'disable=duplicate-code' not in path.read_text(encoding='utf-8')


def test_notebook_service_shared_layer_does_not_contain_trivial_dict_helpers():
    """Общий слой не должен собирать локальные list/modify kwargs словари."""
    source = Path('mls/manager/notebook_service/cli.py').read_text(encoding='utf-8')

    assert 'def list_query_params' not in source
    assert 'def modify_payload_kwargs' not in source
    assert 'def modify_api_body_or_usage_error' not in source


def test_manager_utils_keep_manager_specific_api_decorators():
    """Локальные utils сохраняют manager-specific API helpers."""
    jupyter_utils = Path('mls/manager/jupyter_server/utils.py').read_text(encoding='utf-8')
    tensorboard_utils = Path('mls/manager/tensorboard/utils.py').read_text(encoding='utf-8')

    assert 'def jupyter_server_api' in jupyter_utils
    assert 'JupyterServerApi' in jupyter_utils
    assert 'def tensorboard_api' in tensorboard_utils
    assert 'TensorboardApi' in tensorboard_utils
