"""Тесты dataclass-контракта TensorBoard payload."""
import pytest

from mls.manager.tensorboard.dataclasses import TensorboardCreatePayload
from tests.tensorboard.data import CREATE_TENSORBOARD_PAYLOAD


def test_create_payload_requires_logdir_string_list():
    """YAML/API mapping create принимает logdir только как список строк."""
    payload = {
        **CREATE_TENSORBOARD_PAYLOAD,
        'logdir': '/home/jovyan/logs',
    }

    with pytest.raises(ValueError, match='logdir'):
        TensorboardCreatePayload.from_api_mapping(payload)


def test_create_payload_requires_tensorboard_params_string_mapping():
    """YAML/API mapping create принимает tensorboard_params как dict[str, str]."""
    payload = {
        **CREATE_TENSORBOARD_PAYLOAD,
        'tensorboard_params': {'--port': 6006},
    }

    with pytest.raises(ValueError, match='tensorboard_params'):
        TensorboardCreatePayload.from_api_mapping(payload)
