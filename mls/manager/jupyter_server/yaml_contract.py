"""YAML-манифест и примеры для команд Jupyter Server CLI."""
from typing import Any

import yaml  # type: ignore[import-untyped]

from .constants import CREATE_MANIFEST_BODY_KEY
from .constants import RESUME_MANIFEST_BODY_KEY


def jupyter_server_create_example_yaml() -> str:
    """Возвращает пример YAML для `mls js create --config` (namespace + jupyter_server).

    Returns:
        Текст YAML с ключами верхнего уровня ``namespace`` и ``jupyter_server``.
    """
    payload: dict[str, Any] = {
        'name': 'my-notebook',
        'image': {
            'name': 'cr.ai.cloud.ru/aicloud-jupyter/jupyter-server',
            'tag': 'latest',
            'type': 'datahub',
        },
        'instance_type': 'free.0gpu',
        'postponed_pause_enabled': False,
        'allocation_name': 'my-allocation',
        'queue_name': 'my-queue',
        'description': 'Описание Jupyter Server',
        'pause_at': '45 * * * *',
        's3_buckets': [{'bucket_name': 'bucket-name', 'access_rule': 'ro'}],
        's3_credentials': {
            's3_credentials_source': 'iam-product-sa',
            's3_tenant_id': 'tenant_id',
        },
    }
    manifest: dict[str, Any] = {
        'namespace': 'default',
        CREATE_MANIFEST_BODY_KEY: payload,
    }
    dumped = yaml.dump(manifest, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return str(dumped)


def jupyter_server_resume_example_yaml() -> str:
    """Возвращает пример YAML для `mls js resume --config` (namespace + resume).

    Returns:
        Текст YAML с ключами верхнего уровня ``namespace`` и ``resume``.
    """
    payload: dict[str, Any] = {
        'instance_type': 'free.0gpu',
    }
    manifest: dict[str, Any] = {
        'namespace': 'default',
        RESUME_MANIFEST_BODY_KEY: payload,
    }
    dumped = yaml.dump(manifest, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return str(dumped)
