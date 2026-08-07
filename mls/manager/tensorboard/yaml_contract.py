"""YAML-манифест и примеры для TensorBoard CLI."""
from typing import Any

import yaml  # type: ignore[import-untyped]

from .constants import CREATE_MANIFEST_BODY_KEY
from .constants import RESUME_MANIFEST_BODY_KEY


def tensorboard_create_example_yaml() -> str:
    """Возвращает пример YAML для `mls tensorboard create --config`."""
    manifest: dict[str, Any] = {
        'namespace': 'default',
        CREATE_MANIFEST_BODY_KEY: {
            'name': 'my-tensorboard',
            'image': {
                'name': 'cr.ai.cloud.ru/aicloud-tensorboard/tensorboard-server',
                'tag': 'latest',
                'type': 'datahub',
            },
            'instance_type': 'free.0gpu',
            'logdir': ['/home/jovyan/logs'],
            'postponed_pause_enabled': False,
            'tensorboard_params': {'--port': '6006'},
            's3_buckets': [{'bucket_name': 'test', 'access_rule': 'ro'}],
            's3_credentials': {
                's3_credentials_source': 'iam-product-sa',
                's3_tenant_id': 'tenant_id',
            },
        },
    }
    dumped = yaml.dump(manifest, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return str(dumped)


def tensorboard_resume_example_yaml() -> str:
    """Возвращает пример YAML для `mls tensorboard resume --config`."""
    manifest: dict[str, Any] = {
        'namespace': 'default',
        RESUME_MANIFEST_BODY_KEY: {
            'instance_type': 'free.0gpu',
        },
    }
    dumped = yaml.dump(manifest, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return str(dumped)
