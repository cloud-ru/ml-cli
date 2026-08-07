"""Dataclasses для тел запросов API TensorBoard, собираемых из CLI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import click
from click.core import ParameterSource

from .constants import CREATE_ALLOWED_FIELDS
from .constants import CREATE_MANIFEST_BODY_KEY
from .constants import RESUME_MANIFEST_BODY_KEY
from .create_cli_options import CREATE_CLI_FLAGS
from .create_cli_options import CREATE_CLI_PARAM_NAMES
from .create_cli_options import CREATE_CLI_REQUIRED_PARAM_NAMES
from .resume_cli_options import RESUME_CLI_FLAGS
from .resume_cli_options import RESUME_CLI_PARAM_NAMES
from .resume_cli_options import RESUME_CLI_REQUIRED_PARAM_NAMES
from .utils import missing_create_fields
from mls.manager.notebook_service.cli import resolve_region
from mls.manager.utils import read_yaml


def _explicit_cli_names(param_names: tuple[str, ...]) -> set[str]:
    """Возвращает имена параметров, которые пользователь явно передал в CLI/env."""
    ctx = click.get_current_context(silent=True)
    if ctx is None:
        return set()
    return {
        param_name
        for param_name in param_names
        if ctx.get_parameter_source(param_name) in (ParameterSource.COMMANDLINE, ParameterSource.ENVIRONMENT)
    }


def _merge_create_cli_overrides(manifest: dict[str, Any], cli: dict[str, Any]) -> dict[str, Any]:
    """Накладывает на create-манифест только явно переданные CLI-опции."""
    merged = dict(manifest)
    image = dict(merged.get('image') or {})
    explicit = _explicit_cli_names(CREATE_CLI_PARAM_NAMES)
    for cli_name, api_name in (
        ('name', 'name'),
        ('instance_type', 'instance_type'),
        ('region', 'region'),
        ('allocation_name', 'allocation_name'),
        ('queue_name', 'queue_name'),
        ('description', 'description'),
        ('pause_at', 'pause_at'),
        ('postponed_pause_enabled', 'postponed_pause_enabled'),
        ('s3_buckets_json', 's3_buckets'),
        ('s3_credentials_json', 's3_credentials'),
        ('logdir', 'logdir'),
        ('tensorboard_params', 'tensorboard_params'),
    ):
        if cli_name in explicit:
            value = cli.get(cli_name)
            merged[api_name] = list(value or ()) if cli_name == 'logdir' else value
    for cli_name, image_name in (
        ('image_name', 'name'),
        ('image_tag', 'tag'),
        ('image_type', 'type'),
    ):
        if cli_name in explicit:
            image[image_name] = cli.get(cli_name)
    if image:
        merged['image'] = image
    return merged


def _merge_resume_cli_overrides(manifest: dict[str, Any], cli: dict[str, Any]) -> dict[str, Any]:
    """Накладывает на resume-манифест только явно переданные CLI-опции."""
    merged = dict(manifest)
    explicit = _explicit_cli_names(RESUME_CLI_PARAM_NAMES)
    for cli_name in ('region', 'instance_type'):
        if cli_name in explicit:
            merged[cli_name] = cli.get(cli_name)
    return merged


def _require_string_list(value: Any, field_name: str) -> list[str]:
    """Проверяет, что значение является списком строк."""
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f'Поле {field_name} должно быть списком строк')
    return value


def _optional_string_mapping(value: Any, field_name: str) -> dict[str, str] | None:
    """Проверяет, что optional-значение является словарём строк."""
    if value is None:
        return None
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str)
        for key, item in value.items()
    ):
        raise ValueError(f'Поле {field_name} должно быть словарём со строковыми ключами и значениями')
    return value


@dataclass(frozen=True)
class TensorboardImagePayload:
    """Фрагмент тела запроса: конфигурация образа."""

    name: str
    tag: str
    type: str

    def to_api_fragment(self) -> dict[str, str]:
        """Возвращает объект image для JSON тела запроса."""
        return {'name': self.name, 'tag': self.tag, 'type': self.type}


@dataclass(frozen=True)
class TensorboardCreatePayload:
    """Тело запроса создания инстанса TensorBoard."""

    name: str
    image: TensorboardImagePayload
    instance_type: str
    logdir: list[str]
    region: str
    postponed_pause_enabled: bool = False
    allocation_name: str | None = None
    queue_name: str | None = None
    description: str | None = None
    pause_at: str | None = None
    s3_buckets: list[Any] | None = None
    s3_credentials: dict[str, Any] | None = None
    tensorboard_params: dict[str, Any] | None = None

    def to_api_dict(self) -> dict[str, Any]:
        """Собирает словарь для `TensorboardApi.create_tensorboard`."""
        body: dict[str, Any] = {
            'name': self.name,
            'image': self.image.to_api_fragment(),
            'instance_type': self.instance_type,
            'logdir': self.logdir,
            'region': self.region,
            'postponed_pause_enabled': self.postponed_pause_enabled,
        }
        if self.allocation_name:
            body['allocation_name'] = self.allocation_name
        if self.queue_name:
            body['queue_name'] = self.queue_name
        if self.description:
            body['description'] = self.description
        if self.pause_at:
            body['pause_at'] = self.pause_at
        if self.s3_buckets is not None:
            body['s3_buckets'] = self.s3_buckets
        if self.s3_credentials is not None:
            body['s3_credentials'] = self.s3_credentials
        if self.tensorboard_params:
            body['tensorboard_params'] = self.tensorboard_params
        return body

    @classmethod
    def from_api_mapping(cls, data: dict[str, Any], region: str | None = None) -> 'TensorboardCreatePayload':
        """Собирает payload из словаря в форме тела Public API."""
        unknown = sorted(set(data) - set(CREATE_ALLOWED_FIELDS))
        if unknown:
            raise ValueError(f'Недопустимые поля TensorBoard create: {", ".join(unknown)}')
        missing = missing_create_fields(data)
        if missing:
            joined = ', '.join(missing)
            raise ValueError(f'В секции {CREATE_MANIFEST_BODY_KEY} не хватает обязательных полей: {joined}')

        image = data['image']
        return cls(
            name=data['name'],
            image=TensorboardImagePayload(
                name=image['name'],
                tag=image['tag'],
                type=image['type'],
            ),
            instance_type=data['instance_type'],
            logdir=_require_string_list(data['logdir'], 'logdir'),
            region=resolve_region(data.get('region'), region),
            postponed_pause_enabled=bool(data.get('postponed_pause_enabled', False)),
            allocation_name=data.get('allocation_name'),
            queue_name=data.get('queue_name'),
            description=data.get('description'),
            pause_at=data.get('pause_at'),
            s3_buckets=data.get('s3_buckets'),
            s3_credentials=data.get('s3_credentials'),
            tensorboard_params=_optional_string_mapping(data.get('tensorboard_params'), 'tensorboard_params'),
        )


@dataclass(frozen=True)
class TensorboardCreateInvocation:
    """Namespace и тело запроса create: из YAML-манифеста или из опций CLI."""

    namespace: str
    create: TensorboardCreatePayload

    def api_body(self) -> dict[str, Any]:
        """Словарь JSON для ``TensorboardApi.create_tensorboard``."""
        return self.create.to_api_dict()

    @classmethod
    def resolve(
        cls,
        *,
        config_path: str | None,
        **cli: Any,
    ) -> 'TensorboardCreateInvocation':
        """Собирает вызов create: при ``config_path`` читает манифест, иначе — CLI."""
        if config_path:
            return cls._from_manifest_file(config_path, fallback_region=cli.get('region'), **cli)
        return cls._from_cli_options(**cli)

    @classmethod
    def _from_manifest_file(
        cls,
        file_path: str,
        fallback_region: str | None = None,
        **cli: Any,
    ) -> 'TensorboardCreateInvocation':
        raw = read_yaml(file_path)
        if not isinstance(raw, dict):
            raise ValueError('YAML-манифест create должен быть объектом в корне')

        namespace = cli.get('namespace') if 'namespace' in _explicit_cli_names(CREATE_CLI_PARAM_NAMES) else raw.get('namespace')
        body = raw.get(CREATE_MANIFEST_BODY_KEY)
        if not namespace or not isinstance(namespace, str):
            raise ValueError('В манифесте задайте строковый ключ namespace')
        if not isinstance(body, dict):
            raise ValueError(f'В манифесте задайте объект {CREATE_MANIFEST_BODY_KEY}')
        return cls(namespace, TensorboardCreatePayload.from_api_mapping(_merge_create_cli_overrides(body, cli), fallback_region))

    @classmethod
    def _from_cli_options(cls, **cli: Any) -> 'TensorboardCreateInvocation':
        values: dict[str, Any] = {key: cli.get(key) for key in CREATE_CLI_REQUIRED_PARAM_NAMES}
        missing = [CREATE_CLI_FLAGS[key] for key in CREATE_CLI_REQUIRED_PARAM_NAMES if not values[key]]
        if missing:
            joined = ', '.join(missing)
            raise ValueError(
                f'Отсутствуют обязательные опции: {joined}. Либо передайте --config с манифестом.',
            )

        namespace = cli['namespace']
        payload = TensorboardCreatePayload(
            name=cli['name'],
            image=TensorboardImagePayload(
                name=cli['image_name'],
                tag=cli['image_tag'],
                type=cli['image_type'],
            ),
            instance_type=cli['instance_type'],
            logdir=list(cli['logdir']),
            region=resolve_region(cli.get('region'), None),
            postponed_pause_enabled=cli['postponed_pause_enabled'],
            allocation_name=cli.get('allocation_name'),
            queue_name=cli.get('queue_name'),
            description=cli.get('description'),
            pause_at=cli.get('pause_at'),
            s3_buckets=cli.get('s3_buckets_json'),
            s3_credentials=cli.get('s3_credentials_json'),
            tensorboard_params=cli.get('tensorboard_params'),
        )
        return cls(namespace, payload)


@dataclass(frozen=True)
class TensorboardResumePayload:
    """Тело запроса resume TensorBoard."""

    region: str
    instance_type: str

    def to_api_dict(self) -> dict[str, str]:
        """Собирает словарь для `TensorboardApi.resume_tensorboard`."""
        return {'region': self.region, 'instance_type': self.instance_type}

    @classmethod
    def from_api_mapping(cls, data: dict[str, Any], region: str | None = None) -> 'TensorboardResumePayload':
        """Собирает payload из словаря в форме тела Public API."""
        allowed = {'region', 'instance_type'}
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise ValueError(f'Недопустимые поля TensorBoard resume: {", ".join(unknown)}')
        try:
            return cls(
                region=resolve_region(data.get('region'), region),
                instance_type=data['instance_type'],
            )
        except KeyError as exc:
            missing = exc.args[0]
            raise ValueError(f'В секции resume не хватает обязательного поля: {missing}') from exc


@dataclass(frozen=True)
class TensorboardResumeInvocation:
    """Namespace и тело запроса resume: из YAML-манифеста или из опций CLI."""

    namespace: str
    resume: TensorboardResumePayload

    @classmethod
    def resolve(
        cls,
        *,
        config_path: str | None,
        **cli: Any,
    ) -> 'TensorboardResumeInvocation':
        """Собирает вызов resume: при ``config_path`` читает манифест, иначе — CLI."""
        if config_path:
            return cls._from_manifest_file(config_path, fallback_region=cli.get('region'), **cli)
        return cls._from_cli_options(**cli)

    @classmethod
    def _from_manifest_file(
        cls,
        file_path: str,
        fallback_region: str | None = None,
        **cli: Any,
    ) -> 'TensorboardResumeInvocation':
        raw = read_yaml(file_path)
        if not isinstance(raw, dict):
            raise ValueError('YAML-манифест resume должен быть объектом в корне')

        namespace = cli.get('namespace') if 'namespace' in _explicit_cli_names(RESUME_CLI_PARAM_NAMES) else raw.get('namespace')
        if not namespace or not isinstance(namespace, str):
            raise ValueError('В манифесте задайте строковый ключ namespace')

        body = raw.get(RESUME_MANIFEST_BODY_KEY)
        if not isinstance(body, dict):
            raise ValueError(f'В манифесте задайте объект {RESUME_MANIFEST_BODY_KEY}')
        return cls(namespace, TensorboardResumePayload.from_api_mapping(_merge_resume_cli_overrides(body, cli), fallback_region))

    @classmethod
    def _from_cli_options(cls, **cli: Any) -> 'TensorboardResumeInvocation':
        namespace = cli.get('namespace')
        values: dict[str, str | None] = {key: cli.get(key) for key in RESUME_CLI_REQUIRED_PARAM_NAMES}
        missing = [RESUME_CLI_FLAGS[key] for key in RESUME_CLI_REQUIRED_PARAM_NAMES if not values[key]]
        if missing:
            joined = ', '.join(missing)
            raise ValueError(
                f'Отсутствуют обязательные опции: {joined}. Либо передайте --config с манифестом.',
            )
        assert namespace is not None
        return cls(
            namespace=namespace,
            resume=TensorboardResumePayload(
                region=resolve_region(cli.get('region'), None),
                instance_type=cli['instance_type'],
            ),
        )


@dataclass(frozen=True)
class TensorboardModifyPayload:
    """Тело запроса modify TensorBoard: описание, S3."""

    shutdown_in: int | None = None
    timer_enabled: bool = True
    autoshutdown_config_json: dict[str, Any] | None = None
    description: str | None = None
    s3_buckets: list[Any] | None = None
    s3_credentials: dict[str, Any] | None = None

    @classmethod
    def resolve(
        cls,
        *,
        shutdown_in: int | None,
        timer_enabled: bool,
        autoshutdown_config_json: dict[str, Any] | None,
        description: str | None,
        s3_buckets: list[Any] | None,
        s3_credentials: dict[str, Any] | None,
    ) -> 'TensorboardModifyPayload':
        """Собирает payload modify из явно переданных CLI-опций."""
        return cls(
            shutdown_in=shutdown_in,
            timer_enabled=timer_enabled,
            autoshutdown_config_json=autoshutdown_config_json,
            description=description,
            s3_buckets=s3_buckets,
            s3_credentials=s3_credentials,
        )

    def to_api_dict(self) -> dict[str, Any]:
        """Собирает словарь для `TensorboardApi.modify_tensorboard`."""
        if self.autoshutdown_config_json is not None and self.shutdown_in is not None:
            raise ValueError('Нельзя одновременно задавать --autoshutdown-config-json и --shutdown-in')

        body: dict[str, Any] = {}
        if self.autoshutdown_config_json is not None:
            body['autoshutdown_config'] = self.autoshutdown_config_json
        elif self.shutdown_in is not None:
            body['autoshutdown_config'] = {
                'by_timer': {'shutdown_in': self.shutdown_in, 'is_enabled': self.timer_enabled},
            }
        if self.description:
            body['description'] = self.description
        if self.s3_buckets is not None:
            body['s3_buckets'] = self.s3_buckets
        if self.s3_credentials is not None:
            body['s3_credentials'] = self.s3_credentials
        if not body:
            raise ValueError(
                'Укажите хотя бы одно изменение: --shutdown-in, --autoshutdown-config-json, '
                '--description, --s3-buckets-json или --s3-credentials-json',
            )
        return body
