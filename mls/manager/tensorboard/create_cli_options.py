"""Единая спецификация опций ``mls tensorboard create``."""
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
from .constants import TENSORBOARD_IMAGE_TYPE_CHOICE
from .custom_types import CreateOptions
from .custom_types import ManifestOptions
from .custom_types import RequiredOptions
from mls.manager.notebook_service.cli import click_parse_optional_string_mapping_json_object
from mls.manager.notebook_service.cli_options import create_payload_options
from mls.manager.notebook_service.cli_options import image_name_option
from mls.manager.notebook_service.cli_options import image_tag_option
from mls.manager.notebook_service.cli_options import image_type_option
from mls.manager.notebook_service.cli_options import name_option


def _tensorboard_create_option_specs() -> tuple[TensorboardOptionSpec, ...]:
    """Порядок как в справке сверху вниз: ``--config`` … ``--tensorboard-params``."""
    return (
        tensorboard_config_option(
            'Путь к YAML-манифесту с описанием инстанса TensorBoard',
            ManifestOptions,
        ),
        tensorboard_namespace_option(
            'Namespace воркспейса, в котором будет запущен инстанс TensorBoard',
            RequiredOptions,
        ),
        name_option(
            help_text='Название инстанса TensorBoard',
            option_cls=RequiredOptions,
        ),
        image_name_option(RequiredOptions),
        image_tag_option(RequiredOptions),
        image_type_option(
            help_text='Тип образа, например `datahub` или `custom`',
            image_type_choice=TENSORBOARD_IMAGE_TYPE_CHOICE,
            option_cls=RequiredOptions,
        ),
        tensorboard_instance_type_option(RequiredOptions, 5),
        tensorboard_region_option(CreateOptions),
        *create_payload_options('Описание инстанса TensorBoard', CreateOptions),
        TensorboardOptionSpec(
            param_name='logdir',
            option_decls=('--logdir',),
            default=(),
            role='payload',
            required_cli=True,
            help='Директория с event logs для визуализации в TensorBoard',
            multiple=True,
            option_cls=RequiredOptions,
            index=6,
        ),
        TensorboardOptionSpec(
            param_name='tensorboard_params',
            option_decls=('--tensorboard-params',),
            default=None,
            role='payload',
            help='Параметры запуска TensorBoard',
            callback=click_parse_optional_string_mapping_json_object('tensorboard_params'),
            option_cls=CreateOptions,
            index=8,
        ),
    )


TENSORBOARD_CREATE_OPTION_SPECS: tuple[TensorboardOptionSpec, ...] = _tensorboard_create_option_specs()

CREATE_CLI_PARAM_NAMES: tuple[str, ...] = tuple(
    s.param_name for s in TENSORBOARD_CREATE_OPTION_SPECS if s.role != 'config'
)
CREATE_CLI_REQUIRED_PARAM_NAMES: tuple[str, ...] = tuple(
    s.param_name for s in TENSORBOARD_CREATE_OPTION_SPECS if s.required_cli
)


CREATE_CLI_FLAGS: dict[str, str] = build_tensorboard_cli_flags(
    TENSORBOARD_CREATE_OPTION_SPECS,
    {'postponed_pause_enabled': '--postponed-pause-enabled / --no-postponed-pause-enabled'},
)


def apply_tensorboard_create_click_options() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Вешает все ``@click.option`` для ``tensorboard create``."""
    return apply_tensorboard_click_options(TENSORBOARD_CREATE_OPTION_SPECS)


__all__ = (
    'CREATE_CLI_FLAGS',
    'CREATE_CLI_PARAM_NAMES',
    'CREATE_CLI_REQUIRED_PARAM_NAMES',
    'TENSORBOARD_CREATE_OPTION_SPECS',
    'apply_tensorboard_create_click_options',
)
