"""Константы CLI команд TensorBoard."""
from mls.manager.notebook_service.constants import CREATE_ALLOWED_FIELDS as COMMON_CREATE_ALLOWED_FIELDS
from mls.manager.notebook_service.constants import CREATE_REQUIRED_FIELDS as COMMON_CREATE_REQUIRED_FIELDS
from mls.utils.common_types import RussianChoice

IMAGE_TYPES = ('datahub', 'custom')

TENSORBOARD_IMAGE_TYPE_CHOICE = RussianChoice(IMAGE_TYPES)

TENSORBOARD_INSTANCE_TYPE_HELP = 'Конфигурация ресурсов'
TENSORBOARD_REGION_HELP = (
    'Ключ региона. '
    'Если не указан, используется регион из профиля'
)

CREATE_REQUIRED_FIELDS = (
    *COMMON_CREATE_REQUIRED_FIELDS,
    'logdir',
)

CREATE_ALLOWED_FIELDS = (
    *COMMON_CREATE_ALLOWED_FIELDS,
    'logdir',
    'tensorboard_params',
)

CREATE_MANIFEST_BODY_KEY = 'tensorboard'
RESUME_MANIFEST_BODY_KEY = 'resume'
