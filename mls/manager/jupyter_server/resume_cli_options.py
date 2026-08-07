"""Единая спецификация опций ``mls js resume``: Click-декораторы и списки для ``--config``."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import click

from .constants import JS_REGION_HELP
from .custom_types import ManifestOptions
from .custom_types import RequiredOptions
from .custom_types import ResumeOptions
from mls.utils.common_types import Path


@dataclass(frozen=True, slots=True)
class JsResumeOptionSpec:
    """Описание одной опции команды ``js resume`` (кроме глобальных клиентских опций)."""

    param_name: str
    option_decls: tuple[str, ...]
    default: Any
    help: str
    role: str
    required_cli: bool = False
    click_type: Any | None = None
    callback: Callable[..., Any] | None = None
    option_cls: type[click.Option] | None = None
    index: int = 0


def _js_resume_option_specs() -> tuple[JsResumeOptionSpec, ...]:
    """Порядок как в справке: ``--config`` … ``--instance-type``."""
    return (
        JsResumeOptionSpec(
            param_name='config',
            option_decls=('-c', '--config'),
            default=None,
            role='config',
            help=(
                'Путь к YAML-манифесту с описанием Jupyter Server'
            ),
            click_type=Path(exists=True),
            option_cls=ManifestOptions,
        ),
        JsResumeOptionSpec(
            param_name='namespace',
            option_decls=('--namespace',),
            default=None,
            role='namespace',
            required_cli=True,
            help='Namespace воркспейса, в котором будет запущен Jupyter Server. Не используется с --config',
            option_cls=RequiredOptions,
            index=0,
        ),
        JsResumeOptionSpec(
            param_name='region',
            option_decls=('-R', '--region'),
            default=None,
            role='payload',
            help=JS_REGION_HELP,
            option_cls=ResumeOptions,
            index=0,
        ),
        JsResumeOptionSpec(
            param_name='instance_type',
            option_decls=('--instance-type',),
            default=None,
            role='payload',
            required_cli=True,
            help='Конфигурация ресурсов',
            option_cls=ResumeOptions,
            index=1,
        ),
    )


JS_RESUME_OPTION_SPECS: tuple[JsResumeOptionSpec, ...] = _js_resume_option_specs()

RESUME_CLI_PARAM_NAMES: tuple[str, ...] = tuple(s.param_name for s in JS_RESUME_OPTION_SPECS if s.role != 'config')

RESUME_CLI_REQUIRED_PARAM_NAMES: tuple[str, ...] = tuple(s.param_name for s in JS_RESUME_OPTION_SPECS if s.required_cli)


def _primary_flag(decls: tuple[str, ...]) -> str:
    for d in decls:
        if d.startswith('--') and '/' not in d:
            return d
    for d in decls:
        if d.startswith('--'):
            return d
    return decls[0]


def _resume_cli_flags() -> dict[str, str]:
    out: dict[str, str] = {}
    for spec in JS_RESUME_OPTION_SPECS:
        if spec.role == 'config':
            continue
        out[spec.param_name] = _primary_flag(spec.option_decls)
    return out


RESUME_CLI_FLAGS: dict[str, str] = _resume_cli_flags()


def apply_js_resume_click_options() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Вешает все ``@click.option`` для ``js resume`` в порядке, эквивалентном ручным декораторам."""

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        wrapped = f
        for spec in reversed(JS_RESUME_OPTION_SPECS):
            kw: dict[str, Any] = {'default': spec.default, 'help': spec.help}
            if spec.click_type is not None:
                kw['type'] = spec.click_type
            if spec.callback is not None:
                kw['callback'] = spec.callback
            if spec.option_cls is not None:
                kw['cls'] = spec.option_cls
                kw['index'] = spec.index
            wrapped = click.option(*spec.option_decls, **kw)(wrapped)
        return wrapped

    return decorator


__all__ = (
    'JS_RESUME_OPTION_SPECS',
    'RESUME_CLI_FLAGS',
    'RESUME_CLI_PARAM_NAMES',
    'RESUME_CLI_REQUIRED_PARAM_NAMES',
    'apply_js_resume_click_options',
)
