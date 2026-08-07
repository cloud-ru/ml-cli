"""Единая спецификация опций ``mls tensorboard resume``."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .cli_options import apply_tensorboard_click_options
from .cli_options import build_tensorboard_cli_flags
from .cli_options import tensorboard_config_option
from .cli_options import tensorboard_instance_type_option
from .cli_options import tensorboard_namespace_option
from .cli_options import tensorboard_region_option
from .cli_options import TensorboardOptionSpec
from .custom_types import ManifestOptions
from .custom_types import RequiredOptions
from .custom_types import ResumeOptions


def _tensorboard_resume_option_specs() -> tuple[TensorboardOptionSpec, ...]:
    """Порядок как в справке: ``--config`` … ``--instance-type``."""
    return (
        tensorboard_config_option(
            'Путь к YAML-манифесту с описанием TensorBoard',
            ManifestOptions,
        ),
        tensorboard_namespace_option(
            'Namespace воркспейса, в котором будет запущен инстанс TensorBoard. Не используется с --config',
            RequiredOptions,
        ),
        tensorboard_region_option(ResumeOptions),
        tensorboard_instance_type_option(ResumeOptions, 1),
    )


TENSORBOARD_RESUME_OPTION_SPECS: tuple[TensorboardOptionSpec, ...] = (
    _tensorboard_resume_option_specs()
)
RESUME_CLI_PARAM_NAMES: tuple[str, ...] = tuple(
    s.param_name for s in TENSORBOARD_RESUME_OPTION_SPECS if s.role != 'config'
)
RESUME_CLI_REQUIRED_PARAM_NAMES: tuple[str, ...] = tuple(
    s.param_name for s in TENSORBOARD_RESUME_OPTION_SPECS if s.required_cli
)


RESUME_CLI_FLAGS: dict[str, str] = build_tensorboard_cli_flags(
    TENSORBOARD_RESUME_OPTION_SPECS,
)


def apply_tensorboard_resume_click_options() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Вешает все ``@click.option`` для ``tensorboard resume``."""
    return apply_tensorboard_click_options(TENSORBOARD_RESUME_OPTION_SPECS)


__all__ = (
    'RESUME_CLI_FLAGS',
    'RESUME_CLI_PARAM_NAMES',
    'RESUME_CLI_REQUIRED_PARAM_NAMES',
    'TENSORBOARD_RESUME_OPTION_SPECS',
    'apply_tensorboard_resume_click_options',
)
