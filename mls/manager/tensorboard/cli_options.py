"""Общие инструменты для Click-опций команд ``mls tensorboard``."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click

from .constants import TENSORBOARD_INSTANCE_TYPE_HELP
from .constants import TENSORBOARD_REGION_HELP
from mls.manager.notebook_service.cli_options import apply_click_options
from mls.manager.notebook_service.cli_options import build_cli_flags
from mls.manager.notebook_service.cli_options import config_option
from mls.manager.notebook_service.cli_options import instance_type_option
from mls.manager.notebook_service.cli_options import namespace_option
from mls.manager.notebook_service.cli_options import NotebookServiceOptionSpec
from mls.manager.notebook_service.cli_options import region_option

TensorboardOptionSpec = NotebookServiceOptionSpec


def tensorboard_config_option(
    help_text: str,
    option_cls: type[click.Option],
) -> TensorboardOptionSpec:
    """Возвращает спецификацию ``--config`` для TensorBoard-команды."""
    return config_option(help_text, option_cls)


def tensorboard_namespace_option(
    help_text: str,
    option_cls: type[click.Option],
) -> TensorboardOptionSpec:
    """Возвращает спецификацию ``--namespace`` для TensorBoard-команды."""
    return namespace_option(help_text, option_cls)


def tensorboard_region_option(
    option_cls: type[click.Option],
) -> TensorboardOptionSpec:
    """Возвращает спецификацию ``--region`` для TensorBoard-команды."""
    return region_option(TENSORBOARD_REGION_HELP, option_cls)


def tensorboard_instance_type_option(
    option_cls: type[click.Option],
    index: int,
) -> TensorboardOptionSpec:
    """Возвращает спецификацию ``--instance-type`` для TensorBoard-команды."""
    return instance_type_option(TENSORBOARD_INSTANCE_TYPE_HELP, option_cls, index)


def build_tensorboard_cli_flags(
    specs: tuple[TensorboardOptionSpec, ...],
    custom_flags: dict[str, str] | None = None,
) -> dict[str, str]:
    """Собирает человекочитаемые CLI-флаги для сообщений о валидации."""
    return build_cli_flags(specs, custom_flags)


def apply_tensorboard_click_options(
    specs: tuple[TensorboardOptionSpec, ...],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Вешает ``@click.option`` по переданным спецификациям."""
    return apply_click_options(specs)


__all__ = (
    'TensorboardOptionSpec',
    'apply_tensorboard_click_options',
    'build_tensorboard_cli_flags',
    'tensorboard_config_option',
    'tensorboard_instance_type_option',
    'tensorboard_namespace_option',
    'tensorboard_region_option',
)
