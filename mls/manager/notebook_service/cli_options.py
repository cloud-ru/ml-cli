"""Shared Click option specs for notebook-style services."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import click

from .cli import click_parse_optional_json_array
from .cli import click_parse_optional_json_object
from mls.utils.common_types import Path


@dataclass(frozen=True, slots=True)
class NotebookServiceOptionSpec:
    """Описание одной Click-опции notebook-style команды."""

    param_name: str
    option_decls: tuple[str, ...]
    default: Any
    help: str
    role: str
    required_cli: bool = False
    click_type: Any | None = None
    callback: Callable[..., Any] | None = None
    multiple: bool = False
    option_cls: type[click.Option] | None = None
    index: int = 0


def config_option(
    help_text: str,
    option_cls: type[click.Option],
) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--config``."""
    return NotebookServiceOptionSpec(
        param_name='config',
        option_decls=('-c', '--config'),
        default=None,
        role='config',
        help=help_text,
        click_type=Path(exists=True),
        option_cls=option_cls,
    )


def namespace_option(
    help_text: str,
    option_cls: type[click.Option],
) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--namespace``."""
    return NotebookServiceOptionSpec(
        param_name='namespace',
        option_decls=('--namespace',),
        default=None,
        role='namespace',
        required_cli=True,
        help=help_text,
        option_cls=option_cls,
        index=0,
    )


def name_option(
    help_text: str,
    option_cls: type[click.Option],
) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--name``."""
    return NotebookServiceOptionSpec(
        param_name='name',
        option_decls=('--name',),
        default=None,
        role='payload',
        required_cli=True,
        help=help_text,
        option_cls=option_cls,
        index=1,
    )


def image_name_option(option_cls: type[click.Option]) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--image-name``."""
    return NotebookServiceOptionSpec(
        param_name='image_name',
        option_decls=('--image-name',),
        default=None,
        role='payload',
        required_cli=True,
        help='Название образа',
        option_cls=option_cls,
        index=2,
    )


def image_tag_option(option_cls: type[click.Option]) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--image-tag``."""
    return NotebookServiceOptionSpec(
        param_name='image_tag',
        option_decls=('--image-tag',),
        default=None,
        role='payload',
        required_cli=True,
        help='Тег образа',
        option_cls=option_cls,
        index=3,
    )


def image_type_option(
    help_text: str,
    image_type_choice: Any,
    option_cls: type[click.Option],
) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--image-type``."""
    return NotebookServiceOptionSpec(
        param_name='image_type',
        option_decls=('--image-type',),
        default=None,
        role='payload',
        required_cli=True,
        help=help_text,
        click_type=image_type_choice,
        option_cls=option_cls,
        index=4,
    )


def instance_type_option(
    help_text: str,
    option_cls: type[click.Option],
    index: int,
) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--instance-type``."""
    return NotebookServiceOptionSpec(
        param_name='instance_type',
        option_decls=('--instance-type',),
        default=None,
        role='payload',
        required_cli=True,
        help=help_text,
        option_cls=option_cls,
        index=index,
    )


def region_option(
    help_text: str,
    option_cls: type[click.Option],
) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--region``."""
    return NotebookServiceOptionSpec(
        param_name='region',
        option_decls=('-R', '--region'),
        default=None,
        role='payload',
        help=help_text,
        option_cls=option_cls,
        index=0,
    )


def allocation_name_option(option_cls: type[click.Option]) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--allocation-name``."""
    return NotebookServiceOptionSpec(
        param_name='allocation_name',
        option_decls=('--allocation-name',),
        default=None,
        role='payload',
        help='Название аллокации',
        option_cls=option_cls,
        index=1,
    )


def queue_name_option(option_cls: type[click.Option]) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--queue-name``."""
    return NotebookServiceOptionSpec(
        param_name='queue_name',
        option_decls=('--queue-name',),
        default=None,
        role='payload',
        help='Название очереди',
        option_cls=option_cls,
        index=2,
    )


def description_option(
    help_text: str,
    option_cls: type[click.Option],
) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--description``."""
    return NotebookServiceOptionSpec(
        param_name='description',
        option_decls=('--description',),
        default=None,
        role='payload',
        help=help_text,
        option_cls=option_cls,
        index=3,
    )


def pause_at_option(option_cls: type[click.Option]) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--pause-at``."""
    return NotebookServiceOptionSpec(
        param_name='pause_at',
        option_decls=('--pause-at',),
        default=None,
        role='payload',
        help='CRON-расписание для автоматической остановки сервера',
        option_cls=option_cls,
        index=4,
    )


def postponed_pause_enabled_option(
    option_cls: type[click.Option],
) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--postponed-pause-enabled``."""
    return NotebookServiceOptionSpec(
        param_name='postponed_pause_enabled',
        option_decls=('--postponed-pause-enabled/--no-postponed-pause-enabled',),
        default=False,
        role='payload',
        help='Включение или отключение отложенной автоматической остановки сервера',
        option_cls=option_cls,
        index=5,
    )


def s3_buckets_json_option(option_cls: type[click.Option]) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--s3-buckets-json``."""
    return NotebookServiceOptionSpec(
        param_name='s3_buckets_json',
        option_decls=('--s3-buckets-json',),
        default=None,
        role='payload',
        help='JSON-массив настроек S3 хранилищ. Например: [{"bucket_name":"b","access_rule":"ro"}]',
        callback=click_parse_optional_json_array,
        option_cls=option_cls,
        index=6,
    )


def s3_credentials_json_option(
    option_cls: type[click.Option],
) -> NotebookServiceOptionSpec:
    """Возвращает спецификацию ``--s3-credentials-json``."""
    return NotebookServiceOptionSpec(
        param_name='s3_credentials_json',
        option_decls=('--s3-credentials-json',),
        default=None,
        role='payload',
        help='JSON-объект настроек авторизации S3. По умолчанию на стороне API not-enabled',
        callback=click_parse_optional_json_object,
        option_cls=option_cls,
        index=7,
    )


def create_payload_options(
    description_help: str,
    option_cls: type[click.Option],
) -> tuple[NotebookServiceOptionSpec, ...]:
    """Возвращает общий набор optional payload-опций create-команд."""
    return (
        allocation_name_option(option_cls),
        queue_name_option(option_cls),
        description_option(description_help, option_cls),
        pause_at_option(option_cls),
        postponed_pause_enabled_option(option_cls),
        s3_buckets_json_option(option_cls),
        s3_credentials_json_option(option_cls),
    )


def build_cli_flags(
    specs: tuple[NotebookServiceOptionSpec, ...],
    custom_flags: dict[str, str] | None = None,
) -> dict[str, str]:
    """Собирает человекочитаемые CLI-флаги для сообщений о валидации."""
    out: dict[str, str] = {}
    for spec in specs:
        if spec.role == 'config':
            continue
        if custom_flags and spec.param_name in custom_flags:
            out[spec.param_name] = custom_flags[spec.param_name]
            continue
        out[spec.param_name] = _primary_flag(spec.option_decls)
    return out


def apply_click_options(
    specs: tuple[NotebookServiceOptionSpec, ...],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Вешает ``@click.option`` по переданным спецификациям."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        wrapped = func
        for spec in reversed(specs):
            kw: dict[str, Any] = {'default': spec.default, 'help': spec.help}
            if spec.click_type is not None:
                kw['type'] = spec.click_type
            if spec.callback is not None:
                kw['callback'] = spec.callback
            if spec.multiple:
                kw['multiple'] = True
            if spec.option_cls is not None:
                kw['cls'] = spec.option_cls
                kw['index'] = spec.index
            wrapped = click.option(*spec.option_decls, **kw)(wrapped)
        return wrapped

    return decorator


def _primary_flag(decls: tuple[str, ...]) -> str:
    for decl in decls:
        if decl.startswith('--') and '/' not in decl:
            return decl
    for decl in decls:
        if decl.startswith('--'):
            return decl
    return decls[0]
