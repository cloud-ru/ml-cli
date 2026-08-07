"""Утилиты для TensorBoard payload и CLI параметров."""
from typing import Any
from typing import Callable

from .constants import CREATE_REQUIRED_FIELDS
from mls.manager.notebook_service.cli import notebook_service_client
from mls_core import TensorboardApi


__all__ = (
    'missing_create_fields',
    'tensorboard_api',
)


def tensorboard_api(func: Callable[..., Any]) -> Callable[..., Any]:
    """Декоратор создающий TensorBoardApi instance на базе ввода пользователя."""
    return notebook_service_client(TensorboardApi)(func)


def missing_create_fields(payload: dict[str, Any]) -> list[str]:
    """Возвращает список обязательных create-полей, которых нет в payload."""
    image = payload.get('image') or {}
    checks = {
        'name': payload.get('name'),
        'image.name': image.get('name'),
        'image.tag': image.get('tag'),
        'image.type': image.get('type'),
        'instance_type': payload.get('instance_type'),
        'logdir': payload.get('logdir'),
    }
    return [field for field in CREATE_REQUIRED_FIELDS if not checks[field]]
