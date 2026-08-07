"""Константы CLI Jupyter Server."""
from mls.manager.notebook_service.constants import CREATE_ALLOWED_FIELDS as COMMON_CREATE_ALLOWED_FIELDS
from mls.manager.notebook_service.constants import CREATE_REQUIRED_FIELDS as COMMON_CREATE_REQUIRED_FIELDS
from mls.utils.common_types import RussianChoice

IMAGE_TYPES = ('datahub', 'custom')

JS_IMAGE_TYPE_CHOICE = RussianChoice(IMAGE_TYPES)

JS_REGION_HELP = (
    'Ключ региона.'
    'Если не указан, используется регион из профиля'
)
JS_CREATE_INSTANCE_TYPE_HELP = 'Конфигурация ресурсов'

CREATE_REQUIRED_FIELDS = COMMON_CREATE_REQUIRED_FIELDS
CREATE_ALLOWED_FIELDS = COMMON_CREATE_ALLOWED_FIELDS

RESUME_ALLOWED_FIELDS = (
    'region',
    'instance_type',
)

CREATE_MANIFEST_BODY_KEY = 'jupyter_server'
RESUME_MANIFEST_BODY_KEY = 'resume'
