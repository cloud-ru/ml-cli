"""Dataclasses для тел запросов API Jupyter Server, собираемых из параметров CLI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import click
from click.core import ParameterSource

from ..utils import read_yaml
from .constants import CREATE_ALLOWED_FIELDS
from .constants import CREATE_MANIFEST_BODY_KEY
from .constants import CREATE_REQUIRED_FIELDS
from .constants import RESUME_ALLOWED_FIELDS
from .constants import RESUME_MANIFEST_BODY_KEY
from .create_cli_options import CREATE_CLI_FLAGS
from .create_cli_options import CREATE_CLI_PARAM_NAMES
from .create_cli_options import CREATE_CLI_REQUIRED_PARAM_NAMES
from .resume_cli_options import RESUME_CLI_FLAGS
from .resume_cli_options import RESUME_CLI_PARAM_NAMES
from .resume_cli_options import RESUME_CLI_REQUIRED_PARAM_NAMES
from mls.manager.notebook_service.cli import resolve_region


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


def _missing_create_fields(payload: dict[str, Any]) -> list[str]:
    """Возвращает список обязательных create-полей, которых нет в payload."""
    image = payload.get('image') or {}
    checks = {
        'name': payload.get('name'),
        'image.name': image.get('name'),
        'image.tag': image.get('tag'),
        'image.type': image.get('type'),
        'instance_type': payload.get('instance_type'),
    }
    return [field for field in CREATE_REQUIRED_FIELDS if not checks[field]]


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
    ):
        if cli_name in explicit:
            merged[api_name] = cli.get(cli_name)
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


@dataclass(frozen=True)
class JupyterServerImagePayload:
    """Фрагмент тела запроса: конфигурация образа (image)."""

    name: str
    tag: str
    type: str

    def to_api_fragment(self) -> dict[str, str]:
        """Возвращает объект image для JSON тела запроса."""
        return {'name': self.name, 'tag': self.tag, 'type': self.type}


@dataclass(frozen=True)
class JupyterServerCreatePayload:
    """Тело запроса создания Jupyter Server."""

    name: str
    image: JupyterServerImagePayload
    instance_type: str
    region: str
    postponed_pause_enabled: bool = False
    allocation_name: str | None = None
    queue_name: str | None = None
    description: str | None = None
    pause_at: str | None = None
    s3_buckets: list[Any] | None = None
    s3_credentials: dict[str, Any] | None = None

    def to_api_dict(self) -> dict[str, Any]:
        """Собирает словарь для `JupyterServerApi.create_jupyter_server`."""
        body: dict[str, Any] = {
            'name': self.name,
            'image': self.image.to_api_fragment(),
            'instance_type': self.instance_type,
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
        return body

    @classmethod
    def from_api_mapping(cls, data: dict[str, Any], region: str | None = None) -> 'JupyterServerCreatePayload':
        """Собирает payload из словаря в форме тела Public API (как в YAML `jupyter_server`).

        Args:
            data: Ключи совпадают с JSON телом create после парсинга YAML.

        Returns:
            Экземпляр `JupyterServerCreatePayload`.

        Raises:
            ValueError: Если не хватает обязательных полей или структура image неверна.
        """
        unknown = sorted(set(data) - set(CREATE_ALLOWED_FIELDS))
        if unknown:
            raise ValueError(f'Недопустимые поля Jupyter Server create: {", ".join(unknown)}')
        missing = _missing_create_fields(data)
        if missing:
            joined = ', '.join(missing)
            raise ValueError(f'В секции {CREATE_MANIFEST_BODY_KEY} не хватает обязательных полей: {joined}')
        img = data['image']
        return cls(
            name=data['name'],
            image=JupyterServerImagePayload(
                name=img['name'],
                tag=img['tag'],
                type=img['type'],
            ),
            instance_type=data['instance_type'],
            region=resolve_region(data.get('region'), region),
            postponed_pause_enabled=bool(data.get('postponed_pause_enabled', False)),
            allocation_name=data.get('allocation_name'),
            queue_name=data.get('queue_name'),
            description=data.get('description'),
            pause_at=data.get('pause_at'),
            s3_buckets=data.get('s3_buckets'),
            s3_credentials=data.get('s3_credentials'),
        )


@dataclass(frozen=True)
class JupyterServerCreateInvocation:
    """Namespace и тело запроса create: из YAML-манифеста или из опций CLI."""

    namespace: str
    create: JupyterServerCreatePayload

    def api_body(self) -> dict[str, Any]:
        """Словарь JSON для ``JupyterServerApi.create_jupyter_server``."""
        return self.create.to_api_dict()

    @classmethod
    def resolve(
        cls,
        *,
        config_path: str | None,
        **cli: Any,
    ) -> JupyterServerCreateInvocation:
        """Собирает вызов create: при ``config_path`` читает манифест, иначе — опции CLI.

        Args:
            config_path: Путь к YAML или None.
            **cli: Имена и значения опций как у Click (см. ``JS_CREATE_OPTION_SPECS``).

        Raises:
            ValueError: Некорректный манифест, неполные обязательные опции CLI или неверное тело ``jupyter_server``.
        """
        if config_path:
            return cls._from_manifest_file(config_path, fallback_region=cli.get('region'), **cli)
        return cls._from_cli_options(**cli)

    @classmethod
    def _from_manifest_file(
        cls,
        file_path: str,
        fallback_region: str | None = None,
        **cli: Any,
    ) -> JupyterServerCreateInvocation:
        raw = read_yaml(file_path)
        if not isinstance(raw, dict):
            raise ValueError('YAML-манифест create должен быть объектом в корне')
        ns = cli.get('namespace') if 'namespace' in _explicit_cli_names(CREATE_CLI_PARAM_NAMES) else raw.get('namespace')
        body = raw.get(CREATE_MANIFEST_BODY_KEY)
        if not ns or not isinstance(ns, str):
            raise ValueError('В манифесте задайте строковый ключ namespace')
        if not isinstance(body, dict):
            raise ValueError(f'В манифесте задайте объект {CREATE_MANIFEST_BODY_KEY}')
        return cls(ns, JupyterServerCreatePayload.from_api_mapping(_merge_create_cli_overrides(body, cli), fallback_region))

    @classmethod
    def _from_cli_options(cls, **cli: Any) -> JupyterServerCreateInvocation:
        namespace = cli.get('namespace')
        values: dict[str, str | None] = {key: cli.get(key) for key in CREATE_CLI_REQUIRED_PARAM_NAMES}
        missing = [CREATE_CLI_FLAGS[key] for key in CREATE_CLI_REQUIRED_PARAM_NAMES if not values[key]]
        if missing:
            joined = ', '.join(missing)
            raise ValueError(
                f'Отсутствуют обязательные опции: {joined}. Либо передайте --config с манифестом.',
            )
        assert namespace is not None
        name = cli['name']
        image_name = cli['image_name']
        image_tag = cli['image_tag']
        image_type = cli['image_type']
        instance_type = cli['instance_type']
        region = resolve_region(cli.get('region'), None)
        postponed_pause_enabled = cli['postponed_pause_enabled']
        allocation_name = cli.get('allocation_name')
        queue_name = cli.get('queue_name')
        description = cli.get('description')
        pause_at = cli.get('pause_at')
        s3_buckets = cli.get('s3_buckets_json')
        s3_credentials = cli.get('s3_credentials_json')
        payload = JupyterServerCreatePayload(
            name=name,
            image=JupyterServerImagePayload(name=image_name, tag=image_tag, type=image_type),
            instance_type=instance_type,
            region=region,
            postponed_pause_enabled=postponed_pause_enabled,
            allocation_name=allocation_name,
            queue_name=queue_name,
            description=description,
            pause_at=pause_at,
            s3_buckets=s3_buckets,
            s3_credentials=s3_credentials,
        )
        return cls(namespace, payload)


@dataclass(frozen=True)
class JupyterServerModifyPayload:
    """Тело запроса modify Jupyter Server: autoshutdown, описание, S3."""

    shutdown_in: int | None = None
    timer_enabled: bool = True
    autoshutdown_config_json: dict[str, Any] | None = None
    description: str | None = None
    s3_buckets: list[Any] | None = None
    s3_credentials: dict[str, Any] | None = None

    def to_api_dict(self) -> dict[str, Any]:
        """Собирает словарь для `JupyterServerApi.modify_jupyter_server`."""
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


@dataclass(frozen=True)
class JupyterServerResumePayload:
    """Тело запроса resume Jupyter Server."""

    region: str
    instance_type: str

    def to_api_dict(self) -> dict[str, Any]:
        """Собирает словарь для `JupyterServerApi.resume_jupyter_server`."""
        return {'region': self.region, 'instance_type': self.instance_type}

    @classmethod
    def from_api_mapping(cls, data: dict[str, Any], region: str | None = None) -> 'JupyterServerResumePayload':
        """Собирает payload из словаря в форме тела Public API (как в YAML ``resume``).

        Args:
            data: Ключи совпадают с JSON телом resume после парсинга YAML.

        Returns:
            Экземпляр `JupyterServerResumePayload`.

        Raises:
            ValueError: Если не хватает обязательных полей.
        """
        unknown = sorted(set(data) - set(RESUME_ALLOWED_FIELDS))
        if unknown:
            raise ValueError(f'Недопустимые поля Jupyter Server resume: {", ".join(unknown)}')
        try:
            return cls(
                region=resolve_region(data.get('region'), region),
                instance_type=data['instance_type'],
            )
        except KeyError as exc:
            missing = exc.args[0]
            raise ValueError(f'В секции resume не хватает обязательного поля: {missing}') from exc


@dataclass(frozen=True)
class JupyterServerResumeInvocation:
    """Namespace и тело запроса resume: из YAML-манифеста или из опций CLI."""

    namespace: str
    resume: JupyterServerResumePayload

    @classmethod
    def resolve(
        cls,
        *,
        config_path: str | None,
        **cli: Any,
    ) -> 'JupyterServerResumeInvocation':
        """Собирает вызов resume: при ``config_path`` читает манифест, иначе — опции CLI.

        Args:
            config_path: Путь к YAML или None.
            **cli: Имена и значения опций как у Click (см. ``JS_RESUME_OPTION_SPECS``).

        Raises:
            ValueError: Некорректный манифест, неполные обязательные опции CLI или неверное тело ``resume``.
        """
        if config_path:
            return cls._from_manifest_file(config_path, fallback_region=cli.get('region'), **cli)
        return cls._from_cli_options(**cli)

    @classmethod
    def _from_manifest_file(
        cls,
        file_path: str,
        fallback_region: str | None = None,
        **cli: Any,
    ) -> 'JupyterServerResumeInvocation':
        raw = read_yaml(file_path)
        if not isinstance(raw, dict):
            raise ValueError('YAML-манифест resume должен быть объектом в корне')
        ns = cli.get('namespace') if 'namespace' in _explicit_cli_names(RESUME_CLI_PARAM_NAMES) else raw.get('namespace')
        body = raw.get(RESUME_MANIFEST_BODY_KEY)
        if not ns or not isinstance(ns, str):
            raise ValueError('В манифесте задайте строковый ключ namespace')
        if not isinstance(body, dict):
            raise ValueError(f'В манифесте задайте объект {RESUME_MANIFEST_BODY_KEY}')
        return cls(ns, JupyterServerResumePayload.from_api_mapping(_merge_resume_cli_overrides(body, cli), fallback_region))

    @classmethod
    def _from_cli_options(cls, **cli: Any) -> 'JupyterServerResumeInvocation':
        namespace = cli.get('namespace')
        values: dict[str, str | None] = {key: cli.get(key) for key in RESUME_CLI_REQUIRED_PARAM_NAMES}
        missing = [RESUME_CLI_FLAGS[key] for key in RESUME_CLI_REQUIRED_PARAM_NAMES if not values[key]]
        if missing:
            joined = ', '.join(missing)
            raise ValueError(
                f'Отсутствуют обязательные опции: {joined}. Либо передайте --config с манифестом.',
            )
        assert namespace is not None
        region = resolve_region(cli.get('region'), None)
        instance_type = cli['instance_type']
        payload = JupyterServerResumePayload(region=region, instance_type=instance_type)
        return cls(namespace, payload)


@dataclass(frozen=True)
class WorkspaceAutoshutdownSetPayload:
    """Тело запроса set workspace autoshutdown: by_timer, by_load, by_schedule."""

    by_timer: dict[str, Any] | None = None
    by_load: dict[str, Any] | None = None
    by_schedule: dict[str, Any] | None = None

    def to_api_dict(self) -> dict[str, Any]:
        """Собирает словарь для `JupyterServerApi.set_workspace_autoshutdown_rule`."""
        body: dict[str, Any] = {}
        if self.by_timer is not None:
            body['by_timer'] = self.by_timer
        if self.by_load is not None:
            body['by_load'] = self.by_load
        if self.by_schedule is not None:
            body['by_schedule'] = self.by_schedule
        if not body:
            raise ValueError(
                'Укажите хотя бы одно правило: --by-timer-json, --by-load-json, --by-schedule-json '
                'или --shutdown-in',
            )
        return body
