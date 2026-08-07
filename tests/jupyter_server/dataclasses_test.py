"""Тесты dataclass-контракта Jupyter Server payload."""
import pytest

from mls.manager.jupyter_server.dataclasses import JupyterServerCreatePayload
from mls.manager.jupyter_server.dataclasses import JupyterServerResumePayload


def test_create_payload_rejects_unknown_fields():
    """YAML/API mapping create отклоняет поля вне контракта."""
    payload = {
        'name': 'nb',
        'image': {'name': 'image', 'tag': 'latest', 'type': 'datahub'},
        'instance_type': 'free.0gpu',
        'region': 'SR006',
        'unsupported_field': 'value',
    }

    with pytest.raises(ValueError, match='Недопустимые поля Jupyter Server create'):
        JupyterServerCreatePayload.from_api_mapping(payload)


def test_create_payload_reports_required_fields():
    """YAML/API mapping create перечисляет недостающие обязательные поля."""
    payload = {
        'name': 'nb',
        'image': {'name': 'image', 'type': 'datahub'},
    }

    with pytest.raises(ValueError, match='image.tag.*instance_type'):
        JupyterServerCreatePayload.from_api_mapping(payload)


def test_resume_payload_rejects_unknown_fields():
    """YAML/API mapping resume отклоняет поля вне backend-контракта."""
    payload = {
        'region': 'SR006',
        'instance_type': 'free.0gpu',
        'reason': 'manual',
    }

    with pytest.raises(ValueError, match='Недопустимые поля Jupyter Server resume'):
        JupyterServerResumePayload.from_api_mapping(payload)
